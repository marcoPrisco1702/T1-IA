import http.server
import socketserver
import webbrowser
import json
import urllib.parse
from typing import Optional, Dict, Any
import threading
import time

from Tabuleiro import Tabuleiro, Jogador, Tamanho, Peca, Pos
from IA import IA_Minimax


class JogoWeb:
    def __init__(self):
        self.tabuleiro = Tabuleiro()
        self.jogador_humano = Jogador.JOGADOR
        self.jogador_ia = Jogador.IA
        self.jogador_atual = self.jogador_humano
        # Limitar profundidade máxima inicial a 6
        self.ia = IA_Minimax(profundidade_maxima=4, limite_tempo=30.0)
        self.jogo_ativo = False
        self.posicao_origem = None
        self.mensagem_status = "Clique em 'Novo Jogo' para começar"
        
    def novo_jogo(self, quem_comeca: str = "jogador", profundidade: int = 4, tempo_limite: float = 30.0):
        # Limitar profundidade máxima a 6
        profundidade = min(max(profundidade, 1), 6)
        
        self.tabuleiro = Tabuleiro()
        self.jogador_atual = self.jogador_ia if quem_comeca == "ia" else self.jogador_humano
        self.ia = IA_Minimax(profundidade_maxima=profundidade, limite_tempo=tempo_limite)
        self.jogo_ativo = True
        self.posicao_origem = None
        self.mensagem_status = "Sua vez!" if self.jogador_atual == self.jogador_humano else "IA está pensando..."
        
    def obter_estado(self) -> Dict[str, Any]:
        grid = []
        for i in range(3):
            linha = []
            for j in range(3):
                pos = Pos(i, j)
                top_peca = self.tabuleiro.top(pos)
                if top_peca:
                    linha.append({
                        'jogador': int(top_peca.jogador),
                        'tamanho': int(top_peca.tamanho),
                        'texto': self._obter_simbolo_peca(top_peca)
                    })
                else:
                    linha.append(None)
            grid.append(linha)
            
        return {
            'grid': grid,
            'jogador_atual': int(self.jogador_atual),
            'jogo_ativo': self.jogo_ativo,
            'estoque_jogador': {int(k): v for k, v in self.tabuleiro.stock[self.jogador_humano].items()},
            'estoque_ia': {int(k): v for k, v in self.tabuleiro.stock[self.jogador_ia].items()},
            'vencedor': int(self.tabuleiro.ganhador()) if self.tabuleiro.ganhador() else None,
            'posicao_origem': [self.posicao_origem.linha, self.posicao_origem.coluna] if self.posicao_origem else None,
            'mensagem_status': self.mensagem_status
        }
        
    def _obter_simbolo_peca(self, peca: Peca) -> str:
        if peca.jogador == self.jogador_humano:
            return {Tamanho.P: "●", Tamanho.M: "⬤", Tamanho.G: "⚫"}[peca.tamanho]
        else:
            return {Tamanho.P: "○", Tamanho.M: "◯", Tamanho.G: "⭕"}[peca.tamanho]
        
    def fazer_movimento_humano(self, acao: str, linha: int, coluna: int, tamanho: Optional[int] = None):
        if not self.jogo_ativo or self.jogador_atual != self.jogador_humano:
            return {'sucesso': False, 'erro': 'Não é sua vez!'}
            
        pos = Pos(linha, coluna)
        
        try:
            if acao == "place":
                if tamanho is None:
                    return {'sucesso': False, 'erro': 'Tamanho da peça não especificado!'}
                peca = Peca(self.jogador_humano, Tamanho(tamanho))
                self.tabuleiro.place(self.jogador_humano, peca, pos)
                self.posicao_origem = None
                
            elif acao == "selecionar_origem":
                top_peca = self.tabuleiro.top(pos)
                if not top_peca or top_peca.jogador != self.jogador_humano:
                    return {'sucesso': False, 'erro': 'Selecione uma posição com sua peça no topo!'}
                self.posicao_origem = pos
                self.mensagem_status = "Agora selecione o destino"
                return {'sucesso': True, 'movimento_incompleto': True}
                
            elif acao == "slide":
                if not self.posicao_origem:
                    return {'sucesso': False, 'erro': 'Selecione uma peça origem primeiro!'}
                self.tabuleiro.slide(self.posicao_origem, pos)
                self.posicao_origem = None
                
            # Verificar fim de jogo
            if self.tabuleiro.acabou():
                self.jogo_ativo = False
                vencedor = self.tabuleiro.ganhador()
                if vencedor == self.jogador_humano:
                    self.mensagem_status = "🎉 Você venceu!"
                elif vencedor == self.jogador_ia:
                    self.mensagem_status = "😅 A IA venceu!"
                return {'sucesso': True, 'fim_jogo': True}
                
            # Passar vez para IA
            self.jogador_atual = self.jogador_ia
            self.mensagem_status = "IA está pensando..."
            return {'sucesso': True, 'vez_ia': True}
            
        except ValueError as e:
            return {'sucesso': False, 'erro': str(e)}
            
    def fazer_movimento_ia(self):
        if not self.jogo_ativo or self.jogador_atual != self.jogador_ia:
            return {'sucesso': False, 'erro': 'Não é vez da IA!'}
            
        try:
            movimento = self.ia.obter_melhor_movimento(self.tabuleiro, self.jogador_ia)
            if movimento:
                self.tabuleiro.aplicar_movimento(self.jogador_ia, movimento)
                
            # Verificar fim de jogo
            if self.tabuleiro.acabou():
                self.jogo_ativo = False
                vencedor = self.tabuleiro.ganhador()
                if vencedor == self.jogador_humano:
                    self.mensagem_status = "🎉 Você venceu!"
                elif vencedor == self.jogador_ia:
                    self.mensagem_status = "😅 A IA venceu!"
                return {'sucesso': True, 'fim_jogo': True}
                
            # Passar vez para jogador
            self.jogador_atual = self.jogador_humano
            self.mensagem_status = "Sua vez!"
            return {'sucesso': True}
            
        except Exception as e:
            return {'sucesso': False, 'erro': f'Erro na IA: {str(e)}'}


class GameHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, jogo_instance=None, **kwargs):
        self.jogo = jogo_instance
        super().__init__(*args, **kwargs)
        
    def do_GET(self):
        if self.path == '/':
            self.serve_game_page()
        elif self.path == '/api/estado':
            self.serve_json(self.jogo.obter_estado())
        else:
            super().do_GET()
            
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        if self.path == '/api/novo_jogo':
            data = json.loads(post_data.decode('utf-8'))
            self.jogo.novo_jogo(
                data.get('quem_comeca', 'jogador'),
                data.get('profundidade', 4),
                data.get('tempo_limite', 30.0)
            )
            self.serve_json({'sucesso': True})
            
        elif self.path == '/api/movimento':
            data = json.loads(post_data.decode('utf-8'))
            resultado = self.jogo.fazer_movimento_humano(
                data.get('acao'),
                data.get('linha'),
                data.get('coluna'),
                data.get('tamanho')
            )
            self.serve_json(resultado)
            
        elif self.path == '/api/movimento_ia':
            resultado = self.jogo.fazer_movimento_ia()
            self.serve_json(resultado)
            
        elif self.path == '/api/cancelar_origem':
            self.jogo.posicao_origem = None
            self.jogo.mensagem_status = "Sua vez!"
            self.serve_json({'sucesso': True})
            
    def serve_json(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
        
    def serve_game_page(self):
        html = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎯 Nhac Nhac</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 20px;
            min-height: 100vh;
            color: white;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            text-align: center;
        }
        .titulo {
            font-size: 2.5em;
            margin-bottom: 20px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .controles {
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            backdrop-filter: blur(10px);
        }
        .tabuleiro {
            display: grid;
            grid-template-columns: repeat(3, 100px);
            grid-gap: 5px;
            justify-content: center;
            margin: 20px auto;
        }
        .casa {
            width: 100px;
            height: 100px;
            background: white;
            border: 2px solid #333;
            font-size: 2em;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            border-radius: 10px;
            transition: all 0.2s;
        }
        .casa:hover {
            transform: scale(1.05);
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        }
        .casa.origem {
            background: #f1c40f !important;
            box-shadow: 0 0 10px #f39c12;
        }
        .casa.jogador {
            background: #e74c3c;
            color: white;
        }
        .casa.ia {
            background: #3498db;
            color: white;
        }
        .botao {
            background: #2ecc71;
            color: white;
            border: none;
            padding: 10px 20px;
            margin: 5px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1em;
            transition: background 0.2s;
        }
        .botao:hover {
            background: #27ae60;
        }
        .botao:disabled {
            background: #95a5a6;
            cursor: not-allowed;
        }
        .status {
            font-size: 1.2em;
            margin: 20px 0;
            padding: 10px;
            background: rgba(0,0,0,0.2);
            border-radius: 5px;
        }
        .estoque {
            display: flex;
            justify-content: space-around;
            margin: 20px 0;
        }
        .estoque-item {
            background: rgba(255,255,255,0.1);
            padding: 10px;
            border-radius: 5px;
            backdrop-filter: blur(5px);
        }
        .acoes {
            margin: 10px 0;
        }
        .acoes label {
            margin: 0 10px;
        }
        .configuracao {
            background: rgba(0,0,0,0.3);
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="titulo">🎯 NHAC NHAC 🎯</h1>
        
        <div class="controles">
            <div class="configuracao">
                <h3>⚙️ Configurações</h3>
                <div>
                    <label>Quem começa:</label>
                    <input type="radio" name="quem_comeca" value="jogador" id="comeca_jogador" checked>
                    <label for="comeca_jogador">🧑 Você</label>
                    <input type="radio" name="quem_comeca" value="ia" id="comeca_ia">
                    <label for="comeca_ia">🤖 IA</label>
                </div>
                <div style="margin-top: 10px;">
                    <label>Profundidade IA:</label>
                    <input type="number" id="profundidade" value="4" min="1" max="6" style="width: 50px;">
                    <label style="margin-left: 20px;">Tempo limite (s):</label>
                    <input type="number" id="tempo_limite" value="30" min="5" max="120" style="width: 60px;">
                </div>
                <button class="botao" onclick="novoJogo()">🚀 Novo Jogo</button>
            </div>
            
            <div class="acoes">
                <h4>Sua Ação:</h4>
                <input type="radio" name="acao" value="place" id="acao_place" checked>
                <label for="acao_place">📍 Colocar Peça</label>
                <input type="radio" name="acao" value="slide" id="acao_slide">
                <label for="acao_slide">↔️ Mover Peça</label>
                
                <div id="tamanho_selecao" style="margin-top: 10px;">
                    <label>Tamanho:</label>
                    <input type="radio" name="tamanho" value="1" id="tamanho_p" checked>
                    <label for="tamanho_p">● Pequena</label>
                    <input type="radio" name="tamanho" value="2" id="tamanho_m">
                    <label for="tamanho_m">⬤ Média</label>
                    <input type="radio" name="tamanho" value="3" id="tamanho_g">
                    <label for="tamanho_g">⚫ Grande</label>
                </div>
                
                <div id="tamanho_ia_info" style="margin-top: 10px;">
                    <label>Peças da IA:</label>
                    <span style="margin-left: 10px;">○ Pequena</span>
                    <span style="margin-left: 20px;">◯ Média</span>
                    <span style="margin-left: 20px;">⭕ Grande</span>
                </div>

                <div id="slide_controles" style="display: none; margin-top: 10px;">
                    <button class="botao" onclick="cancelarOrigem()">❌ Cancelar Seleção</button>
                </div>
            </div>
        </div>
        
        <div class="status" id="status">Clique em 'Novo Jogo' para começar</div>
        
        <div class="tabuleiro" id="tabuleiro">
            <!-- Gerado dinamicamente -->
        </div>
        
        <div class="estoque">
            <div class="estoque-item">
                <h4>🧑 Suas Peças</h4>
                <div id="estoque_jogador">P:2 M:2 G:2</div>
            </div>
            <div class="estoque-item">
                <h4>🤖 Peças da IA</h4>
                <div id="estoque_ia">P:2 M:2 G:2</div>
            </div>
        </div>
    </div>

    <script>
        let estadoJogo = null;
        let aguardandoIA = false;

        // Configurar interface
        document.querySelectorAll('input[name="acao"]').forEach(radio => {
            radio.addEventListener('change', function() {
                const tamanhoDiv = document.getElementById('tamanho_selecao');
                const slideDiv = document.getElementById('slide_controles');
                if (this.value === 'place') {
                    tamanhoDiv.style.display = 'block';
                    slideDiv.style.display = 'none';
                } else {
                    tamanhoDiv.style.display = 'none';
                    slideDiv.style.display = 'block';
                }
            });
        });

        function novoJogo() {
            const quemComeca = document.querySelector('input[name="quem_comeca"]:checked').value;
            const profundidade = parseInt(document.getElementById('profundidade').value);
            const tempoLimite = parseFloat(document.getElementById('tempo_limite').value);
            
            fetch('/api/novo_jogo', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    quem_comeca: quemComeca,
                    profundidade: profundidade,
                    tempo_limite: tempoLimite
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.sucesso) {
                    atualizarInterface();
                    if (quemComeca === 'ia') {
                        setTimeout(movimentoIA, 1000);
                    }
                }
            });
        }

        function cliqueTabuleiro(linha, coluna) {
            if (!estadoJogo || !estadoJogo.jogo_ativo || aguardandoIA) return;
            if (estadoJogo.jogador_atual !== 1) return; // Não é vez do jogador
            
            const acao = document.querySelector('input[name="acao"]:checked').value;
            let tamanho = null;
            
            if (acao === 'place') {
                tamanho = parseInt(document.querySelector('input[name="tamanho"]:checked').value);
            }
            
            const requestData = {
                acao: acao === 'slide' && !estadoJogo.posicao_origem ? 'selecionar_origem' : acao,
                linha: linha,
                coluna: coluna,
                tamanho: tamanho
            };
            
            fetch('/api/movimento', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(requestData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.sucesso) {
                    atualizarInterface();
                    if (data.vez_ia && !data.fim_jogo) {
                        setTimeout(movimentoIA, 1000);
                    }
                } else {
                    alert(data.erro);
                }
            });
        }

        function movimentoIA() {
            if (!estadoJogo || !estadoJogo.jogo_ativo) return;
            
            aguardandoIA = true;
            fetch('/api/movimento_ia', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'}
            })
            .then(response => response.json())
            .then(data => {
                aguardandoIA = false;
                atualizarInterface();
            });
        }

        function cancelarOrigem() {
            fetch('/api/cancelar_origem', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'}
            })
            .then(response => response.json())
            .then(data => {
                if (data.sucesso) {
                    atualizarInterface();
                }
            });
        }

        function atualizarInterface() {
            fetch('/api/estado')
            .then(response => response.json())
            .then(data => {
                estadoJogo = data;
                atualizarTabuleiro();
                atualizarStatus();
                atualizarEstoque();
            });
        }

        function atualizarTabuleiro() {
            const tabuleiro = document.getElementById('tabuleiro');
            tabuleiro.innerHTML = '';
            
            for (let i = 0; i < 3; i++) {
                for (let j = 0; j < 3; j++) {
                    const casa = document.createElement('div');
                    casa.className = 'casa';
                    casa.onclick = () => cliqueTabuleiro(i, j);
                    
                    const peca = estadoJogo.grid[i][j];
                    if (peca) {
                        casa.textContent = peca.texto;
                        casa.classList.add(peca.jogador === 1 ? 'jogador' : 'ia');
                    }
                    
                    // Destacar origem selecionada
                    if (estadoJogo.posicao_origem && 
                        estadoJogo.posicao_origem[0] === i && 
                        estadoJogo.posicao_origem[1] === j) {
                        casa.classList.add('origem');
                    }
                    
                    tabuleiro.appendChild(casa);
                }
            }
        }

        function atualizarStatus() {
            document.getElementById('status').textContent = estadoJogo.mensagem_status;
        }

        function atualizarEstoque() {
            const estJogador = estadoJogo.estoque_jogador;
            const estIA = estadoJogo.estoque_ia;
            
            document.getElementById('estoque_jogador').textContent = 
                `P:${estJogador[1]} M:${estJogador[2]} G:${estJogador[3]}`;
            document.getElementById('estoque_ia').textContent = 
                `P:${estIA[1]} M:${estIA[2]} G:${estIA[3]}`;
        }

        // Inicializar
        atualizarInterface();
    </script>
</body>
</html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))


def main():
    jogo = JogoWeb()
    
    def handler(*args, **kwargs):
        GameHandler(*args, jogo_instance=jogo, **kwargs)
    
    port = 8000
    print(f"🎯 Nhac Nhac - Interface Web")
    print(f"Servidor iniciando na porta {port}")
    print(f"Abra seu navegador em: http://localhost:{port}")
    
    try:
        with socketserver.TCPServer(("", port), handler) as httpd:
            # Tentar abrir o navegador automaticamente
            try:
                webbrowser.open(f'http://localhost:{port}')
            except:
                pass
                
            print("Pressione Ctrl+C para parar o servidor")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor parado!")
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"Porta {port} já está em uso. Tentando porta {port+1}...")
            port += 1
            with socketserver.TCPServer(("", port), handler) as httpd:
                print(f"Servidor iniciado na porta {port}")
                print(f"Abra seu navegador em: http://localhost:{port}")
                try:
                    webbrowser.open(f'http://localhost:{port}')
                except:
                    pass
                httpd.serve_forever()


if __name__ == "__main__":
    main()