import math
import time

# classe pra representar cada peca do jogo com seu respectivo jogador e tamanho.
# tamanho varia de 1 a 3, 1 sendo pequeno e 3 grande
# jogador varia de 1 a 2, sendo 1 sempre o humano e 2 sempre a IA
class Peca:
    def __init__(self, jogador, tamanho):
        self.jogador = jogador
        self.tamanho = tamanho

    def eh_maior_que(self, outra_peca):
        return self.tamanho > outra_peca.tamanho
    
    def __str__(self):
        simbolo = str(self.tamanho)  # mostra os tamanhos 1: pequeno, 2: medio, 3: grande
        if self.jogador == 2:        # se for IA
            return simbolo + "*"    # coloca um asteristico pra diferenciar
        return simbolo
    
    