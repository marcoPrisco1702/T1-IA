# T1-IA

Trabalho 1 de IA PUCRS
Alunos: Felipe Ribeiro
Marco Prisco

As execuções detalhadas estão descritas no README_INTERFACE.
O jogo foi originalmente desenvolvido para rodar no terminal, mas a experiência de jogar por lá não era muito prática. Por isso, implementamos também uma interface gráfica, onde é possível configurar:
A profundidade da IA
O tempo máximo de cálculo da jogada
Quem começa a partida

(Se preferir, ainda é possível jogar pelo terminal, o passo a passo está explicado no README_INTERFACE).

Durante os testes, percebemos que maiores profundidades tornam a IA mais difícil. Ao colocarmos IAs de profundidades diferentes uma contra a outra, a de profundidade maior sempre levava vantagem.

Os valores padrão que utilizamos foram:
Profundidade: 4
Tempo máximo: 30 segundos

Esses parâmetros seguem o que o professor pediu. No entanto, se quiser deixar o jogo mais desafiador, pode configurar, por exemplo, profundidade 6 e se quiser,um tempo maior mas, a profundidade 6 dificilmente vai passar de 10 segundos pra efetuar a jogada.

OBS:Esses valores maiores de tempo a gente usou pra testar profundidades maiores que 6

Vale destacar que em profundidades maiores que 6 tivemos alguns problemas de execução, então optamos por não mantê-las disponíveis no jogo.