# -*- coding: utf-8 -*-

import os
import sys
import gc
import time
import traceback
import re

# ============================================================
# GERAARTEIA
# Sistema de geração de imagens por Inteligência Artificial
# ============================================================

os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:32"
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"

# ============================================================
# DIRETÓRIO DO PROJETO
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# ============================================================
# IMPORTS
# ============================================================

import torch
import gradio as gr
import spaces

from diffusers import (
    StableDiffusionPipeline,
    DPMSolverMultistepScheduler,
)

# ============================================================
# CONFIGURAÇÕES
# ============================================================

MODEL_ID = "stable-diffusion-v1-5/stable-diffusion-v1-5"

# ------------------------------------------------------------
# RESOLUÇÃO
# ------------------------------------------------------------
#
# 512x512 é a resolução nativa mais adequada para SD 1.5.
#
# Na GTX 960 de 2 GB usamos CPU offload + attention slicing +
# VAE slicing/tiling para tentar manter o consumo controlado.
#
# ------------------------------------------------------------

IMAGE_WIDTH = 512
IMAGE_HEIGHT = 512

NUM_INFERENCE_STEPS = 24
GUIDANCE_SCALE = 7.0

# Seed padrão.
# O usuário poderá escolher uma seed pela interface.
DEFAULT_SEED = 42

# ============================================================
# NEGATIVE PROMPT
# ============================================================

NEGATIVE_PROMPT = (
    "cropped, cut off, clipped, out of frame, "
    "subject touching image border, "
    "head cut off, face cut off, "
    "body cut off, torso cut off, "
    "legs cut off, feet cut off, paws cut off, "
    "tail cut off, ears cut off, "
    "missing head, missing face, missing body, "
    "missing legs, missing feet, missing paws, "
    "missing tail, "
    "partial body, incomplete body, "
    "deformed, distorted, malformed, "
    "bad anatomy, bad proportions, "
    "mutated, disfigured, "
    "extra head, extra face, "
    "extra limbs, extra legs, extra arms, "
    "extra paws, extra feet, "
    "duplicate subject, duplicated body, "
    "multiple subjects, "
    "blurry, low quality, "
    "low resolution, "
    "text, watermark, logo, "
    "cartoon, anime, illustration, drawing, painting"
)

# ============================================================
# CABEÇALHO
# ============================================================

print()
print("=" * 70)
print("GeraArteIA")
print("Sistema de geração de imagens por Inteligência Artificial")
print("=" * 70)
print()

# ============================================================
# DETECTAR GPU
# ============================================================

if torch.cuda.is_available():

    DEVICE = "cuda"

    GPU_NAME = torch.cuda.get_device_name(0)

    try:
        VRAM_GB = (
            torch.cuda.get_device_properties(0).total_memory
            / (1024 ** 3)
        )
    except Exception:
        VRAM_GB = 0.0

    print("GPU encontrada:")
    print(GPU_NAME)
    print(f"VRAM aproximada: {VRAM_GB:.2f} GB")

else:

    DEVICE = "cpu"
    GPU_NAME = "CPU"
    VRAM_GB = 0.0

    print("GPU CUDA não encontrada.")
    print("Será utilizado CPU.")

# ============================================================
# PRECISÃO
# ============================================================

if DEVICE == "cuda":
    DTYPE = torch.float16
else:
    DTYPE = torch.float32

print()
print("Modelo:", MODEL_ID)
print("Dispositivo:", DEVICE)
print("Resolução:", f"{IMAGE_WIDTH}x{IMAGE_HEIGHT}")
print("Steps:", NUM_INFERENCE_STEPS)
print("Guidance:", GUIDANCE_SCALE)
print("Seed padrão:", DEFAULT_SEED)

# ============================================================
# MODELO
# ============================================================

pipe = None

print()
print("=" * 70)
print("CARREGANDO STABLE DIFFUSION")
print("=" * 70)
print()
print("Aguarde...")
print()

try:

    gc.collect()

    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    # --------------------------------------------------------
    # CARREGAR MODELO
    # --------------------------------------------------------

    print("Carregando componentes do modelo...")
    print()

    pipe = StableDiffusionPipeline.from_pretrained(
        MODEL_ID,
        torch_dtype=DTYPE,
        use_safetensors=True,
        low_cpu_mem_usage=True,
    )

    print()
    print("Pipeline carregado.")

    # --------------------------------------------------------
    # SCHEDULER
    # --------------------------------------------------------

    pipe.scheduler = DPMSolverMultistepScheduler.from_config(
        pipe.scheduler.config
    )

    print("Scheduler: OK")

    # --------------------------------------------------------
    # SAFETY CHECKER
    # --------------------------------------------------------
    #
    # Desabilitado para reduzir consumo de memória.
    #
    # --------------------------------------------------------

    try:
        pipe.safety_checker = None
        pipe.requires_safety_checker = False
        print("Safety checker: DESATIVADO")
    except Exception as erro:
        print("Aviso no safety checker:", erro)

    # --------------------------------------------------------
    # VAE
    # --------------------------------------------------------

    if hasattr(pipe, "vae"):

        try:

            if hasattr(pipe.vae.config, "force_upcast"):
                pipe.vae.config.force_upcast = False

            print("VAE force_upcast: DESATIVADO")

        except Exception as erro:

            print(
                "Aviso ao configurar VAE:",
                str(erro)
            )

    # --------------------------------------------------------
    # OTIMIZAÇÕES CUDA
    # --------------------------------------------------------

    if DEVICE == "cuda":

        # ----------------------------------------------------
        # ATTENTION SLICING
        # ----------------------------------------------------

        try:

            pipe.enable_attention_slicing("max")

            print("Attention slicing: OK")

        except Exception as erro:

            print(
                "Attention slicing:",
                str(erro)
            )

        # ----------------------------------------------------
        # VAE SLICING
        # ----------------------------------------------------

        try:

            pipe.enable_vae_slicing()

            print("VAE slicing: OK")

        except Exception as erro:

            print(
                "VAE slicing:",
                str(erro)
            )

        # ----------------------------------------------------
        # VAE TILING
        # ----------------------------------------------------

        try:

            pipe.enable_vae_tiling()

            print("VAE tiling: OK")

        except Exception as erro:

            print(
                "VAE tiling:",
                str(erro)
            )

        # ----------------------------------------------------
        # SEQUENTIAL CPU OFFLOAD
        # ----------------------------------------------------

        try:

            pipe.enable_sequential_cpu_offload()

            print("Sequential CPU offload: OK")

        except Exception as erro:

            print()
            print("Aviso no CPU offload:")
            print(str(erro))

            try:

                pipe = pipe.to("cuda")

                print(
                    "Fallback: pipeline enviada para CUDA."
                )

            except Exception:

                raise

    else:

        pipe = pipe.to("cpu")

    # --------------------------------------------------------
    # LIMPEZA
    # --------------------------------------------------------

    gc.collect()

    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    print()
    print("=" * 70)
    print("MODELO CARREGADO COM SUCESSO")
    print("=" * 70)
    print()

except Exception:

    print()
    print("=" * 70)
    print("ERRO AO CARREGAR O MODELO")
    print("=" * 70)
    print()

    traceback.print_exc()

    pipe = None


# ============================================================
# DICIONÁRIO DE TERMOS EM PORTUGUÊS
# ============================================================

TRADUCOES = {

    # --------------------------------------------------------
    # ANIMAIS
    # --------------------------------------------------------

    "cavalo": "horse",
    "cavalos": "horses",

    "égua": "mare",
    "éguas": "mares",

    "cachorro": "dog",
    "cachorros": "dogs",
    "cão": "dog",
    "cães": "dogs",

    "gato": "cat",
    "gatos": "cats",

    "leão": "lion",
    "leões": "lions",

    "tigre": "tiger",
    "tigres": "tigers",

    "urso": "bear",
    "ursos": "bears",

    "lobo": "wolf",
    "lobos": "wolves",

    "raposa": "fox",
    "raposas": "foxes",

    "elefante": "elephant",
    "elefantes": "elephants",

    "girafa": "giraffe",
    "girafas": "giraffes",

    "zebra": "zebra",
    "zebras": "zebras",

    "vaca": "cow",
    "vacas": "cows",

    "boi": "ox",
    "bois": "oxen",

    "touro": "bull",
    "touros": "bulls",

    "porco": "pig",
    "porcos": "pigs",

    "ovelha": "sheep",
    "ovelhas": "sheep",

    "cabra": "goat",
    "cabras": "goats",

    "coelho": "rabbit",
    "coelhos": "rabbits",

    "macaco": "monkey",
    "macacos": "monkeys",

    "pássaro": "bird",
    "pássaros": "birds",
    "passaro": "bird",
    "passaros": "birds",

    "águia": "eagle",
    "águias": "eagles",
    "aguia": "eagle",
    "aguias": "eagles",

    "galinha": "chicken",
    "galinhas": "chickens",

    "galo": "rooster",
    "galos": "roosters",

    "peixe": "fish",
    "peixes": "fish",

    # --------------------------------------------------------
    # PESSOAS
    # --------------------------------------------------------

    "homem": "man",
    "homens": "men",

    "mulher": "woman",
    "mulheres": "women",

    "menino": "boy",
    "meninos": "boys",

    "menina": "girl",
    "meninas": "girls",

    "criança": "child",
    "crianças": "children",

    "pessoa": "person",
    "pessoas": "people",

    "bebê": "baby",
    "bebe": "baby",

    # --------------------------------------------------------
    # VEÍCULOS
    # --------------------------------------------------------

    "carro": "car",
    "carros": "cars",

    "moto": "motorcycle",
    "motos": "motorcycles",

    "motocicleta": "motorcycle",
    "motocicletas": "motorcycles",

    "caminhão": "truck",
    "caminhões": "trucks",
    "caminhao": "truck",
    "caminhoes": "trucks",

    "ônibus": "bus",
    "onibus": "bus",

    "avião": "airplane",
    "aviões": "airplanes",
    "aviao": "airplane",
    "avioes": "airplanes",

    "bicicleta": "bicycle",
    "bicicletas": "bicycles",

    # --------------------------------------------------------
    # NATUREZA
    # --------------------------------------------------------

    "praia": "beach",
    "campo": "field",
    "floresta": "forest",
    "montanha": "mountain",
    "montanhas": "mountains",

    "lago": "lake",
    "rio": "river",
    "cachoeira": "waterfall",

    "cidade": "city",
    "fazenda": "farm",

    "deserto": "desert",
    "flor": "flower",
    "flores": "flowers",

    "árvore": "tree",
    "árvores": "trees",
    "arvore": "tree",
    "arvores": "trees",

    "grama": "grass",
    "céu": "sky",
    "nuvem": "cloud",
    "nuvens": "clouds",

    # --------------------------------------------------------
    # CORES
    # --------------------------------------------------------

    "marrom": "brown",
    "preto": "black",
    "preta": "black",
    "branco": "white",
    "branca": "white",

    "vermelho": "red",
    "vermelha": "red",

    "azul": "blue",
    "verde": "green",

    "amarelo": "yellow",
    "amarela": "yellow",

    "laranja": "orange",
    "rosa": "pink",
    "roxo": "purple",
    "cinza": "gray",

    # --------------------------------------------------------
    # AÇÕES
    # --------------------------------------------------------

    "correndo": "running",
    "correr": "running",

    "caminhando": "walking",
    "caminhar": "walking",

    "andando": "walking",
    "andar": "walking",

    "parado": "standing",
    "parada": "standing",

    "saltando": "jumping",
    "saltar": "jumping",

    "pulando": "jumping",
    "pular": "jumping",

    "voando": "flying",
    "voar": "flying",

    "nadando": "swimming",
    "nadar": "swimming",

    "deitado": "lying down",
    "deitada": "lying down",

    "sentado": "sitting",
    "sentada": "sitting",

    # --------------------------------------------------------
    # AMBIENTE / TEMPO
    # --------------------------------------------------------

    "pôr do sol": "sunset",
    "por do sol": "sunset",

    "amanhecer": "sunrise",

    "noite": "night",
    "dia": "day",

    "ensolarado": "sunny",
    "ensolarada": "sunny",

    "chuvoso": "rainy",
    "chuvosa": "rainy",

    "nublado": "cloudy",
    "nublada": "cloudy",

    # --------------------------------------------------------
    # FOTOGRAFIA / ESTILO
    # --------------------------------------------------------

    "fotografia realista": "realistic photography",
    "fotografia": "photography",

    "realista": "photorealistic",
    "realista": "photorealistic",

    "realismo": "photorealistic",

    "retrato": "portrait",

    "profissional": "professional photography",

    "cinematográfico": "cinematic",
    "cinematografico": "cinematic",

    "natural": "natural",

    # --------------------------------------------------------
    # ROUPAS / OBJETOS COMUNS
    # --------------------------------------------------------

    "chapéu": "hat",
    "chapeu": "hat",

    "camisa": "shirt",
    "calça": "pants",
    "vestido": "dress",

    "casa": "house",
    "casas": "houses",

    "igreja": "church",
    "prédio": "building",
    "predio": "building",

    "ponte": "bridge",
    "estrada": "road",
    "rua": "street",

}


# ============================================================
# TERMOS DE COMPOSIÇÃO
# ============================================================

COMPOSICAO_ANIMAL = (
    "single main animal, "
    "full body visible from head to feet, "
    "complete head fully visible, "
    "complete face visible, "
    "complete body visible, "
    "complete legs visible, "
    "complete tail visible, "
    "ears fully visible, "
    "subject entirely inside the frame, "
    "wide framing, "
    "medium distance from subject, "
    "clear space around the entire animal, "
    "no body part touching the image border"
)

COMPOSICAO_PESSOA = (
    "single main person, "
    "full body visible from head to feet, "
    "complete head fully visible, "
    "complete face visible, "
    "complete arms and hands visible, "
    "complete legs and feet visible, "
    "subject entirely inside the frame, "
    "wide framing, "
    "medium distance from subject, "
    "clear space around the entire person, "
    "no body part touching the image border"
)

COMPOSICAO_GERAL = (
    "single clear main subject, "
    "entire subject fully visible, "
    "subject completely inside the frame, "
    "wide framing, "
    "medium distance from subject, "
    "clear space around the subject, "
    "no important part touching the image border"
)


# ============================================================
# DETECTAR ANIMAL
# ============================================================

def detectar_animal(texto):

    animais = [
        "cavalo",
        "cavalos",
        "égua",
        "éguas",
        "cachorro",
        "cachorros",
        "cão",
        "cães",
        "gato",
        "gatos",
        "leão",
        "leões",
        "leao",
        "leoes",
        "tigre",
        "tigres",
        "urso",
        "ursos",
        "lobo",
        "lobos",
        "raposa",
        "raposas",
        "elefante",
        "elefantes",
        "girafa",
        "girafas",
        "zebra",
        "zebras",
        "vaca",
        "vacas",
        "boi",
        "bois",
        "touro",
        "touros",
        "porco",
        "porcos",
        "ovelha",
        "ovelhas",
        "cabra",
        "cabras",
        "coelho",
        "coelhos",
        "macaco",
        "macacos",
        "pássaro",
        "pássaros",
        "passaro",
        "passaros",
        "águia",
        "águias",
        "aguia",
        "aguias",
        "galinha",
        "galinhas",
        "galo",
        "galos",
        "peixe",
        "peixes",
    ]

    texto_lower = texto.lower()

    return any(
        re.search(
            r"\b" + re.escape(animal) + r"\b",
            texto_lower,
        )
        for animal in animais
    )


# ============================================================
# DETECTAR PESSOA
# ============================================================

def detectar_pessoa(texto):

    pessoas = [
        "homem",
        "homens",
        "mulher",
        "mulheres",
        "menino",
        "meninos",
        "menina",
        "meninas",
        "criança",
        "crianças",
        "pessoa",
        "pessoas",
        "bebê",
        "bebe",
    ]

    texto_lower = texto.lower()

    return any(
        re.search(
            r"\b" + re.escape(pessoa) + r"\b",
            texto_lower,
        )
        for pessoa in pessoas
    )


# ============================================================
# TRADUZIR TERMOS
# ============================================================

def traduzir_termos(texto):

    resultado = texto

    termos_ordenados = sorted(
        TRADUCOES.items(),
        key=lambda item: len(item[0]),
        reverse=True,
    )

    for portugues, ingles in termos_ordenados:

        padrao = re.compile(
            r"\b" + re.escape(portugues) + r"\b",
            re.IGNORECASE,
        )

        resultado = padrao.sub(
            ingles,
            resultado,
        )

    return resultado


# ============================================================
# LIMPAR TEXTO
# ============================================================

def limpar_texto(texto):

    texto = re.sub(
        r"\s+",
        " ",
        texto,
    )

    texto = texto.replace(
        " ,",
        ","
    )

    texto = texto.replace(
        ", ,",
        ","
    )

    texto = re.sub(
        r",\s*,+",
        ",",
        texto,
    )

    return texto.strip(" ,")


# ============================================================
# TOKENIZAÇÃO SEGURA
# ============================================================

def limitar_prompt(prompt_texto, max_tokens=72):

    if not prompt_texto:
        return ""

    if pipe is None:
        return prompt_texto

    try:

        tokenizer = pipe.tokenizer

        tokens = tokenizer(
            prompt_texto,
            truncation=True,
            max_length=max_tokens,
            padding=False,
            return_tensors="pt",
        )

        texto = tokenizer.decode(
            tokens.input_ids[0],
            skip_special_tokens=True,
            clean_up_tokenization_spaces=True,
        )

        return limpar_texto(texto)

    except Exception as erro:

        print(
            "Aviso ao limitar prompt:",
            str(erro)
        )

        return prompt_texto


# ============================================================
# PREPARAR PROMPT PRINCIPAL
# ============================================================

def preparar_prompt(prompt_original):

    texto = limpar_texto(
        prompt_original
    )

    if not texto:
        return ""

    eh_animal = detectar_animal(texto)
    eh_pessoa = detectar_pessoa(texto)

    # --------------------------------------------------------
    # TRADUZIR TERMOS CONHECIDOS
    # --------------------------------------------------------

    texto_ingles = traduzir_termos(
        texto
    )

    texto_ingles = limpar_texto(
        texto_ingles
    )

    # --------------------------------------------------------
    # ESCOLHER COMPOSIÇÃO
    # --------------------------------------------------------

    if eh_animal:

        composicao = COMPOSICAO_ANIMAL

    elif eh_pessoa:

        composicao = COMPOSICAO_PESSOA

    else:

        composicao = COMPOSICAO_GERAL

    # --------------------------------------------------------
    # PROMPT
    # --------------------------------------------------------
    #
    # A ordem é importante.
    #
    # Colocamos primeiro as características de composição,
    # depois o conteúdo solicitado pelo usuário.
    #
    # --------------------------------------------------------

    partes = [
        composicao,
        texto_ingles,
        "natural proportions",
        "correct anatomy",
        "realistic proportions",
        "sharp focus",
        "detailed subject",
        "realistic lighting",
        "natural perspective",
        "photorealistic photography",
    ]

    if eh_animal:

        partes.extend([
            "realistic animal anatomy",
            "natural animal proportions",
            "detailed realistic fur",
        ])

    if eh_pessoa:

        partes.extend([
            "natural human anatomy",
            "realistic face",
            "natural human proportions",
        ])

    prompt_final = limpar_texto(
        ", ".join(partes)
    )

    # --------------------------------------------------------
    # LIMITAR SEM PERDER O COMEÇO
    # --------------------------------------------------------

    prompt_final = limitar_prompt(
        prompt_final,
        max_tokens=72,
    )

    return prompt_final


# ============================================================
# NEGATIVE PROMPT
# ============================================================

def preparar_negative_prompt(
    prompt_original
):

    negativo = NEGATIVE_PROMPT

    if detectar_animal(
        prompt_original
    ):

        negativo += (
            ", bad animal anatomy, "
            "animal deformation, "
            "missing animal parts, "
            "cut off animal, "
            "cropped animal, "
            "animal outside frame, "
            "animal touching border"
        )

    if detectar_pessoa(
        prompt_original
    ):

        negativo += (
            ", bad human anatomy, "
            "deformed face, "
            "deformed body, "
            "extra fingers, "
            "missing fingers, "
            "cropped person, "
            "person outside frame"
        )

    negativo = limpar_texto(
        negativo
    )

    return limitar_prompt(
        negativo,
        max_tokens=72,
    )


# ============================================================
# GERAR IMAGEM
# ============================================================

@spaces.GPU
def gerar_imagem(
    prompt,
    seed,
):

    global pipe

    # --------------------------------------------------------
    # MODELO
    # --------------------------------------------------------

    if pipe is None:

        raise gr.Error(
            "O modelo Stable Diffusion não foi carregado. "
            "Verifique o terminal."
        )

    # --------------------------------------------------------
    # PROMPT
    # --------------------------------------------------------

    if (
        prompt is None
        or not prompt.strip()
    ):

        raise gr.Error(
            "Digite uma descrição para gerar a imagem."
        )

    prompt_original = prompt.strip()

    # --------------------------------------------------------
    # SEED
    # --------------------------------------------------------

    try:

        seed = int(seed)

    except Exception:

        seed = DEFAULT_SEED

    if seed < 0:

        seed = DEFAULT_SEED

    # --------------------------------------------------------
    # PROMPTS
    # --------------------------------------------------------

    prompt_final = preparar_prompt(
        prompt_original
    )

    negative_prompt_final = (
        preparar_negative_prompt(
            prompt_original
        )
    )

    # --------------------------------------------------------
    # TERMINAL
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("NOVA GERAÇÃO")
    print("=" * 70)

    print()
    print("Prompt original:")
    print(prompt_original)

    print()
    print("Prompt final:")
    print(prompt_final)

    print()
    print("Negative prompt:")
    print(negative_prompt_final)

    print()
    print("Resolução:")
    print(
        f"{IMAGE_WIDTH}x{IMAGE_HEIGHT}"
    )

    print()
    print("Steps:")
    print(NUM_INFERENCE_STEPS)

    print()
    print("Guidance:")
    print(GUIDANCE_SCALE)

    print()
    print("Seed:")
    print(seed)

    print()
    print("Gerando imagem...")
    print()

    inicio = time.perf_counter()

    # --------------------------------------------------------
    # LIMPEZA DE MEMÓRIA
    # --------------------------------------------------------

    gc.collect()

    if torch.cuda.is_available():

        torch.cuda.empty_cache()

        try:
            torch.cuda.reset_peak_memory_stats()
        except Exception:
            pass

    # --------------------------------------------------------
    # GERADOR
    # --------------------------------------------------------

    generator = torch.Generator(
        device="cpu"
    ).manual_seed(
        seed
    )

    # --------------------------------------------------------
    # GERAÇÃO
    # --------------------------------------------------------

    try:

        with torch.inference_mode():

            resultado = pipe(
                prompt=prompt_final,
                negative_prompt=negative_prompt_final,
                width=IMAGE_WIDTH,
                height=IMAGE_HEIGHT,
                num_inference_steps=NUM_INFERENCE_STEPS,
                guidance_scale=GUIDANCE_SCALE,
                generator=generator,
            )

        if (
            resultado is None
            or not hasattr(
                resultado,
                "images"
            )
            or not resultado.images
        ):

            raise RuntimeError(
                "O pipeline não retornou uma imagem."
            )

        imagem = resultado.images[0]

    except torch.cuda.OutOfMemoryError:

        print()
        print("=" * 70)
        print("CUDA OUT OF MEMORY")
        print("=" * 70)
        print()

        traceback.print_exc()

        gc.collect()

        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        raise gr.Error(
            "A GPU ficou sem memória. "
            "Tente novamente ou reduza a resolução."
        )

    except Exception:

        print()
        print("=" * 70)
        print("ERRO DURANTE A GERAÇÃO")
        print("=" * 70)
        print()

        traceback.print_exc()

        gc.collect()

        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        raise gr.Error(
            "Erro durante a geração. "
            "Veja o terminal para identificar o problema."
        )

    # --------------------------------------------------------
    # VALIDAR IMAGEM
    # --------------------------------------------------------

    if imagem is None:

        raise gr.Error(
            "O Stable Diffusion não retornou uma imagem."
        )

    # --------------------------------------------------------
    # RGB
    # --------------------------------------------------------

    try:

        if imagem.mode != "RGB":

            imagem = imagem.convert(
                "RGB"
            )

    except Exception:
        pass

    # --------------------------------------------------------
    # TEMPO
    # --------------------------------------------------------

    tempo = (
        time.perf_counter()
        - inicio
    )

    print()
    print("=" * 70)
    print("IMAGEM GERADA COM SUCESSO")
    print("=" * 70)
    print()

    print(
        f"Tempo de geração: {tempo:.2f} segundos"
    )

    # --------------------------------------------------------
    # VRAM
    # --------------------------------------------------------

    if torch.cuda.is_available():

        try:

            memoria = (
                torch.cuda.max_memory_allocated()
                / (1024 ** 3)
            )

            print(
                f"Pico de VRAM: {memoria:.2f} GB"
            )

            torch.cuda.reset_peak_memory_stats()

        except Exception:
            pass

    print()

    # --------------------------------------------------------
    # LIMPEZA
    # --------------------------------------------------------

    gc.collect()

    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    return imagem


# ============================================================
# INTERFACE
# ============================================================

with gr.Blocks(
    title="GeraArteIA"
) as demo:

    gr.Markdown(
        """
# 🎨 GeraArteIA

### Geração de imagens por Inteligência Artificial

Digite em **português** o que você deseja criar.

O sistema prepara automaticamente a descrição para o
Stable Diffusion, buscando melhorar:

- composição;
- enquadramento;
- corpo completo;
- cabeça completa;
- anatomia;
- proporções;
- iluminação;
- perspectiva;
- realismo fotográfico.

### Exemplo

**um cavalo marrom correndo em um campo verde ao pôr do sol**

O sistema tenta manter o animal inteiro dentro da imagem,
com espaço ao redor da cabeça, patas e cauda.
"""
    )

    # --------------------------------------------------------
    # PROMPT
    # --------------------------------------------------------

    prompt = gr.Textbox(
        label="Descrição da imagem",

        placeholder=(
            "Exemplo: um cavalo marrom correndo em um "
            "campo verde ao pôr do sol, fotografia realista"
        ),

        lines=5,
    )

    # --------------------------------------------------------
    # SEED
    # --------------------------------------------------------

    seed = gr.Number(
        label="Seed",
        value=DEFAULT_SEED,
        precision=0,
        minimum=0,
        maximum=2147483647,
    )

    # --------------------------------------------------------
    # BOTÃO
    # --------------------------------------------------------

    gerar = gr.Button(
        "✨ Gerar imagem",
        variant="primary",
    )

    # --------------------------------------------------------
    # RESULTADO
    # --------------------------------------------------------

    resultado = gr.Image(
        label="Imagem gerada",
        type="pil",
    )

    # --------------------------------------------------------
    # EVENTO
    # --------------------------------------------------------

    gerar.click(
        fn=gerar_imagem,
        inputs=[
            prompt,
            seed,
        ],
        outputs=resultado,
    )

    # --------------------------------------------------------
    # RODAPÉ
    # --------------------------------------------------------

    gr.Markdown(
        """
---

**GeraArteIA**

Projeto acadêmico de geração de imagens por difusão.

Modelo utilizado: Stable Diffusion v1.5
"""
    )


# ============================================================
# INICIAR
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 70)
    print("INICIANDO INTERFACE WEB")
    print("=" * 70)
    print()

    if pipe is not None:

        print("Modelo: CARREGADO")

    else:

        print("Modelo: NÃO CARREGADO")

    print()
    print("Acesse:")
    print(
        "http://127.0.0.1:7860"
    )

    print()

    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        inbrowser=True,
    )