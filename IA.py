import math
import time
from typing import Optional
from Tabuleiro import Tabuleiro, Jogador, Peca, Pos, Tamanho, WIN_LINES

class IA_Minimax:

    def __init__(self, profundidade_maxima: int = 4, limite_tempo: float = 30):
        self.profundidade_maxima = profundidade_maxima
        self.limite_tempo = limite_tempo  # segundos, o padrao de maximo de profundidade é 4 e tempo 30 seg, mas da pra aumentar pra testar mais
        self.nos_avaliados = 0
        self._t0 = 0.0 # pro controle do tempo

    def _oponente(self, j: Jogador) -> Jogador: # só pra mudar o jogador mais facil, jogador_atual = self._oponente(jogador_atual) dai troca
        return Jogador.IA if j == Jogador.JOGADOR else Jogador.JOGADOR

    def _checar_tempo(self):
        if self.limite_tempo is not None and (time.time() - self._t0) >= self.limite_tempo:
            raise TimeoutError

    # avalia a heuristica
    def _avaliar(self, tab: Tabuleiro, max_player: Jogador) -> float:
        vencedor = tab.ganhador()
        if vencedor == max_player:
            return tab.WIN_SCORE
        if vencedor is not None:
            return -tab.WIN_SCORE

        score = 0.0
        for linha in WIN_LINES:
            tops = [tab.top(pos) for pos in linha]
            donos = [p.jogador if p else None for p in tops]
            c_max = sum(1 for d in donos if d == max_player)
            c_min = sum(1 for d in donos if (d is not None and d != max_player))

            if   c_max == 2 and c_min == 0: score += tab.W_TWO_ALIGNED
            elif c_max == 1 and c_min == 0: score += tab.W_ONE_ALIGNED
            elif c_min == 2 and c_max == 0: score -= tab.W_BLOCK_THREAT
            elif c_min == 1 and c_max == 0: score -= tab.W_ONE_ALIGNED

        centro = tab.top(Pos(1, 1))
        if centro and centro.jogador == max_player:
            score += tab.W_CENTER_BONUS

        return score

    def obter_melhor_movimento(self, tabuleiro: Tabuleiro, jogador: Jogador) -> Optional[Peca.Move]:
        self.nos_avaliados = 0
        self._t0 = time.time()
        inicio = self._t0

        movimentos = tabuleiro.movimentos_possiveis(jogador)
        if not movimentos:
            return None

       # ordenacao simples pra ajudar na poda depois
        def chave(mv: Peca.Move) -> int:
            pri = 0
            if mv.dst == Pos(1, 1): pri += 3
            if mv.tipo == "place":
                pri += 2
                pri += (mv.size or Tamanho.P)  # P<M<G
            else:
                pri += 1
            return -pri
        movimentos.sort(key=chave)

        melhor_val = -math.inf
        melhor_mov: Optional[Peca.Move] = movimentos[0] # se der timeout, pelo menos joga o primeiro na ordenacao, failsafe

        try:
            val, move = self._minimax(
                tabuleiro,
                jogador_max=jogador,
                profundidade=self.profundidade_maxima,
                alfa=-math.inf,
                beta=math.inf,
                maximizando=True,
                jogador_atual=jogador
            )
            if move is not None: #só atualiza se achar algo melhor
                melhor_val, melhor_mov = val, move
        except TimeoutError:
            # se der timeout, retorna o melhor movimento encontrado até agora
            pass

        tempo_decorrido = time.time() - inicio
        print(f"Avaliados {self.nos_avaliados} nós em {tempo_decorrido:.2f}s (prof={self.profundidade_maxima})")
        return melhor_mov

    def _minimax(self,tab: Tabuleiro,jogador_max: Jogador,profundidade: int,alfa: float,beta: float,maximizando: bool,jogador_atual: Jogador) -> tuple[float, Optional[Peca.Move]]:
        self._checar_tempo()
        self.nos_avaliados += 1

        vencedor = tab.ganhador()
        if vencedor is not None or profundidade == 0:
            return self._avaliar(tab, jogador_max), None

        movimentos = tab.movimentos_possiveis(jogador_atual)
        if not movimentos:
            return self._avaliar(tab, jogador_max), None

        # ordenacao pra melhorar a poda
        def chave(mv: Peca.Move) -> int:
            pri = 0
            if mv.dst == Pos(1, 1): pri += 3
            if mv.tipo == "place":
                pri += 2
                pri += (mv.size or Tamanho.P)
            else:
                pri += 1
            return -pri
        movimentos.sort(key=chave)

        melhor_mov: Optional[Peca.Move] = None

        if maximizando:
            melhor = -math.inf
            for mv in movimentos:
                self._checar_tempo()
                filho = tab.clone()
                filho.aplicar_movimento(jogador_atual, mv)
                val, _ = self._minimax(
                    filho, jogador_max, profundidade - 1, alfa, beta,
                    False, self._oponente(jogador_atual)
                )
                if val > melhor:
                    melhor = val
                    melhor_mov = mv
                alfa = max(alfa, melhor)
                if beta <= alfa:
                    break
            return melhor, melhor_mov
        else:
            pior = math.inf
            for mv in movimentos:
                self._checar_tempo()
                filho = tab.clone()
                filho.aplicar_movimento(jogador_atual, mv)
                val, _ = self._minimax(
                    filho, jogador_max, profundidade - 1, alfa, beta,
                    True, self._oponente(jogador_atual)
                )
                if val < pior:
                    pior = val
                    melhor_mov = mv
                beta = min(beta, pior)
                if beta <= alfa:
                    break
            return pior, melhor_mov