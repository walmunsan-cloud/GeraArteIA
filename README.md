# 🎨 GeraArteIA

## Sistema de Geração de Imagens por Inteligência Artificial

O **GeraArteIA** é um projeto acadêmico desenvolvido para demonstrar a utilização de **Inteligência Artificial Generativa** e **modelos de difusão** na criação de imagens a partir de descrições em linguagem natural.

O usuário descreve a imagem desejada e o sistema utiliza um modelo de Inteligência Artificial para interpretar o texto e gerar uma nova imagem.

---

# 🚀 Demonstração Online

## 🌐 [ABRIR O GERADOR DE IMAGENS](https://controlled-appropriations-appointment-cruises.trycloudflare.com)

### Como testar

1. Acesse o link acima.
2. Digite uma descrição da imagem desejada.
3. Clique em **✨ Gerar imagem**.
4. Aguarde o processamento da Inteligência Artificial.
5. A imagem será exibida automaticamente na tela.

### Exemplo de prompt

> Um cavalo marrom correndo em um campo verde ao pôr do sol, fotografia realista.

---

> ⚠️ **Observação sobre a demonstração:**
> A demonstração online utiliza um ambiente temporário de execução. Portanto, o endereço pode depender da disponibilidade da sessão de demonstração.

---

# 🧠 Tecnologias Utilizadas

O projeto foi desenvolvido utilizando:

* Python
* FastAPI
* Uvicorn
* PyTorch
* Hugging Face Diffusers
* Transformers
* Stable Diffusion
* CUDA
* NVIDIA GPU
* HTML
* CSS
* JavaScript
* GitHub
* Google Colab
* Cloudflare Tunnel

---

# 🏗️ Arquitetura do Sistema

O funcionamento do sistema ocorre conforme o fluxo abaixo:

```text
Usuário
   │
   ▼
Interface Web
   │
   ▼
FastAPI
   │
   ▼
API /api/gerar
   │
   ▼
Otimização do Prompt
   │
   ▼
Stable Diffusion
   │
   ▼
GPU / CUDA
   │
   ▼
Geração da Imagem
   │
   ▼
API /api/imagem
   │
   ▼
Imagem exibida ao usuário
```

---

# ✨ Funcionalidades

## 🎨 Geração de imagens

O usuário pode criar imagens utilizando descrições em linguagem natural.

Exemplo:

```text
Um carro esportivo vermelho em uma pista de corrida moderna ao pôr do sol, fotografia realista.
```

---

## 🧠 Otimização automática de prompts

O sistema identifica categorias presentes no texto informado pelo usuário e adiciona instruções para melhorar a geração.

Entre as categorias identificadas estão:

* 🐴 Animais
* 👤 Pessoas
* 🚗 Veículos
* 🌄 Paisagens
* 📦 Objetos

---

## 🐴 Melhoria de enquadramento de animais

Para prompts contendo animais, o sistema aplica instruções adicionais para melhorar o enquadramento e reduzir problemas como cortes na imagem.

Exemplos de otimização:

```text
full body animal
entire animal fully visible
head clearly visible
complete head and face
correct animal anatomy
natural body proportions
centered composition
wide shot
clear space around the animal
no cropping
animal completely inside the frame
```

---

## 🚗 Melhoria de enquadramento de veículos

Para imagens de veículos, o sistema utiliza instruções adicionais para melhorar:

* enquadramento;
* proporções;
* visibilidade completa do veículo;
* composição da cena;
* visualização do ambiente.

---

## ⚙️ API REST

O backend utiliza FastAPI para comunicação entre a interface e o sistema de geração.

### Status do sistema

```text
GET /api/status
```

Exemplo de resposta:

```json
{
  "sistema": "GeraArteIA",
  "modelo": "stable-diffusion-v1-5/stable-diffusion-v1-5",
  "modelo_carregado": true
}
```

---

### Gerar imagem

```text
POST /api/gerar
```

Exemplo de requisição:

```json
{
  "prompt": "Um cavalo marrom correndo em um campo verde ao pôr do sol, fotografia realista."
}
```

Exemplo de resposta:

```json
{
  "sucesso": true,
  "arquivo": "imagem_20260903.png",
  "imagem": "/api/imagem/imagem_20260903.png"
}
```

---

# 🖥️ Interface Web

A interface permite:

* inserir o prompt;
* iniciar a geração;
* acompanhar o processamento;
* receber mensagens de erro mais claras;
* visualizar automaticamente a imagem gerada.

A comunicação com a API utiliza JavaScript e requisições assíncronas.

O sistema também realiza validação da resposta recebida da API, diferenciando corretamente respostas JSON de respostas inesperadas em HTML.

---

# 🧪 Modelo de Inteligência Artificial

O projeto utiliza o modelo:

```text
Stable Diffusion v1.5
```

O modelo é utilizado para gerar imagens a partir de descrições textuais.

Durante a demonstração do projeto, a geração foi executada utilizando aceleração por GPU NVIDIA e CUDA.

---

# 📁 Estrutura do Projeto

```text
GeraArteIA
│
├── app
│   ├── generator.py
│   └── prompt_optimizer.py
│
├── web
│   └── templates
│       └── index.html
│
├── huggingface_space
│
├── web_app.py
│
├── requirements.txt
│
└── README.md
```

---

# ▶️ Execução Local

## 1. Clonar o repositório

```bash
git clone https://github.com/walmunsan-cloud/GeraArteIA.git
```

## 2. Acessar o diretório

```bash
cd GeraArteIA
```

## 3. Instalar as dependências

```bash
pip install -r requirements.txt
```

## 4. Iniciar o servidor

```bash
uvicorn web_app:app --host 0.0.0.0 --port 8000
```

## 5. Abrir no navegador

```text
http://localhost:8000
```

---

# 🔄 Fluxo de Geração

```text
Prompt do usuário
        │
        ▼
Detecção de categoria
        │
        ▼
Otimização do prompt
        │
        ▼
Stable Diffusion
        │
        ▼
Processamento pela GPU
        │
        ▼
Imagem PNG gerada
        │
        ▼
Resposta JSON da API
        │
        ▼
Exibição automática no navegador
```

---

# 🎓 Contexto Acadêmico

O **GeraArteIA** foi desenvolvido como projeto acadêmico na área de:

**Engenharia de Software, Automação, Inovação e Inteligência Artificial**

O projeto demonstra, na prática:

* Inteligência Artificial Generativa;
* geração de imagens por difusão;
* integração entre frontend e backend;
* desenvolvimento de APIs;
* processamento utilizando GPU;
* otimização de prompts;
* utilização de modelos de Machine Learning.

---

# 👨‍💻 Desenvolvedores

**Walter Muniz**

**Luan Jesus**

---

# 📌 Repositório

🌐 [GitHub - GeraArteIA](https://github.com/walmunsan-cloud/GeraArteIA)

---

# 🎨 Demonstração

## 👉 [CLIQUE AQUI PARA ABRIR O GERAARTEIA](https://controlled-appropriations-appointment-cruises.trycloudflare.com)

Digite uma descrição, clique em **✨ Gerar imagem** e aguarde a Inteligência Artificial criar a imagem.

---

<div align="center">

### 🎨 GeraArteIA

**Geração de Imagens por Inteligência Artificial**

Projeto acadêmico desenvolvido utilizando Inteligência Artificial Generativa e modelos de difusão.

</div>
