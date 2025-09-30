from __future__ import annotations
import time
from typing import Optional

from Tabuleiro import Tabuleiro, Jogador, Tamanho, Peca, Pos
from IA import IA_Minimax 

def _parse_pos(txt: str) -> Optional[Pos]:
    try:
        txt = txt.strip()
        if "," not in txt:
            return None
        l, c = txt.split(",", 1)
        l_int = int(l.strip())
        c_int = int(c.strip())
        if 0 <= l_int <= 2 and 0 <= c_int <= 2:
            return Pos(l_int, c_int)
        return None
    except Exception:
        return None

def _escolher_tamanho() -> Optional[Tamanho]:
    op = input("Escolha o tamanho da peça (1=pequena, 2=média, 3=grande) ou 'q' para voltar: ").strip().lower()
    if op == "q":
        return None
    if op == "1":
        return Tamanho.P
    if op == "2":
        return Tamanho.M
    if op == "3":
        return Tamanho.G
    print("Opção inválida.")
    return None


class Jogo:
    def __init__(self, profundidade_ia: int = 4, limite_tempo_ia: float = 30.0):
        self.tab = Tabuleiro()
        self.jogador_humano = Jogador.JOGADOR
        self.jogador_ia = Jogador.IA
        self.jogador_atual = self.jogador_humano  # default
        self.ia = IA_Minimax(profundidade_maxima=profundidade_ia, limite_tempo=limite_tempo_ia)

    def configurar_inicio(self):
        print(" NHAC NHAC ")
        print("Quem começa?")
        print("1. Você (Humano)")
        print("2. IA")
        esc = input("Digite 1 ou 2: ").strip()
        while esc not in ("1", "2"):
            esc = input("Opção inválida. Digite 1 para começar o jogador ou 2 para a IA: ").strip()
        if esc == "2":
            self.jogador_atual = self.jogador_ia
        else:
            self.jogador_atual = self.jogador_humano
        print(f"\n-> Começa: {'Você' if self.jogador_atual == self.jogador_humano else 'IA'}\n")


    def _turno_humano(self):
        self.tab.imprimir_tabuleiro()
        print("\nSua vez. Estoque (você):", self.tab.stock[self.jogador_humano])
        print("\nEstoque (IA):", self.tab.stock[self.jogador_ia]) # coloquei pra testar só, na hora do jogo pode tirar pra ficar desafiador e real


        while True:
            print("\nAção:")
            print("1. Colocar peça do estoque (place)")
            print("2. Mover peça no tabuleiro (slide)")
            print("q. Desistir/sair")
            ac = input("Escolha: ").strip().lower()

            if ac == "q":
                print("Você saiu do jogo.")
                exit(0)

            if ac == "1":
                tam = _escolher_tamanho()
                if tam is None:
                    continue
                pos_txt = input("Posição destino (linha,coluna) [ex: 1,2] ou 'q' para voltar: ").strip().lower()
                if pos_txt == "q":
                    continue
                pos = _parse_pos(pos_txt)
                if not pos:
                    print("Posição inválida.")
                    continue

                peca = Peca(self.jogador_humano, tam)
                try:
                    self.tab.place(self.jogador_humano, peca, pos)
                    print(f"Você colocou ({peca}) em {pos}.")
                    break
                except ValueError as e:
                    print("Movimento inválido:", e)
                    continue

            elif ac == "2":
                org_txt = input("Origem (linha,coluna) [ex: 0,0] ou 'q' para voltar: ").strip().lower()
                if org_txt == "q":
                    continue
                org = _parse_pos(org_txt)
                if not org:
                    print("Origem inválida.")
                    continue

                dst_txt = input("Destino (linha,coluna) [ex: 2,2] ou 'q' para voltar: ").strip().lower()
                if dst_txt == "q":
                    continue
                dst = _parse_pos(dst_txt)
                if not dst:
                    print("Destino inválido.")
                    continue

                try:
                    self.tab.slide(org, dst)
                    print(f"Você moveu de {org} para {dst}.")
                    break
                except ValueError as e:
                    print("Movimento inválido:", e)
                    continue

            else:
                print("Opção inválida.")


    def _turno_ia(self):
        print("\nIA pensando...")
        t0 = time.time()
        mv = self.ia.obter_melhor_movimento(self.tab, self.jogador_ia)
        if mv is None:
            print("IA não encontrou movimentos (isso não deveria acontecer se o jogo não tem empates).")
            return

        # aplica o movimento e mostra
        if mv.tipo == "place":
            self.tab.aplicar_movimento(self.jogador_ia, mv)
            print(f"IA colocou ({Peca(self.jogador_ia, mv.size)}) em {mv.dst}.")
        else:  # slide
            self.tab.aplicar_movimento(self.jogador_ia, mv)
            print(f"IA moveu de {mv.org} para {mv.dst}.")
        print(f"IA decidiu em {time.time() - t0:.2f}s.")
        self.tab.imprimir_tabuleiro()


    def executar(self):
        self.configurar_inicio()

        while not self.tab.acabou():
            if self.jogador_atual == self.jogador_humano:
                self._turno_humano()
                if self.tab.acabou():
                    break
                self.jogador_atual = self.jogador_ia
            else:
                self._turno_ia()
                if self.tab.acabou():
                    break
                self.jogador_atual = self.jogador_humano

        vencedor = self.tab.ganhador()
        print("\n=== FIM DE JOGO ===")
        self.tab.imprimir_tabuleiro()
        if vencedor == self.jogador_humano:
            print("Parabéns, você venceu!")
        elif vencedor == self.jogador_ia:
            print("A IA venceu!")
        else:
            print("Jogo encerrado.")


if __name__ == "__main__":
    jogo = Jogo(profundidade_ia=4, limite_tempo_ia=30.0)  # troque se quiser
    jogo.executar()