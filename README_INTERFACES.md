# 🎯 Nhac Nhac - Interfaces Gráficas

Este projeto agora possui três formas de jogar:

## 1. Interface de Terminal (Original)

```bash
python3 Main.py
# ou
python3 Main.py --prof 6 --tempo 45
```

## 2. Interface Web Simples (Recomendada) ⭐

```bash
python3 InterfaceWebSimples.py
```

Depois abra seu navegador em: `http://localhost:8000`

**Recursos:**

- ✅ Interface visual moderna e responsiva
- ✅ Tabuleiro interativo com cliques
- ✅ Controles para colocar e mover peças
- ✅ Configuração de profundidade e tempo da IA
- ✅ Mostra estoque de peças em tempo real
- ✅ Feedback visual do estado do jogo
- ✅ Não requer instalação de bibliotecas extras

## 3. Interface Tkinter (Requer tkinter)

```bash
python3 InterfaceGrafica.py
```

_Nota: Requer que o tkinter esteja instalado no sistema_

## Como Jogar

### Regras do Jogo

- Tabuleiro 3x3 como jogo da velha
- Cada jogador tem 6 peças: 2 pequenas (●), 2 médias (⬤), 2 grandes (⚫)
- Peças maiores podem ser colocadas sobre peças menores
- Ganha quem alinhar 3 peças visíveis (no topo das pilhas)

### Ações Disponíveis

1. **Colocar Peça**: Selecione o tamanho e clique em uma posição
2. **Mover Peça**: Selecione uma peça sua no tabuleiro, depois o destino

### Interface Web - Controles

- **Novo Jogo**: Configure quem começa e dificuldade da IA
- **Ação**: Escolha entre "Colocar Peça" ou "Mover Peça"
- **Tamanho**: Para colocar peças, selecione Pequena/Média/Grande
- **Tabuleiro**: Clique nas posições para jogar
- **Estoque**: Acompanhe suas peças restantes

### Configurações da IA

- **Profundidade**: 1-8 (padrão: 4) - maior = mais inteligente
- **Tempo Limite**: 5-120 segundos (padrão: 30)

## Características das Interfaces

| Característica    | Terminal | Web Simples | Tkinter             |
| ----------------- | -------- | ----------- | ------------------- |
| Facilidade de uso | ⭐⭐     | ⭐⭐⭐⭐⭐  | ⭐⭐⭐⭐            |
| Visual            | ⭐       | ⭐⭐⭐⭐⭐  | ⭐⭐⭐⭐            |
| Instalação        | ✅       | ✅          | ❌ (requer tkinter) |
| Multiplataforma   | ✅       | ✅          | ⚠️ (depende do SO)  |

## Tecnologias Utilizadas

- **Backend**: Python puro com classes originais do jogo
- **IA**: Algoritmo Minimax com poda alfa-beta
- **Interface Web**: HTML5, CSS3, JavaScript, HTTP Server nativo
- **Interface Desktop**: Tkinter (quando disponível)

## Arquitetura do Projeto

```
📁 T1-IA/
├── 🎮 Main.py              # Interface terminal original
├── 🧠 IA.py                # Algoritmo Minimax da IA
├── 🎯 Tabuleiro.py         # Lógica do jogo e regras
├── 🎪 NhacNhac.py          # Controle de fluxo do jogo
├── 🌐 InterfaceWebSimples.py    # Interface web (recomendada)
├── 🖥️ InterfaceGrafica.py       # Interface Tkinter
└── 📖 README.md            # Este arquivo
```

A interface web é **recomendada** por ser mais visual e não depender de bibliotecas externas!
