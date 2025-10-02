from __future__ import annotations
import argparse
from NhacNhac import Jogo

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prof", type=int, default=4, help="Profundidade máxima da IA (máximo: 6)") # a padrao é 4, mas pode mudar no terminal ali pra testes só na hora de colocar tem que ser tipo: --prof x --tempo x 
    parser.add_argument("--tempo", type=float, default=30.0, help="Limite de tempo por jogada em segundos") #  a padrao é 30 seg, mas pode mudar no terminal ali pra testes
    args = parser.parse_args()
    
    # Limitar profundidade máxima a 6
    profundidade = min(max(args.prof, 1), 6)
    if args.prof > 6:
        print(f"Aviso: Profundidade limitada a 6 (valor solicitado: {args.prof})")

    jogo = Jogo(profundidade_ia=profundidade, limite_tempo_ia=args.tempo)
    jogo.executar()

if __name__ == "__main__": # roda só se executar o main.py
    main()