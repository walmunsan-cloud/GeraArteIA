from pathlib import Path

p = Path("modal_app.py")
s = p.read_text(encoding="utf-8")

alvo = "</section></main>`n<script>"
if alvo not in s:
    alvo = "</section></main>\n<script>"

rodape = """</section>
<footer style="text-align:center;margin:42px auto 0;padding:22px 12px 8px;border-top:1px solid #303955;color:#aab3ce;font-size:13px;line-height:1.8">
  <div style="font-weight:600;color:#f4f6ff">GeraArteIA</div>
  <div>Desenvolvido por Walter Muniz Santos e Luan Jesus Pereira Gomes</div>
  <div>Trabalho de Conclusão de Curso — Geração de Imagens por Difusão</div>
</footer>
</main>
<script>"""

if "Desenvolvido por Walter Muniz Santos e Luan Jesus Pereira Gomes" in s:
    print("Os nomes dos criadores já estão no arquivo. Nenhuma alteração necessária.")
elif alvo in s:
    s = s.replace(alvo, rodape, 1)
    p.write_text(s, encoding="utf-8")
    print("Rodapé dos criadores adicionado com sucesso.")
else:
    raise SystemExit("Não encontrei o ponto exato para inserir o rodapé. O arquivo não foi alterado.")
