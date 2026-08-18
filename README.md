# GeraArteIA

Sistema de geração de imagens utilizando Inteligência Artificial Generativa e modelos de difusão.

Projeto desenvolvido como parte da Pós-Graduação em Engenharia de Software, com foco em Automação, Inovação e Inteligência Artificial.

---

## Sobre o projeto

O GeraArteIA é uma aplicação desenvolvida para estudar e demonstrar o processo de geração de imagens a partir de descrições textuais utilizando modelos de Inteligência Artificial baseados em difusão.

O sistema recebe um prompt textual do usuário e utiliza o modelo Stable Diffusion para produzir uma imagem correspondente à descrição fornecida.

O projeto também busca demonstrar, na prática, conceitos relacionados a:

- Inteligência Artificial Generativa;
- Deep Learning;
- Modelos de difusão;
- Processamento de linguagem natural;
- Geração de imagens;
- Otimização de modelos de IA;
- Uso de GPU e CUDA;
- Desenvolvimento de software.

---

## Objetivo

Desenvolver uma aplicação capaz de gerar imagens a partir de comandos textuais utilizando um modelo de difusão executado localmente.

Além da geração das imagens, o projeto tem como objetivo analisar os impactos de diferentes parâmetros na qualidade do resultado, considerando as limitações de hardware disponíveis.

---

## Tecnologias utilizadas

- Python
- PyTorch
- Hugging Face Diffusers
- Hugging Face Transformers
- Stable Diffusion v1.5
- CUDA
- Pillow
- HTML
- CSS
- JavaScript
- Git
- GitHub

---

## Arquitetura do projeto

```text
GeraArteIA/
│
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── generator.py
│   └── main.py
│
├── src/
│   ├── __init__.py
│   ├── generator.py
│   ├── model.py
│   └── utils.py
│
├── tests/
│   └── test_generator.py
│
├── web/
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   └── templates/
│       └── index.html
│
├── outputs/
│
├── .gitignore
├── requirements.txt
├── app.py
└── README.md