from app.prompt_optimizer import PromptOptimizer

otimizador = PromptOptimizer()

casos = [
    ("Cavalo", "Um cavalo realista galopando em um campo"),
    ("Girafa", "Uma girafa inteira na savana africana"),
    ("SUV rosa", "Um SUV rosa com um laço rosa"),
    ("Tatuagem de onça", "Uma tatuagem realista de uma onça"),
    ("Ciclista", "Um ciclista andando de bicicleta na ciclovia da cidade"),
]

falhas = []

for nome, entrada in casos:
    categoria = otimizador.detectar_categoria(entrada)
    prompt = otimizador.otimizar(entrada)

    print("\n" + "=" * 72)
    print(f"CASO: {nome}")
    print(f"CATEGORIA: {categoria}")
    print(f"PROMPT OTIMIZADO:\n{prompt}")

    if not prompt or entrada not in prompt:
        falhas.append(f"{nome}: prompt original ausente")

    if nome == "Cavalo" and "anatomically plausible horse" not in prompt:
        falhas.append("Cavalo: instrução anatômica ausente")

    if nome == "Girafa" and "giraffe" not in prompt.lower():
        falhas.append("Girafa: instruções específicas ausentes")

    if nome == "SUV rosa" and "vehicle paint is pink" not in prompt:
        falhas.append("SUV rosa: instrução de cor ausente")

    if nome == "Tatuagem de onça" and "tattoo design" not in prompt:
        falhas.append("Tatuagem de onça: instruções de tatuagem ausentes")

    if nome == "Ciclista" and "designated bike lane" not in prompt:
        falhas.append("Ciclista: instrução de ciclovia ausente")

print("\n" + "=" * 72)
if falhas:
    print("RESULTADO: FORAM ENCONTRADOS PROBLEMAS")
    for falha in falhas:
        print(f"- {falha}")
    raise SystemExit(1)

print("RESULTADO: TODOS OS CINCO CASOS PASSARAM.")
