from __future__ import annotations
import math
from enum import IntEnum
from typing import List, Optional, Tuple, Dict, Iterable, NamedTuple
from dataclasses import dataclass


# enum pra representar os jogadores, jogador 1 sendo o humano e jogador 2 a IA sempre
class Jogador(IntEnum):
    JOGADOR = 1
    IA = 2

# enum pra representar o tamanho das pecas
class Tamanho(IntEnum):
    P = 1
    M = 2
    G = 3

class Pos(NamedTuple):
    linha: int
    coluna: int


# classe pra representar cada peca do jogo com seu respectivo jogador e tamanho.
# tamanho varia de 1 a 3, 1 sendo pequeno e 3 grande
# jogador varia de 1 a 2, sendo 1 sempre o humano e 2 sempre a IA
@dataclass(frozen=True)
class Peca:
    jogador: Jogador # de qual jogador é aquela peca
    tamanho: Tamanho

    def __str__(self) -> str:
        string = str(int(self.tamanho))          # 1: p , 2: m, 3: g
        return string + "*" if self.jogador == Jogador.IA else string # coloca um asteristico pra diferenciar se for IA

    @dataclass(frozen=True)
    class Move:
        tipo: str                 # place ou slide, place tu pega uma que nao esta no tabuleiro ainda e colcoa e slide so troca de lugar uma que ja ta
        size: Optional[Tamanho]   # usado só em place
        org: Optional[Pos]    # usado só em slide pra saber a origem daonde vem
        dst: Pos             # usado em place e slide pra saber o destino da peca   


ALL_POS: Tuple[Pos, ...] = tuple(Pos(r, c) for r in range(3) for c in range(3))
WIN_LINES: Tuple[Tuple[Pos, Pos, Pos], ...] = ( #linhas que causam uma vitoria pro jogador se preenchidas por ele
    
    # linhas vencedoras
    (Pos(0,0), Pos(0,1), Pos(0,2)),
    (Pos(1,0), Pos(1,1), Pos(1,2)),
    (Pos(2,0), Pos(2,1), Pos(2,2)),
    # colunas vencedoras
    (Pos(0,0), Pos(1,0), Pos(2,0)),
    (Pos(0,1), Pos(1,1), Pos(2,1)),
    (Pos(0,2), Pos(1,2), Pos(2,2)),
    # diagonais vencedoras
    (Pos(0,0), Pos(1,1), Pos(2,2)),
    (Pos(0,2), Pos(1,1), Pos(2,0)),
)

# uma matriz 3x3 tipo cubo, onde cada posicao pode ficar vazia ou ter até 3 pecas
class Tabuleiro:

    #Heuristica
    W_TWO_ALIGNED   = 50.0
    W_ONE_ALIGNED   = 10.0
    W_BLOCK_THREAT  = 50.0
    W_CENTER_BONUS  = 10.0
    WIN_SCORE       = 1000.0

    def __init__(self,):
        self.grid: List[List[List[Peca]]] = [[[] for _ in range(3)] for _ in range(3)] # matriz 3x3 onde cada posicao tem uma lista de pecas
        self.stock: Dict[Jogador, Dict[Tamanho, int]] = {
            Jogador.JOGADOR: {Tamanho.P: 2, Tamanho.M: 2, Tamanho.G: 2},
            Jogador.IA: {Tamanho.P: 2, Tamanho.M: 2, Tamanho.G: 2},
        }

    def top(self,pos: Pos) -> Optional[Peca]: # pode ser none se estiver vazio ou retorna a no topo
        pecas = self.grid[pos.linha][pos.coluna]
        return pecas[-1] if pecas else None

    def can_place (self, peca: Peca, pos: Pos) -> bool:
        top_peca = self.top(pos)
        if top_peca is None:
            return True # se estiver vazio pode colocar
        else: # se nao ve se a peca é maior que a que esta no topo
            return peca.tamanho > top_peca.tamanho
        
    def place (self, jogador: Jogador, peca: Peca, pos: Pos) -> None:
        if self.stock[jogador][peca.tamanho] <= 0:
            raise ValueError(f"Jogador {jogador} nao tem mais pecas do tamanho {peca.tamanho} restantes")
        if not self.can_place(peca, pos):
            raise ValueError(f"Nao pode colocar peca {peca} na posicao {pos}")
        self.grid[pos.linha][pos.coluna].append(peca)
        self.stock[jogador][peca.tamanho] -= 1

    def can_slide (self, org: Pos, dst:Pos) -> bool:
        if org == dst:
            return False
        if not self.grid[org.linha][org.coluna]: # se a origem estiver vazia
            return False
        top_peca = self.top(org)
        top_dst = self.top(dst)
        return top_dst is None or top_peca.tamanho > top_dst.tamanho # se o destino estiver vazio ou a peca da origem for maior que a do destino
    
    def slide (self, org: Pos, dst: Pos) -> None:
        if not self.can_slide(org, dst):
            raise ValueError(f"Nao pode deslizar de {org} para {dst}")
        peca = self.grid[org.linha][org.coluna].pop()
        self.grid[dst.linha][dst.coluna].append(peca)

    def aplicar_movimento(self, jogador: Jogador, mv: Peca.Move) -> None:
        if mv.tipo == "place":
            self.place(jogador, Peca(jogador, mv.size), mv.dst)
        else: #slide
            self.slide(mv.org, mv.dst)

    def clone(self) -> "Tabuleiro":
        nb = Tabuleiro()
        for r in range(3):
            for c in range(3):
                nb.grid[r][c] = list(self.grid[r][c])[:]  # copia a lista de pecas naquela posicao
        nb.stock = {j: dict(tamanhos) for j, tamanhos in self.stock.items()}  # copia o estoque
        return nb

    def visible_player(self, pos: Pos) -> Optional[Jogador]:
        top_peca = self.top(pos)
        return top_peca.jogador if top_peca else None
    
    def movimentos_possiveis(self, jogador: Jogador) -> List[Peca.Move]:
        moves: List[Peca.Move] = []
        # place
        for tamanho in Tamanho:
            if self.stock[jogador][tamanho] > 0:
                peca = Peca(jogador, tamanho)
                for pos in ALL_POS:
                    if self.can_place(peca, pos):
                        moves.append(Peca.Move("place", tamanho, None, pos))
        # slide
        for org in ALL_POS:
            if self.top(org) and self.top(org).jogador == jogador:
                for dst in ALL_POS:
                    if self.can_slide(org, dst):
                        moves.append(Peca.Move("slide", None, org, dst))
        return moves
    
    def ganhador(self) -> Optional[Jogador]:
        for line in WIN_LINES:
            players = [self.visible_player(pos) for pos in line]
            if players[0] is not None and all(p == players[0] for p in players):
                return players[0]
        return None
    
        
    
    def acabou(self) -> bool:
            return self.ganhador() is not None
        

    def imprimir_tabuleiro(self) -> None:
        print("\n TABULEIRO:")
        print("    0   1   2")
        for i in range(3):
            linha_str = f"{i} "
            for j in range(3):
                topo = self.top(Pos(i, j))
                if topo:
                    linha_str += f"({topo})"
                else:
                    linha_str += "(X)"
                if j < 2:
                    linha_str += "|"
            print(linha_str)
        print("\n LEGENDA (peças visíveis de cima):")
        print("Nenhuma: (X)")
        print("Jogador: (1)=pequena, (2)=média, (3)=grande")
        print("IA: (1*)=pequena, (2*)=média, (3*)=grande")  
