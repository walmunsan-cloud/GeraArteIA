from pathlib import Path

db_path = Path("app/database.py")
api_path = Path("web_app.py")
html_path = Path("web/templates/index.html")

db = db_path.read_text(encoding="utf-8")
api = api_path.read_text(encoding="utf-8")
html = html_path.read_text(encoding="utf-8")

# 1. Função para recuperar o histórico salvo no SQLite.
if "def obter_historico(" not in db:
    db += '''


def obter_historico(limite=30):
    with conectar() as conexao:
        linhas = conexao.execute(
            """
            SELECT id, prompt, arquivo, criado_em, nota
            FROM geracoes
            ORDER BY id DESC
            LIMIT ?
            """,
            (limite,),
        ).fetchall()

    return [
        {
            "id": linha["id"],
            "prompt": linha["prompt"],
            "arquivo": linha["arquivo"],
            "criado_em": linha["criado_em"],
            "nota": linha["nota"],
            "imagem": f"/api/imagem/{linha['arquivo']}",
        }
        for linha in linhas
    ]
'''
    db_path.write_text(db, encoding="utf-8")

# 2. Rota de histórico na API.
if "def historico():" not in api:
    api = api.replace(
        "    obter_estatisticas,",
        "    obter_estatisticas,\n    obter_historico,"
        , 1
    )
    anchor = '@app.get("/api/dashboard")'
    if anchor not in api:
        raise SystemExit("Não encontrei a rota do dashboard em web_app.py.")
    api = api.replace(
        anchor,
        '@app.get("/api/historico")\ndef historico():\n'
        '    return obter_historico()\n\n\n' + anchor,
        1,
    )
    api_path.write_text(api, encoding="utf-8")

# 3. Estilos novos.
css = r"""
        .rating-panel {
            margin-top: 18px;
            padding: 16px;
            border: 1px solid var(--border);
            border-radius: 13px;
            background: #121626;
        }
        .rating-panel h3 { margin: 0 0 7px; font-size: 15px; }
        .rating-panel p { margin: 0 0 12px; color: var(--muted); font-size: 12px; }
        .rating-options { display: flex; flex-wrap: wrap; gap: 6px; }
        .rating-option {
            min-width: 34px; padding: 8px 6px; border: 1px solid var(--border);
            border-radius: 8px; background: #242941; color: var(--text);
        }
        .rating-option.selecionada { background: var(--blue); border-color: var(--blue); }
        .rating-save { margin-top: 12px; }
        .dashboard { margin-top: 28px; }
        .dashboard-grid {
            display: grid; grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 12px; margin-top: 16px;
        }
        .metric {
            padding: 18px; border: 1px solid var(--border); border-radius: 14px;
            background: linear-gradient(145deg, #20253b, #171b2c);
        }
        .metric-label { color: var(--muted); font-size: 12px; }
        .metric-value { margin-top: 8px; font-size: 27px; font-weight: 750; }
        .chart { margin-top: 18px; padding: 18px; border: 1px solid var(--border);
            border-radius: 14px; background: #121626; }
        .chart h3 { margin: 0 0 16px; font-size: 15px; }
        .bar-row { display: grid; grid-template-columns: 42px 1fr 28px;
            align-items: center; gap: 10px; margin: 9px 0; font-size: 12px; }
        .bar-track { height: 11px; overflow: hidden; border-radius: 99px; background: #292e49; }
        .bar-fill { height: 100%; border-radius: 99px;
            background: linear-gradient(90deg, var(--blue), var(--purple)); }
        .persistent-history { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr));
            gap: 10px; margin-top: 12px; }
        .persistent-item { min-width: 0; padding: 6px; border: 1px solid var(--border);
            border-radius: 10px; background: #121626; color: var(--text); text-align: left; }
        .persistent-item img { width: 100%; aspect-ratio: 1; object-fit: cover; border-radius: 7px; }
        .persistent-item span { display: block; margin-top: 6px; overflow-wrap: anywhere;
            font-size: 11px; color: var(--muted); }
        @media (max-width: 650px) {
            .dashboard-grid { grid-template-columns: 1fr; }
            .persistent-history { grid-template-columns: repeat(2, minmax(0, 1fr)); }
        }
"""

if ".rating-panel {" not in html:
    html = html.replace("    </style>", css + "\n    </style>", 1)

# 4. Área de avaliação abaixo dos botões da imagem.
rating_html = """
                    <div class="rating-panel" id="ratingPanel">
                        <h3>Avalie esta imagem</h3>
                        <p>De 0 (insatisfeito) a 10 (muito satisfeito).</p>
                        <div class="rating-options" id="ratingOptions" role="group" aria-label="Nota de satisfação">
"""
for i in range(11):
    rating_html += f'                            <button type="button" class="rating-option" data-nota="{i}" aria-pressed="false">{i}</button>\n'
rating_html += """                        </div>
                        <button type="button" class="secondary rating-save" id="btnAvaliar">Salvar avaliação</button>
                        <p id="ratingStatus" role="status" aria-live="polite" style="margin-top:10px"></p>
                    </div>
"""

if 'id="ratingPanel"' not in html:
    marker = '                    <div class="image-actions">'
    start = html.find(marker)
    if start < 0:
        raise SystemExit("Não encontrei os botões de ação da imagem.")
    close = html.find("                    </div>", start)
    if close < 0:
        raise SystemExit("Não encontrei o fechamento da área de botões.")
    close += len("                    </div>")
    html = html[:close] + "\n" + rating_html + html[close:]

# 5. Painel e histórico permanente antes do rodapé.
dashboard_html = """
        <section class="card dashboard">
            <h2 class="section-title">Painel de resultados</h2>
            <p class="section-help">Indicadores calculados com os registros salvos nesta instalação.</p>
            <div class="dashboard-grid">
                <div class="metric"><div class="metric-label">Imagens geradas</div><div class="metric-value" id="metricGeracoes">—</div></div>
                <div class="metric"><div class="metric-label">Avaliações recebidas</div><div class="metric-value" id="metricAvaliacoes">—</div></div>
                <div class="metric"><div class="metric-label">Média de satisfação</div><div class="metric-value" id="metricMedia">—</div></div>
            </div>
            <div class="chart">
                <h3>Distribuição das notas</h3>
                <div id="graficoSatisfacao"><p class="section-help">Carregando estatísticas...</p></div>
            </div>
        </section>

        <section class="card dashboard">
            <div class="history-heading">
                <h2>Histórico salvo</h2>
                <button type="button" class="secondary" id="btnAtualizarHistorico">Atualizar</button>
            </div>
            <p class="section-help">As últimas 30 imagens registradas no banco de dados.</p>
            <div class="persistent-history" id="historicoPersistente">
                <div class="history-empty">Carregando histórico...</div>
            </div>
        </section>
"""

if 'id="metricGeracoes"' not in html:
    html = html.replace("        <footer>", dashboard_html + "\n        <footer>", 1)

# 6. Ajustes mínimos no JavaScript existente.
old_show = """        function mostrarImagem(url, prompt) {
            imagemAtual = { url, prompt };
            imagemEl.src = url;
            areaImagem.style.display = "block";
            estadoVazio.style.display = "none";
        }"""
new_show = """        function mostrarImagem(url, prompt, id = null, nota = null) {
            imagemAtual = { url, prompt, id, nota };
            imagemEl.src = url;
            areaImagem.style.display = "block";
            estadoVazio.style.display = "none";
            document.querySelectorAll(".rating-option").forEach((botao) => {
                const selecionada = nota !== null && Number(botao.dataset.nota) === Number(nota);
                botao.classList.toggle("selecionada", selecionada);
                botao.setAttribute("aria-pressed", String(selecionada));
            });
            document.getElementById("ratingStatus").textContent =
                nota === null ? "" : `Nota registrada: ${nota}/10`;
        }"""

if old_show in html:
    html = html.replace(old_show, new_show, 1)
elif "function mostrarImagem(url, prompt, id = null, nota = null)" not in html:
    raise SystemExit("Não encontrei a função mostrarImagem esperada.")

html = html.replace(
    "mostrarImagem(item.url, item.prompt);",
    "mostrarImagem(item.url, item.prompt, item.id, item.nota);",
    1,
)

html = html.replace(
    "mostrarImagem(urlImagem, prompt);",
    "mostrarImagem(urlImagem, prompt, dados.id, null);",
    1,
)

html = html.replace(
    """                    prompt,
                    arquivo: dados.arquivo || ""
                });""",
    """                    prompt,
                    id: dados.id,
                    nota: null,
                    arquivo: dados.arquivo || ""
                });""",
    1,
)

js_extra = r"""
        let notaSelecionada = null;

        document.querySelectorAll(".rating-option").forEach((botao) => {
            botao.addEventListener("click", () => {
                notaSelecionada = Number(botao.dataset.nota);
                document.querySelectorAll(".rating-option").forEach((opcao) => {
                    const ativa = opcao === botao;
                    opcao.classList.toggle("selecionada", ativa);
                    opcao.setAttribute("aria-pressed", String(ativa));
                });
            });
        });

        document.getElementById("btnAvaliar").addEventListener("click", async () => {
            const status = document.getElementById("ratingStatus");
            if (!imagemAtual || !imagemAtual.id) {
                status.textContent = "Selecione uma imagem gerada nesta versão para avaliá-la.";
                return;
            }
            if (notaSelecionada === null) {
                status.textContent = "Escolha uma nota de 0 a 10.";
                return;
            }
            try {
                const resposta = await fetch("/api/avaliar", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({geracao_id: imagemAtual.id, nota: notaSelecionada})
                });
                const dados = await resposta.json();
                if (!resposta.ok) throw new Error(dados.detail || "Não foi possível salvar a nota.");
                imagemAtual.nota = notaSelecionada;
                const item = imagensDaSessao.find((x) => x.id === imagemAtual.id);
                if (item) item.nota = notaSelecionada;
                status.textContent = `Avaliação ${notaSelecionada}/10 salva com sucesso.`;
                await carregarDashboard();
                await carregarHistoricoPersistente();
            } catch (erro) {
                status.textContent = "Erro ao salvar avaliação: " + erro.message;
            }
        });

        async function carregarDashboard() {
            const resposta = await fetch("/api/dashboard");
            if (!resposta.ok) throw new Error("Falha ao consultar o painel.");
            const dados = await resposta.json();
            document.getElementById("metricGeracoes").textContent = dados.total_geracoes;
            document.getElementById("metricAvaliacoes").textContent = dados.total_avaliacoes;
            document.getElementById("metricMedia").textContent =
                dados.media_satisfacao === null ? "—" : `${Number(dados.media_satisfacao).toFixed(1)}/10`;

            const contagens = Array.from({length: 11}, (_, nota) => {
                const registro = dados.avaliacoes.find((x) => Number(x.nota) === nota);
                return {nota, quantidade: registro ? registro.quantidade : 0};
            });
            const maximo = Math.max(1, ...contagens.map((x) => x.quantidade));
            const grafico = document.getElementById("graficoSatisfacao");
            grafico.replaceChildren();
            contagens.forEach(({nota, quantidade}) => {
                const linha = document.createElement("div");
                linha.className = "bar-row";
                const rotulo = document.createElement("span");
                rotulo.textContent = `${nota}/10`;
                const trilho = document.createElement("div");
                trilho.className = "bar-track";
                const barra = document.createElement("div");
                barra.className = "bar-fill";
                barra.style.width = `${quantidade / maximo * 100}%`;
                trilho.appendChild(barra);
                const valor = document.createElement("span");
                valor.textContent = quantidade;
                linha.append(rotulo, trilho, valor);
                grafico.appendChild(linha);
            });
        }

        async function carregarHistoricoPersistente() {
            const area = document.getElementById("historicoPersistente");
            const resposta = await fetch("/api/historico");
            if (!resposta.ok) throw new Error("Falha ao carregar o histórico.");
            const itens = await resposta.json();
            area.replaceChildren();
            if (!itens.length) {
                const vazio = document.createElement("div");
                vazio.className = "history-empty";
                vazio.textContent = "Nenhuma imagem foi salva ainda. Gere a primeira imagem para iniciar o histórico.";
                area.appendChild(vazio);
                return;
            }
            itens.forEach((item) => {
                const botao = document.createElement("button");
                botao.type = "button";
                botao.className = "persistent-item";
                const img = document.createElement("img");
                img.loading = "lazy";
                img.src = item.imagem;
                img.alt = item.prompt;
                const legenda = document.createElement("span");
                legenda.textContent = `${item.prompt} · ${item.nota === null ? "Sem nota" : "Nota " + item.nota + "/10"}`;
                botao.append(img, legenda);
                botao.addEventListener("click", () => {
                    campoPrompt.value = item.prompt;
                    campoPrompt.dispatchEvent(new Event("input"));
                    mostrarImagem(item.imagem, item.prompt, item.id, item.nota);
                    notaSelecionada = item.nota === null ? null : Number(item.nota);
                    areaImagem.scrollIntoView({behavior: "smooth", block: "center"});
                });
                area.appendChild(botao);
            });
        }

        document.getElementById("btnAtualizarHistorico").addEventListener("click", async () => {
            try {
                await carregarHistoricoPersistente();
                mostrarStatus("Histórico atualizado.", "sucesso");
            } catch (erro) {
                mostrarStatus(erro.message, "erro");
            }
        });

        // Atualiza o painel e o histórico sem exigir uma geração de imagem.
        Promise.all([carregarDashboard(), carregarHistoricoPersistente()])
            .catch((erro) => console.error("Falha ao carregar painel/histórico:", erro));
"""

if "async function carregarDashboard()" not in html:
    marker = "    </script>"
    if marker not in html:
        raise SystemExit("Não encontrei o fechamento do JavaScript.")
    html = html.replace(marker, js_extra + "\n" + marker, 1)

html_path.write_text(html, encoding="utf-8")
print("Interface atualizada: avaliação, painel, gráfico e histórico persistente.")
