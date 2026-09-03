# GeraArteIA

## Sistema de Geração de Imagens por Inteligência Artificial

O **GeraArteIA** é um sistema de geração de imagens a partir de descrições textuais (*text-to-image*), desenvolvido como projeto acadêmico de **Pós-Graduação em Engenharia de Software: Automação, Inovação e Inteligência Artificial**.

O projeto utiliza técnicas de **Inteligência Artificial Generativa** e **modelos de difusão**, tendo como modelo principal o **Stable Diffusion v1.5**.

O objetivo é transformar uma descrição fornecida pelo usuário em uma imagem gerada artificialmente, utilizando processamento por GPU quando disponível.

---

## 🎓 Projeto Acadêmico

**Projeto:** GeraArteIA
**Tema:** Geração de Imagens por Difusão
**Área:** Inteligência Artificial Generativa
**Curso:** Pós-Graduação em Engenharia de Software: Automação, Inovação e Inteligência Artificial

O projeto foi desenvolvido com foco em demonstrar, de forma prática, a aplicação de modelos de difusão na geração de conteúdo visual a partir de linguagem natural.

---

## 🧠 Sobre o Projeto

O GeraArteIA recebe uma descrição textual informada pelo usuário e utiliza um modelo de difusão para produzir uma imagem correspondente.

Fluxo simplificado:

```text
Usuário
   │
   ▼
Descrição textual
   │
   ▼
Otimização do prompt
   │
   ▼
Stable Diffusion v1.5
   │
   ▼
Processamento por IA
   │
   ▼
Imagem gerada
```

A aplicação possui uma interface web desenvolvida com **FastAPI**, permitindo que o usuário interaja com o sistema por meio do navegador.

---

## ✨ Funcionalidades

* Geração de imagens a partir de texto.
* Utilização do modelo **Stable Diffusion v1.5**.
* Otimização automática dos prompts.
* Detecção de categoria do prompt.
* Prompt negativo para reduzir distorções e elementos indesejados.
* Geração de imagens em resolução **512 × 512 pixels**.
* Controle de *seed* para permitir reprodutibilidade.
* Utilização de GPU NVIDIA com CUDA quando disponível.
* Otimizações de memória para execução em GPUs com menor quantidade de VRAM.
* API REST desenvolvida com FastAPI.
* Interface web para interação com o sistema.
* Armazenamento das imagens geradas na pasta `outputs`.

---

## 🏗️ Arquitetura

A arquitetura principal do GeraArteIA pode ser representada da seguinte forma:

```text
┌──────────────────────────────┐
│          Usuário             │
│       Navegador Web          │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│          FastAPI             │
│         web_app.py           │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│         GeraArteIA           │
│      app/generator.py        │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│      Prompt Optimizer        │
│  Otimização e categorização  │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│      Hugging Face Diffusers  │
│     Stable Diffusion v1.5    │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│       PyTorch + CUDA         │
│       GPU NVIDIA             │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│       Imagem PNG gerada      │
│          /outputs            │
└──────────────────────────────┘
```

---

## 📁 Estrutura do Projeto

```text
GeraArteIA/
│
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── generator.py
│   ├── main.py
│   └── prompt_optimizer.py
│
├── huggingface_space/
│   └── main.py
│
├── outputs/
│
├── src/
│
├── tests/
│
├── web/
│   ├── static/
│   └── templates/
│
├── .gitignore
├── INICIAR_GERAARTEIA.bat
├── INSTALAR_GERAARTEIA.bat
├── lista_arquivos.txt
├── README.md
├── requirements.txt
├── requirements_backup.txt
├── teste_modelo.py
└── web_app.py
```

---

## ⚙️ Tecnologias Utilizadas

| Tecnologia            | Utilização                                |
| --------------------- | ----------------------------------------- |
| Python                | Linguagem principal                       |
| PyTorch               | Computação e execução do modelo           |
| CUDA                  | Aceleração por GPU NVIDIA                 |
| Diffusers             | Pipeline de geração por difusão           |
| Transformers          | Componentes de processamento de linguagem |
| Stable Diffusion v1.5 | Modelo de geração de imagens              |
| FastAPI               | API e servidor web                        |
| Uvicorn               | Servidor ASGI                             |
| Jinja2                | Templates HTML                            |
| Pillow                | Manipulação e armazenamento de imagens    |
| NumPy                 | Operações numéricas                       |
| Git                   | Controle de versão                        |
| GitHub                | Hospedagem do código-fonte                |

---

## 📦 Requisitos

Para executar o projeto localmente, recomenda-se:

* Windows, Linux ou ambiente compatível com Python.
* Python **3.11 ou 3.12**.
* Memória RAM suficiente para carregar o modelo.
* Aproximadamente **4 GB ou mais de espaço disponível** para o modelo e dependências.
* GPU NVIDIA com CUDA é recomendada para melhor desempenho.

### GPU

O sistema identifica automaticamente se existe uma GPU CUDA disponível:

```python
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
```

Quando uma GPU compatível está disponível, o processamento pode ser realizado utilizando CUDA.

Caso contrário, o sistema utiliza CPU, embora a geração possa ser consideravelmente mais lenta.

---

# 🚀 Instalação

## 1. Clonar o repositório

```bash
git clone https://github.com/walmunsan-cloud/GeraArteIA.git
```

Entrar na pasta:

```bash
cd GeraArteIA
```

---

## 2. Criar ambiente virtual

```bash
python -m venv .venv
```

Ativar no Windows:

```bash
.venv\Scripts\activate
```

---

## 3. Instalar as dependências

```bash
pip install -r requirements.txt
```

---

# ▶️ Executando o sistema

Após instalar as dependências, execute:

```bash
uvicorn web_app:app --host 127.0.0.1 --port 8000
```

Depois abra o navegador em:

```text
http://127.0.0.1:8000
```

---

# 🪟 Instalação simplificada no Windows

O projeto também possui scripts `.bat` para facilitar a utilização.

### Instalação

Execute:

```text
INSTALAR_GERAARTEIA.bat
```

O instalador:

1. verifica a instalação do Python;
2. cria o ambiente virtual;
3. ativa o ambiente;
4. atualiza o pip;
5. instala as dependências do projeto.

Depois da instalação, execute:

```text
INICIAR_GERAARTEIA.bat
```

O script inicia o servidor e abre o sistema no navegador.

---

# 🖼️ Gerando uma imagem

Na interface web, o usuário informa uma descrição textual.

Exemplo:

```text
uma bela paisagem brasileira ao pôr do sol,
com montanhas, árvores verdes e céu dramático
azul e laranja, fotografia realista
```

O sistema processa o prompt, realiza a otimização automática e envia a solicitação para o modelo Stable Diffusion.

A imagem resultante é armazenada na pasta:

```text
outputs/
```

---

# ⚙️ Configuração do Modelo

As principais configurações utilizadas no projeto são:

```text
Modelo:
stable-diffusion-v1-5/stable-diffusion-v1-5

Resolução:
512 × 512 pixels

Steps:
24

Guidance Scale:
7.0

Seed padrão:
42
```

Esses parâmetros foram definidos buscando equilíbrio entre qualidade da imagem e tempo de processamento.

---

# 🛡️ Prompt Negativo

O sistema utiliza um *negative prompt* para tentar reduzir problemas comuns encontrados em modelos de geração de imagens.

Entre os elementos considerados estão:

```text
blurry
low quality
distorted
deformed
bad anatomy
bad proportions
extra limbs
extra fingers
missing fingers
missing head
missing body parts
cropped
text
watermark
logo
```

Essa estratégia ajuda a reduzir a ocorrência de elementos visualmente indesejados durante a geração.

---

# 🚀 Otimizações

Para reduzir o consumo de memória durante a execução, principalmente em GPUs com menor quantidade de VRAM, o projeto utiliza técnicas como:

```text
Sequential CPU Offload
Attention Slicing
```

Essas técnicas permitem reduzir a pressão de memória da GPU durante a execução do modelo.

---

# 🧪 Validação Experimental

O sistema foi testado em ambiente equipado com GPU NVIDIA Tesla T4.

### Ambiente utilizado

```text
GPU:
NVIDIA Tesla T4

VRAM:
15 GB

PyTorch:
2.10.0+cu128

CUDA:
Disponível

Diffusers:
0.39.0

Transformers:
5.14.1

Accelerate:
1.14.0

Safetensors:
0.8.0
```

Durante o teste completo da classe `GeraArteIA`, o modelo foi carregado com sucesso e uma imagem foi gerada utilizando:

```text
Resolução: 512 × 512
Steps: 24
Guidance Scale: 7.0
Seed: 42
```

Resultado observado no teste:

```text
Modelo carregado com sucesso.

IMAGEM GERADA COM SUCESSO!

Tempo de geração:
aproximadamente 20,88 segundos

Pico de VRAM:
aproximadamente 3,75 GB
```

O teste confirmou o funcionamento integrado entre:

```text
Python
   ↓
PyTorch
   ↓
CUDA
   ↓
Diffusers
   ↓
Stable Diffusion v1.5
   ↓
GeraArteIA
   ↓
Imagem PNG
```

---

# 🔬 Testes

O projeto possui uma estrutura destinada a testes automatizados e testes do modelo.

Também está disponível o arquivo:

```text
teste_modelo.py
```

Ele pode ser utilizado para verificar o carregamento e o funcionamento do modelo.

---

# 🌐 API

A aplicação disponibiliza endpoints através do FastAPI.

### Status

```text
GET /api/status
```

Retorna informações sobre o estado do sistema.

### Geração

```text
POST /api/gerar
```

Recebe um prompt e solicita a geração de uma imagem.

Exemplo de requisição:

```json
{
  "prompt": "uma bela paisagem brasileira ao pôr do sol"
}
```

### Imagem

```text
GET /api/imagem/{nome_arquivo}
```

Permite acessar uma imagem gerada anteriormente.

---

# 📚 Conceitos Demonstrados

O GeraArteIA demonstra na prática conceitos relacionados a:

* Inteligência Artificial Generativa;
* Machine Learning;
* Deep Learning;
* Modelos de difusão;
* Text-to-Image;
* Processamento de linguagem natural;
* Engenharia de prompts;
* Otimização de inferência;
* Computação acelerada por GPU;
* APIs REST;
* Arquitetura de software;
* Integração entre modelos de IA e aplicações web;
* Controle de versão com Git e GitHub.

---

# 🎯 Objetivo Acadêmico

O principal objetivo do projeto é demonstrar como modelos de difusão podem ser integrados a uma aplicação de software para possibilitar a geração de imagens a partir de linguagem natural.

O projeto também busca apresentar uma arquitetura prática que integre:

```text
Interface Web
      +
API
      +
Lógica de aplicação
      +
Engenharia de Prompt
      +
Modelo de IA
      +
GPU/CUDA
```

---

# 👨‍💻 Autor

**Walter Muniz Santos e Luan Jesus Pereira Gomes**

Projeto desenvolvido para conclusão da Pós-Graduação em Engenharia de Software: Automação, Inovação e Inteligência Artificial.

---

# 📌 Repositório

Código-fonte completo do projeto:

https://github.com/walmunsan-cloud/GeraArteIA

---

# 📄 Observações

O modelo **Stable Diffusion v1.5** é um modelo de terceiros utilizado pelo projeto para fins acadêmicos e experimentais.

A primeira execução pode levar mais tempo devido ao carregamento dos componentes necessários do modelo.

A utilização de GPU NVIDIA compatível com CUDA é recomendada para obter melhor desempenho.

---

## 🏁 Status do Projeto

**Concluído para fins de demonstração acadêmica e apresentação do TCC.**

O sistema foi validado com carregamento do modelo, processamento do prompt e geração efetiva de imagens utilizando GPU NVIDIA Tesla T4.
