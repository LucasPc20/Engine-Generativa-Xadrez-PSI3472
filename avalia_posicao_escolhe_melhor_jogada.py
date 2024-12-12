import chess
import chess.engine
import random
from stockfish import Stockfish

# Inicializar o Stockfish (ou outro motor de xadrez para avaliação)
stockfish_path = "/home/lucas/stockfish/stockfish"  # Ajuste o caminho conforme necessário
stockfish = Stockfish(stockfish_path)


def avaliar_posicao(stockfish, fen, parametros):
    """
    Avalia uma posição no tabuleiro usando parâmetros de um indivíduo.
    A função utiliza o Stockfish para auxiliar na avaliação.
    
    Args:
    - stockfish: instância do motor Stockfish.
    - fen (str): FEN da posição atual.
    - parametros (dict): Parâmetros de avaliação do indivíduo.
    
    Returns:
    - float: avaliação da posição em centipawns.
    """
    stockfish.set_fen_position(fen)
    evaluation = stockfish.get_evaluation()
    valor = evaluation['value'] if evaluation['type'] == 'cp' else 10000  # Usando 10000 para mate
    # Aplicar pesos dos parâmetros (ajustar essa lógica conforme os parâmetros). Essa lógica aqui não está boa.
    return valor * parametros["material"] + valor * parametros["mobilidade"] + valor * parametros["controle_centro"] + valor * parametros["desenvolvimento"] + valor * parametros["seguranca_rei"]

def melhor_jogada(board, stockfish, individuo):
    """
    Calcula a melhor jogada para um indivíduo baseado na avaliação do tabuleiro.
    
    Args:
    - board: tabuleiro de xadrez (chess.Board).
    - stockfish: instância do motor Stockfish.
    - individuo: dicionário com os parâmetros de avaliação do indivíduo.
    
    Returns:
    - A melhor jogada (chess.Move).
    """
    best_move = None
    best_value = -float('inf')
    
    for move in board.legal_moves:
        board.push(move)
        fen = board.fen()
        score = avaliar_posicao(stockfish, fen, individuo) # A função avaliar_posicao não está boa
        if score > best_value:
            best_value = score
            best_move = move
        board.pop()
    
    return best_move


"""
# Exemplo de populações
populacao1 = [
    {"material": 1.0, "mobilidade": 0.5, "controle_centro": 0.8, "desenvolvimento": 0.3, "seguranca_rei": 0.7},
    # Outros indivíduos com diferentes parâmetros
]

populacao2 = [
    {"material": 0.9, "mobilidade": 0.6, "controle_centro": 0.7, "desenvolvimento": 0.4, "seguranca_rei": 0.8},
    # Outros indivíduos com diferentes parâmetros
]

# Executa uma partida entre as duas populações
resultado = jogar_partida(populacao1, populacao2, stockfish)
print("Resultado da partida:", resultado)
"""