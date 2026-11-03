from pathlib import Path

p = Path("modal_app.py")
s = p.read_text(encoding="utf-8")

old = '''        try:
            pipe = get_pipe()
            with torch.inference_mode():
                result = pipe(prompt=prompt, num_inference_steps=20, width=512, height=512)
            image = result.images[0]
'''

new = '''        try:
            # Complementa o prompt sem substituir a ideia original.
            prompt_lower = prompt.casefold()
            complemento = (
                "clear main subject, coherent composition, natural lighting, "
                "realistic proportions, detailed textures"
            )

            if any(x in prompt_lower for x in ("cavalo", "horse")):
                complemento = (
                    "full body horse, natural equine proportions, four visible legs, "
                    "realistic horse anatomy, natural lighting"
                )
            elif any(x in prompt_lower for x in ("girafa", "giraffe")):
                complemento = (
                    "full body giraffe, long natural neck, four visible legs, "
                    "realistic wildlife photography"
                )
            elif any(x in prompt_lower for x in ("onça", "onca", "jaguar")):
                complemento = (
                    "realistic jaguar, natural golden coat with black rosettes, "
                    "anatomically plausible body, detailed wildlife photography"
                )
            elif any(x in prompt_lower for x in ("bicicleta", "ciclista", "bike")):
                complemento = (
                    "complete bicycle with two visible wheels, natural riding posture, "
                    "realistic proportions, coherent scene"
                )
            elif any(x in prompt_lower for x in ("carro", "suv", "veículo", "veiculo")):
                complemento = (
                    "complete vehicle, realistic automotive proportions, "
                    "four visible wheels, coherent paint and reflections"
                )

            prompt_final = f"{prompt}, {complemento}"
            negativo = (
                "blurry, low quality, deformed anatomy, extra limbs, missing limbs, "
                "duplicate objects, malformed hands, distorted proportions, watermark, text"
            )

            pipe = get_pipe()
            with torch.inference_mode():
                result = pipe(
                    prompt=prompt_final,
                    negative_prompt=negativo,
                    num_inference_steps=20,
                    width=512,
                    height=512,
                )
            image = result.images[0]
'''

if old not in s:
    raise SystemExit(
        "ERRO: o bloco original não foi encontrado. Nenhuma alteração foi gravada."
    )

p.write_text(s.replace(old, new, 1), encoding="utf-8")
print("Modal atualizado: otimizacao basica e prompt negativo adicionados.")
