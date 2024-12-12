import time
import chess
import random
from stockfish import Stockfish
import avalia_posicao_escolhe_melhor_jogada as simulador
import concurrent.futures

# Caminho do executável do Stockfish
stockfish_path = "/home/lucas/stockfish/stockfish"

def criar_populacao(tamanho=10):
    """Cria uma população de indivíduos com parâmetros aleatórios."""
    return [
        {
            "material": random.uniform(0.5, 1.5),
            "mobilidade": random.uniform(0.5, 1.5),
            "controle_centro": random.uniform(0.5, 1.5),
            "desenvolvimento": random.uniform(0.5, 1.5),
            "seguranca_rei": random.uniform(0.5, 1.5)
        }
        for _ in range(tamanho)
    ]

def avaliar_individuo(individuo, stockfish, fen):
    """Avalia uma posição para um indivíduo usando uma instância do Stockfish."""
    stockfish.set_fen_position(fen)
    evaluation = stockfish.get_evaluation()
    valor = evaluation["value"] if evaluation["type"] == "cp" else 10000
    return (valor * individuo["material"] + 
            valor * individuo["mobilidade"] + 
            valor * individuo["controle_centro"] + 
            valor * individuo["desenvolvimento"] + 
            valor * individuo["seguranca_rei"])

def jogar_populacao_vs_populacao(stockfish, populacao1, populacao2):
    """Simula uma partida entre duas populações e retorna o vencedor."""
    board = chess.Board()
    turno_populacao1 = True
    
    start_match = time.time()
    while not board.is_game_over():
        if turno_populacao1:
            individuo = random.choice(populacao1)
        else:
            individuo = random.choice(populacao2)
        
        move = simulador.melhor_jogada(board, stockfish, individuo)
        if move:
            board.push(move)
        
        turno_populacao1 = not turno_populacao1
    end_match = time.time()
    print(f"Time of 1 match = {start_match - end_match}")
    return 1 if board.result() == "1-0" else 2 if board.result() == "0-1" else 0

def simular_partidas(populacoes, i, j):
    """Função auxiliar para simular partidas entre duas populações."""
    stockfish = Stockfish(stockfish_path)  # Inicializa o Stockfish
    populacao1 = populacoes[i]
    populacao2 = populacoes[j]
    vencedor = jogar_populacao_vs_populacao(stockfish, populacao1, populacao2)
    return (i, j, vencedor)

def encontrar_melhor_populacao(populacoes, jogos_por_populacao=3):
    """Encontra a melhor população entre uma lista de populações e identifica o melhor indivíduo dentro dela."""
    resultados = {i: 0 for i in range(len(populacoes))}
    combinacoes = [(i, j) for i in range(len(populacoes)) for j in range(i+1, len(populacoes))]
    
    executor = concurrent.futures.ProcessPoolExecutor()
    futures = {executor.submit(simular_partidas, populacoes, i, j): (i, j) for i, j in combinacoes}
    
    try:
        for future in concurrent.futures.as_completed(futures):
            i, j, vencedor = future.result()
            if vencedor == 1:
                resultados[i] += 1
            elif vencedor == 2:
                resultados[j] += 1
    finally:
        executor.shutdown()
    
    # Identificar a melhor população com base nos resultados
    melhor_populacao_index = max(resultados, key=resultados.get)
    melhor_populacao = populacoes[melhor_populacao_index]
    
    # Identificar o melhor indivíduo dentro da melhor população
    stockfish = Stockfish(stockfish_path)
    melhor_individuo = max(
        melhor_populacao,
        key=lambda individuo: avaliar_individuo(individuo, stockfish, chess.STARTING_FEN)
    )
    
    return melhor_populacao, melhor_individuo


def jogar_contra_melhor_individuo(melhor_individuo):
    """Permite ao usuário jogar contra o melhor indivíduo encontrado."""
    board = chess.Board()
    
    print("Você joga com as peças brancas. Boa sorte!")
    stockfish = Stockfish(stockfish_path)
    while not board.is_game_over():
        print(board)
        user_move = input("Digite seu movimento: ")
        
        try:
            board.push_san(user_move)
        except ValueError:
            print("Movimento inválido! Tente novamente.")
            continue
        
        # Movimento do melhor indivíduo
        move = simulador.melhor_jogada(board, stockfish, melhor_individuo)
        if move:
            board.push(move)
            print(f"Indivíduo jogou: {move}")
        
    print("Resultado final:", board.result())


# Etapas principais
# Reduzindo para 20 populações para acelerar
populacoes = [criar_populacao() for _ in range(20)]

# Encontrar a melhor população e o melhor indivíduo
melhor_populacao, melhor_individuo = encontrar_melhor_populacao(populacoes)

# Jogar contra o melhor indivíduo da melhor população
jogar_contra_melhor_individuo(melhor_individuo)

