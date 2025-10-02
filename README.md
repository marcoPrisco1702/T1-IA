# T1-IA

Trabalho 1 de IA PUCRS, plano de execucao do trabalho feito por IA, só pra termos uma base:
Plano de Trabalho – Nhac Nhac

1. Entender o problema
   • Jogo: variação do jogo da velha (3x3), mas com peças de diferentes tamanhos (2 grandes, 2 médias, 2 pequenas por jogador).
   • Ações possíveis:

   1. Colocar peça em casa vazia.
   2. Colocar peça sobre outra menor (sua ou do adversário).
   3. Mover peça que está no tabuleiro para casa vazia ou com peça menor.
      • Vitória: alinhar 3 peças visíveis (como no jogo da velha clássico).

2. Requisitos mínimos do programa
   • Permitir jogo IA x humano.
   • Usuário escolhe quem começa.
   • IA deve decidir jogada em no máximo 30s.
   • Estratégia de busca: Minimax ou Monte Carlo Tree Search (MCTS).
   • Deve haver função heurística para avaliar estados intermediários.
   • Não precisa ter interface gráfica (mas pode ser opcional).

3. Estrutura de dados e modelagem
   • Tabuleiro: matriz 3x3, mas cada célula pode ser uma pilha (stack) de peças.
   • Peça: identificada por jogador + tamanho.
   • Jogador: humano ou IA, com estoque de peças restantes.
   • Movimentos possíveis: função que gera todos os estados válidos a partir do estado atual.

4. Algoritmo de decisão da IA
   • Escolher entre:
   • Minimax com poda alfa-beta: limitar profundidade da árvore de busca e usar heurística.
   • MCTS: simular jogadas aleatórias até limite de tempo, escolher movimento mais promissor.
   • Definir heurística:
   • Pontuar número de linhas/parciais controladas.
   • Valor maior para alinhamentos com peças grandes.
   • Penalizar se adversário está prestes a ganhar.

5. Controle do tempo (≤30s)
   • Implementar timer que interrompe a busca e retorna a melhor jogada encontrada até então.
   • No Minimax → limitar profundidade (máximo: 6 níveis).
   • No MCTS → número máximo de simulações até estourar o tempo.

6. Fluxo do programa

   1. Início: escolher modo (humano x IA).
   2. Loop de turnos:
      • Mostrar tabuleiro.
      • Se for humano: ler entrada (posição + peça/movimento).
      • Se for IA: chamar algoritmo de busca e aplicar jogada.
      • Verificar condição de vitória ou empate.
   3. Fim: exibir vencedor.

7. Testes
   • Criar casos de teste:
   • Vitória direta em linha.
   • Cobrir peça do adversário.
   • Movimentar peça já no tabuleiro.
   • Situações de empate.
   • Validar se IA joga de forma coerente (não faz jogadas inválidas, reage a ameaças).

8. Apresentação (vídeo até 5 min)
   • Explicar:
   • Como o jogo funciona.
   • Estrutura de dados adotada.
   • Estratégia da IA (Minimax ou MCTS).
   • Demonstração rápida de execução.
   • Dica: preparar slides curtos e mostrar o programa rodando.

9. Entregáveis
   • Código (com comentários claros, indicar se teve ajuda de IA).
   • README explicando regras, como executar e como jogar.
   • Vídeo de até 5 minutos explicando estratégia.
