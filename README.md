# 🎨 GeraArteIA — Geração de Imagens por Difusão

**GeraArteIA** é uma aplicação de Inteligência Artificial desenvolvida como projeto de **Trabalho de Conclusão de Curso (TCC)**, com o objetivo de demonstrar, de forma prática, o funcionamento da **geração de imagens a partir de descrições textuais utilizando modelos de Difusão**.

O sistema recebe uma descrição fornecida pelo usuário (*prompt*), realiza o processamento do texto e utiliza o modelo **Stable Diffusion v1.5** para produzir uma imagem correspondente à solicitação.

---

## 🚀 Demonstração Online

### ▶️ Acessar o GeraArteIA

**[🌐 ABRIR O GERADOR DE IMAGENS](https://brandon-begin-travelling-mode.trycloudflare.com)**

> ⚠️ **Observação:** o link utiliza um túnel temporário do Cloudflare conectado ao ambiente de execução do projeto. Para a demonstração acadêmica, o ambiente precisa estar ativo.

### Como testar

1. Acesse o link acima.
2. Digite uma descrição no campo de texto.
3. Clique em **Gerar imagem**.
4. Aguarde o processamento do modelo de Inteligência Artificial.
5. A imagem gerada será apresentada na aplicação.

### Exemplo de prompt

```text
Um cavalo marrom correndo em um campo verde ao pôr do sol
```

O sistema utiliza técnicas de otimização do prompt para melhorar a composição da imagem e reduzir problemas anatômicos, especialmente em representações de animais.

---

# 🎓 Sobre o Projeto

O GeraArteIA foi desenvolvido para demonstrar a aplicação prática de **Inteligência Artificial Generativa**, especificamente os modelos baseados em **Difusão**.

Modelos de difusão são técnicas de aprendizado de máquina capazes de gerar imagens a partir de descrições textuais. O processo envolve a transformação progressiva de ruído em uma imagem coerente de acordo com as características descritas pelo usuário.

O projeto apresenta uma implementação prática desse conceito por meio de uma aplicação web acessível pelo navegador.

---

# 🎯 Objetivos

## Objetivo geral

Desenvolver uma aplicação capaz de gerar imagens a partir de descrições textuais utilizando técnicas de **Inteligência Artificial Generativa e modelos de Difusão**.

## Objetivos específicos

* Demonstrar o funcionamento de modelos de geração de imagens por difusão;
* Utilizar o modelo **Stable Diffusion v1.5** para geração de imagens;
* Desenvolver uma interface web para interação com o usuário;
* Implementar processamento e otimização dos prompts;
* Utilizar aceleração por GPU para melhorar o desempenho;
* Disponibilizar uma demonstração acessível por navegador;
* Registrar e organizar o desenvolvimento do projeto utilizando Git e GitHub.

---

# 🧠 Tecnologias utilizadas

| Tecnologia                  | Utilização                                        |
| --------------------------- | ------------------------------------------------- |
| **Python**                  | Linguagem principal do projeto                    |
| **PyTorch**                 | Processamento de Inteligência Artificial          |
| **Diffusers**               | Implementação do modelo de difusão                |
| **Stable Diffusion v1.5**   | Geração das imagens                               |
| **Transformers**            | Processamento dos componentes de linguagem        |
| **FastAPI**                 | Desenvolvimento da API e aplicação web            |
| **Uvicorn**                 | Servidor da aplicação                             |
| **HTML / CSS / JavaScript** | Interface web                                     |
| **Git / GitHub**            | Controle de versão e disponibilização do código   |
| **Google Colab**            | Ambiente de execução com GPU                      |
| **Cloudflare Tunnel**       | Acesso público à aplicação durante a demonstração |

---

# 🏗️ Arquitetura do sistema

O funcionamento geral do GeraArteIA pode ser representado pelo seguinte fluxo:

```text
┌─────────────────────┐
│       Usuário       │
│                     │
│  Digita o prompt    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│    Interface Web    │
│       HTML/CSS/JS   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│       FastAPI       │
│      Web API        │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Otimização do Prompt│
│                     │
│ Processamento textual│
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Stable Diffusion  │
│       v1.5          │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│     GPU / PyTorch   │
│                     │
│ Geração da imagem   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│    Imagem gerada    │
│                     │
│      PNG 512x512    │
└─────────────────────┘
```

---

# ⚙️ Configuração da geração

O projeto utiliza uma configuração voltada para equilibrar **qualidade da imagem e desempenho computacional**.

| Parâmetro        | Configuração          |
| ---------------- | --------------------- |
| Modelo           | Stable Diffusion v1.5 |
| Resolução        | 512 × 512 pixels      |
| Steps            | 24                    |
| Guidance Scale   | 7.0                   |
| Seed padrão      | 42                    |
| Dispositivo      | GPU CUDA              |
| Formato de saída | PNG                   |

O projeto também utiliza técnicas de otimização de memória, incluindo:

* Attention Slicing;
* VAE Slicing;
* VAE Tiling;
* Sequential CPU Offload.

Essas técnicas permitem executar o modelo em GPUs com recursos limitados de memória.

---

# 🐴 Otimização de prompts

Uma das funcionalidades implementadas no projeto é o **otimizador de prompts**.

O sistema identifica determinados tipos de conteúdo e acrescenta características ao prompt para tentar melhorar a composição da imagem.

Para representações de animais, por exemplo, são adicionadas orientações relacionadas a:

```text
full body animal
entire animal fully visible
head clearly visible
complete head and face
four legs clearly visible when applicable
correct animal anatomy
natural body proportions
centered composition
wide shot
medium distance camera
clear space around the animal
no cropping
animal completely inside the frame
```

Essa abordagem foi utilizada para reduzir problemas observados durante os testes, como animais parcialmente cortados ou com anatomia incompleta.

---

# 📁 Estrutura do projeto

```text
GeraArteIA/
│
├── app/
│   ├── config.py
│   ├── generator.py
│   └── prompt_optimizer.py
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
├── web_app.py
│
├── requirements.txt
├── README.md
└── ...
```

---

# 🔄 Funcionamento

O processo de geração ocorre seguindo as seguintes etapas:

### 1. Entrada

O usuário fornece uma descrição textual da imagem desejada.

### 2. Processamento

A aplicação recebe o texto por meio da API desenvolvida em **FastAPI**.

### 3. Otimização

O sistema processa o prompt e acrescenta informações que podem auxiliar na composição da imagem.

### 4. Geração

O prompt processado é enviado ao modelo **Stable Diffusion v1.5**.

### 5. Processamento computacional

O modelo utiliza **PyTorch** e aceleração por **CUDA/GPU** para realizar a geração.

### 6. Resultado

A imagem é salva no formato PNG e disponibilizada ao usuário pela aplicação web.

---

# 💻 Execução local

Para executar o projeto localmente, é necessário ter:

* Python 3.10 ou superior;
* Git;
* GPU compatível com CUDA recomendada;
* Dependências do projeto.

Clone o repositório:

```bash
git clone https://github.com/walmunsan-cloud/GeraArteIA.git
```

Entre no diretório:

```bash
cd GeraArteIA
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Execute a aplicação:

```bash
uvicorn web_app:app --host 0.0.0.0 --port 8000
```

Depois, acesse:

```text
http://127.0.0.1:8000
```

---

# ☁️ Ambiente de demonstração

Durante o desenvolvimento e os testes, o projeto foi executado em ambiente de **Google Colab utilizando GPU NVIDIA Tesla T4**.

Para disponibilizar temporariamente a aplicação para acesso externo durante a apresentação, foi utilizado **Cloudflare Tunnel**.

Essa arquitetura permite que o professor ou avaliador acesse a aplicação pelo navegador sem precisar instalar o projeto localmente.

---

# 🧪 Testes realizados

Durante o desenvolvimento foram realizados testes envolvendo:

* Inicialização da aplicação FastAPI;
* Comunicação entre interface web e API;
* Carregamento do modelo Stable Diffusion;
* Utilização da GPU através do CUDA;
* Geração de imagens em 512 × 512 pixels;
* Testes com diferentes prompts;
* Testes específicos com animais;
* Otimização automática de prompts;
* Geração e armazenamento das imagens;
* Acesso externo através de túnel seguro.

Os testes demonstraram o funcionamento completo do fluxo:

```text
Prompt → API → Otimização → Stable Diffusion → GPU → Imagem
```

---

# 📊 Resultado

O GeraArteIA demonstrou a viabilidade de utilizar modelos de **Inteligência Artificial Generativa baseados em Difusão** para transformar descrições textuais em imagens.

A aplicação também demonstra a integração entre diferentes tecnologias de software:

```text
Interface Web
      ↓
FastAPI
      ↓
Python
      ↓
Diffusers / PyTorch
      ↓
Stable Diffusion
      ↓
GPU CUDA
      ↓
Imagem gerada
```

---

# 🔐 Observações

O projeto foi desenvolvido para fins **acadêmicos e demonstrativos**.

A execução do modelo Stable Diffusion exige recursos computacionais consideráveis. Por esse motivo, o ambiente utilizado para a demonstração emprega GPU.

O link de demonstração disponibilizado acima é temporário e depende da disponibilidade do ambiente de execução.

---

# 👨‍🎓 Projeto acadêmico

**Projeto:** GeraArteIA
**Tema:** Geração de Imagens por Difusão
**Área:** Engenharia de Software, Automação, Inovação e Inteligência Artificial
**Finalidade:** Trabalho de Conclusão de Curso (TCC)

---

# 📌 Repositório

O código-fonte completo do projeto está disponível publicamente no GitHub:

**https://github.com/walmunsan-cloud/GeraArteIA**

### 🌐 Demonstração

**[https://brandon-begin-travelling-mode.trycloudflare.com](https://controlled-appropriations-appointment-cruises.trycloudflare.com)**

---

## 📄 Licença

Este projeto foi desenvolvido para fins acadêmicos e educacionais.


## Desenvolvido por Walter Muniz Santos e Luan Jesus Pereira Gomes 


