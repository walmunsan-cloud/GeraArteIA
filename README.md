# 🎨 GeraArteIA — Geração de Imagens por Difusão

![Status](https://img.shields.io/badge/status-funcionando-success)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![Stable Diffusion](https://img.shields.io/badge/Stable%20Diffusion-v1.5-purple)
![GPU](https://img.shields.io/badge/GPU-NVIDIA%20Tesla%20T4-green)
![Modal](https://img.shields.io/badge/Hospedagem-Modal-orange)

## 🌐 Acesse o GeraArteIA

### 🚀 GERADOR DE IMAGENS ONLINE

**[👉 CLIQUE AQUI PARA ACESSAR O GERADOR](https://walmunsan-cloud--geraarteia-web.modal.run)**

> O sistema está hospedado no Modal e pode ser acessado diretamente pelo navegador, sem necessidade de instalar Python, abrir Google Colab ou executar programas localmente.

---

# 🎓 Sobre o projeto

O **GeraArteIA** é uma aplicação de Inteligência Artificial Generativa desenvolvida como projeto de **Trabalho de Conclusão de Curso (TCC)**, com foco na **Geração de Imagens por Difusão**.

O sistema permite que o usuário forneça uma descrição textual (*prompt*) e, a partir dessa descrição, utilize o modelo **Stable Diffusion v1.5** para gerar uma imagem correspondente.

O projeto demonstra, de forma prática, a integração entre:

* Inteligência Artificial Generativa;
* Modelos de Difusão;
* Processamento de linguagem;
* Redes neurais;
* Python;
* PyTorch;
* CUDA;
* GPU;
* API web;
* Interface web;
* Computação em nuvem.

---

# 👨‍🎓 Autores

**Walter Muniz Santos**

**Luan Jesus**

Projeto desenvolvido para fins acadêmicos.

---

# 🎯 Objetivo geral

Desenvolver uma aplicação web capaz de gerar imagens a partir de descrições textuais utilizando técnicas de **Inteligência Artificial Generativa e modelos de Difusão**.

---

# 🎯 Objetivos específicos

* Estudar o funcionamento dos modelos de geração de imagens por difusão;
* Utilizar o modelo Stable Diffusion v1.5;
* Desenvolver uma aplicação web para geração de imagens;
* Permitir a entrada de prompts pelo usuário;
* Processar os prompts antes da geração;
* Utilizar GPU para aceleração do processamento;
* Integrar Python, PyTorch e Diffusers;
* Disponibilizar o sistema pela internet;
* Avaliar os resultados obtidos durante os testes;
* Documentar todo o processo de desenvolvimento.

---

# 🧠 O que são modelos de Difusão?

Os modelos de difusão são modelos de Inteligência Artificial capazes de gerar imagens a partir de informações fornecidas pelo usuário.

De maneira simplificada, o processo parte de uma representação baseada em ruído e realiza sucessivas etapas de transformação até produzir uma imagem coerente com a descrição fornecida.

No GeraArteIA, o usuário informa um texto e o modelo **Stable Diffusion v1.5** interpreta essa descrição para produzir a imagem.

Fluxo simplificado:

```text
Descrição textual
       ↓
     Prompt
       ↓
Processamento
       ↓
Stable Diffusion v1.5
       ↓
PyTorch / CUDA
       ↓
GPU NVIDIA Tesla T4
       ↓
Imagem gerada
```

---

# 🏗️ Arquitetura final

A versão final do projeto utiliza uma arquitetura web baseada em **FastAPI**, sem depender do Gradio para a interface.

```text
┌──────────────────────────┐
│          USUÁRIO         │
│                          │
│      Digita o Prompt     │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│      INTERFACE WEB       │
│      HTML / CSS / JS     │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│         FASTAPI          │
│          API             │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│       PYTHON             │
│                          │
│ Processamento do Prompt  │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│   DIFFUSERS              │
│                          │
│ Stable Diffusion v1.5    │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│        PYTORCH           │
│          CUDA            │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│     NVIDIA TESLA T4      │
│                          │
│ Processamento da IA      │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│      IMAGEM PNG          │
│        512 × 512         │
└──────────────────────────┘
```

---

# 🛠️ Tecnologias utilizadas

| Tecnologia                | Utilização                                  |
| ------------------------- | ------------------------------------------- |
| **Python 3.11**           | Linguagem principal                         |
| **PyTorch 2.5.1**         | Computação e execução do modelo             |
| **Torchvision 0.20.1**    | Processamento relacionado a imagens         |
| **Diffusers 0.31.0**      | Implementação do modelo de difusão          |
| **Transformers 4.46.3**   | Componentes de processamento de linguagem   |
| **Accelerate 1.1.1**      | Aceleração e gerenciamento do processamento |
| **Safetensors 0.4.5**     | Armazenamento seguro dos pesos do modelo    |
| **FastAPI**               | API e servidor web                          |
| **HTML**                  | Estrutura da interface                      |
| **CSS**                   | Estilização da interface                    |
| **JavaScript**            | Interação com a aplicação                   |
| **Stable Diffusion v1.5** | Geração das imagens                         |
| **CUDA**                  | Aceleração utilizando GPU                   |
| **NVIDIA Tesla T4**       | Processamento da IA                         |
| **Modal**                 | Hospedagem e execução em nuvem              |
| **Git / GitHub**          | Controle de versão e documentação           |

---

# ⚙️ Configuração final da geração

A configuração utilizada na versão final foi:

| Parâmetro      | Valor                 |
| -------------- | --------------------- |
| Modelo         | Stable Diffusion v1.5 |
| Resolução      | 512 × 512 pixels      |
| Steps          | 24                    |
| Guidance Scale | 7.0                   |
| Seed padrão    | 42                    |
| Precisão       | Float16               |
| Formato        | PNG                   |
| GPU            | NVIDIA Tesla T4       |
| Framework      | PyTorch               |
| Aceleração     | CUDA                  |

---

# 🧩 Otimização da geração

Durante o desenvolvimento foram utilizadas técnicas de otimização para melhorar o desempenho e o consumo de memória.

Entre os recursos utilizados estão:

* Attention Slicing;
* VAE Slicing;
* VAE Tiling;
* otimizações do PyTorch;
* execução em precisão Float16;
* utilização de GPU CUDA.

Essas técnicas foram importantes principalmente durante os testes em ambientes com recursos computacionais limitados.

---

# ✍️ Processamento dos prompts

O sistema trabalha com uma descrição textual fornecida pelo usuário.

O prompt pode ser processado antes de ser enviado ao modelo, permitindo adicionar informações relacionadas à composição da imagem.

Durante os testes foram observados problemas como:

* objetos parcialmente cortados;
* animais incompletos;
* problemas de enquadramento;
* anatomia inadequada;
* partes do corpo fora da imagem.

Para reduzir esses problemas, foram utilizadas orientações adicionais relacionadas à composição, enquadramento e visualização completa do objeto.

Exemplo:

```text
full body animal
entire animal fully visible
head clearly visible
complete head and face
correct animal anatomy
natural body proportions
centered composition
wide shot
clear space around the subject
no cropping
subject completely inside the frame
```

---

# 🔄 Evolução do projeto

O GeraArteIA passou por diferentes etapas durante seu desenvolvimento.

## 1. Execução local

A primeira etapa foi realizada em computador local utilizando Python e uma GPU NVIDIA GTX 960.

Nessa etapa foram identificadas limitações de memória da GPU, principalmente para geração de imagens em resoluções maiores.

---

## 2. Google Colab

Posteriormente, o projeto foi executado no Google Colab utilizando GPU NVIDIA Tesla T4.

A utilização da T4 permitiu aumentar a resolução e melhorar significativamente a qualidade das imagens.

---

## 3. Kaggle

Também foram realizados testes utilizando ambientes com GPU NVIDIA Tesla T4 disponibilizados pelo Kaggle.

Essa etapa permitiu avaliar diferentes ambientes de execução em nuvem.

---

## 4. Cloudflare Tunnel

Durante uma das etapas de demonstração, foi utilizado o Cloudflare Tunnel para disponibilizar temporariamente a aplicação local/Colab pela internet.

Essa solução funcionou para testes, porém dependia da sessão de execução permanecer ativa.

---

## 5. Gradio

O Gradio também foi utilizado durante o desenvolvimento para criar uma interface de demonstração.

Após os testes, optou-se por retirar o Gradio da versão final devido a problemas de compatibilidade encontrados no ambiente de hospedagem.

---

## 6. Modal — versão final

Na etapa final, o projeto foi migrado para o **Modal**, utilizando uma GPU NVIDIA Tesla T4.

A aplicação final utiliza:

```text
Modal
   ↓
FastAPI
   ↓
Python
   ↓
Diffusers
   ↓
Stable Diffusion v1.5
   ↓
PyTorch
   ↓
CUDA
   ↓
NVIDIA Tesla T4
```

Essa arquitetura permitiu disponibilizar o sistema por meio de um endereço público acessível pelo navegador.

---

# ☁️ Hospedagem final

A versão final do GeraArteIA está hospedada no **Modal**.

O usuário não precisa instalar o projeto ou abrir o Google Colab para utilizar a demonstração.

### Link da aplicação:

**https://walmunsan-cloud--geraarteia-web.modal.run**

### Repositório:

**https://github.com/walmunsan-cloud/GeraArteIA**

---

# 🖥️ Como utilizar

Para utilizar o GeraArteIA:

### 1. Acesse:

https://walmunsan-cloud--geraarteia-web.modal.run

### 2. Digite uma descrição

Exemplo:

```text
Um cavalo marrom correndo em um campo verde durante o pôr do sol
```

### 3. Informe a seed

A seed padrão é:

```text
42
```

Também é possível utilizar outra seed para produzir uma variação da geração.

### 4. Clique em gerar

O sistema enviará o prompt para a API.

### 5. Aguarde o processamento

O modelo Stable Diffusion realizará a geração utilizando a GPU NVIDIA Tesla T4.

### 6. Visualize a imagem

A imagem será apresentada diretamente na página.

---

# 🔌 API

A aplicação final disponibiliza endpoints HTTP.

## Página principal

```text
GET /
```

Retorna a interface web do GeraArteIA.

---

## Verificação de funcionamento

```text
GET /health
```

Utilizado para verificar o estado da aplicação.

Exemplo de resposta:

```json
{
  "status": "online",
  "app": "GeraArteIA"
}
```

---

## Geração de imagem

```text
POST /generate
```

Recebe o prompt e os parâmetros da geração.

Exemplo conceitual:

```json
{
  "prompt": "Um cavalo marrom correndo em um campo verde",
  "seed": 42
}
```

A API retorna a imagem gerada em formato PNG codificado para apresentação na interface web.

---

# 🧪 Testes realizados

Durante o desenvolvimento foram realizados testes de:

* carregamento do modelo;
* funcionamento da API;
* processamento dos prompts;
* utilização da GPU;
* geração de imagens;
* alteração de seeds;
* resolução 512 × 512;
* diferentes quantidades de steps;
* diferentes descrições;
* geração de animais;
* geração de veículos;
* geração de paisagens;
* funcionamento da interface web;
* acesso público pela internet.

Os testes confirmaram o funcionamento da versão final.

---

# 📊 Resultado final

A versão final do GeraArteIA conseguiu realizar o fluxo completo de geração:

```text
Usuário
   ↓
Prompt
   ↓
Interface Web
   ↓
FastAPI
   ↓
Processamento do Prompt
   ↓
Stable Diffusion v1.5
   ↓
PyTorch
   ↓
CUDA
   ↓
NVIDIA Tesla T4
   ↓
Imagem 512 × 512
   ↓
Usuário
```

O projeto demonstrou a viabilidade de integrar um modelo de Inteligência Artificial Generativa a uma aplicação web acessível diretamente pelo navegador.

---

# 🎓 Conclusão

O desenvolvimento do GeraArteIA possibilitou analisar, na prática, o funcionamento de modelos de **Geração de Imagens por Difusão**.

Durante o projeto foram avaliadas diferentes arquiteturas e ambientes de execução, desde a utilização de hardware local até ambientes de computação em nuvem.

A utilização da GPU NVIDIA Tesla T4 proporcionou recursos computacionais adequados para a execução do Stable Diffusion v1.5 em resolução de 512 × 512 pixels.

A versão final, hospedada no Modal, apresenta uma arquitetura composta por **FastAPI, Python, Diffusers, PyTorch, CUDA e Stable Diffusion**, disponibilizando uma interface web para interação com o usuário.

O projeto também demonstrou a importância da escolha da infraestrutura de computação para aplicações de Inteligência Artificial Generativa, especialmente em modelos que demandam elevada capacidade de processamento gráfico.

---

# 📚 Finalidade acadêmica

Este projeto foi desenvolvido como parte do **Trabalho de Conclusão de Curso (TCC)** da pós-graduação em:

**Engenharia de Software: Automação, Inovação e Inteligência Artificial**

### Tema

**Geração de Imagens por Difusão**

### Projeto

**GeraArteIA**

### Autores

**Walter Muniz Santos e Luan Jesus**

---

# 📁 Estrutura principal

```text
GeraArteIA/
│
├── app/
├── src/
├── tests/
├── web/
├── huggingface_space/
├── modal_app.py
├── requirements.txt
├── README.md
└── TCC_GERAARTEIA.md
```

A implementação final de hospedagem utiliza o arquivo:

```text
modal_app.py
```

---

# ⚠️ Observação sobre custos

A execução de modelos de Inteligência Artificial utilizando GPU em nuvem pode gerar consumo de recursos computacionais.

O projeto foi configurado para fins acadêmicos e de demonstração.

O tempo de execução da GPU deve ser considerado durante a utilização da aplicação.

---

# 🔗 Links

### 🌐 Aplicação online

**https://walmunsan-cloud--geraarteia-web.modal.run**

### 💻 GitHub

**https://github.com/walmunsan-cloud/GeraArteIA**

---

# 👨‍💻 Desenvolvedores

**Walter Muniz Santos**

**Luan Jesus Pereira Gomes**

🎨 **GeraArteIA — Geração de Imagens por Difusão**
