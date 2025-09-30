from __future__ import annotations
import argparse
from NhacNhac import Jogo

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prof", type=int, default=4, help="Profundidade máxima da IA") # a padrao é 4, mas pode mudar no terminal ali pra testes 
    parser.add_argument("--tempo", type=float, default=30.0, help="Limite de tempo por jogada em segundos") #  a padrao é 30 seg, mas pode mudar no terminal ali pra testes
    args = parser.parse_args()

    jogo = Jogo(profundidade_ia=args.prof, limite_tempo_ia=args.tempo)
    jogo.executar()

if __name__ == "__main__":
    main()