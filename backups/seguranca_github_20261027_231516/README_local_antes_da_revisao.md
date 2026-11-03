# GeraArteIA — Geração de Imagens por Difusão

Aplicação web acadêmica para geração de imagens a partir de descrições textuais, utilizando Stable Diffusion v1.5.

## Acesso online

O projeto possui um endereço de implantação no Modal:

https://walmunsan-cloud--geraarteia-web.modal.run

A disponibilidade do endereço deve ser confirmada acessando o link.

## Sobre o projeto

O GeraArteIA demonstra a aplicação prática de Inteligência Artificial Generativa e modelos de difusão. O usuário fornece um prompt, que é otimizado antes de ser enviado ao modelo de geração de imagens.

### Funcionalidades

- Geração de imagens com Stable Diffusion.
- Otimização de prompts e exemplos selecionáveis.
- Configuração de passos e resolução.
- Download das imagens geradas.
- Avaliação de 0 a 10 e satisfação percentual.
- Dashboard com estatísticas e distribuição da satisfação.
- Histórico de gerações.
- Fila de revisão de resultados com baixa avaliação.
- Persistência dos registros em banco de dados SQLite.

## Tecnologias

- Python
- FastAPI
- Uvicorn
- PyTorch
- Hugging Face Diffusers
- Stable Diffusion v1.5
- HTML e CSS
- SQLite

As versões e os requisitos de hardware dependem do ambiente de execução e das dependências instaladas.

## Autores

- Walter Muniz Santos
- Luan Jesus Pereira Gomes

Projeto desenvolvido para fins acadêmicos, com foco em geração de imagens por difusão.

## Executar localmente no Windows

1. Abra o PowerShell na pasta do projeto.
2. Confirme que o ambiente virtual `.venv` existe e contém as dependências.
3. Execute:

```powershell
.\iniciar.ps1
```

4. Abra no navegador:

http://127.0.0.1:8000

Para encerrar o servidor, pressione `Ctrl+C` no terminal.

Caso as dependências ainda não estejam instaladas, consulte `requirements.txt` e as instruções específicas do ambiente antes de instalar ou atualizar pacotes.

## Verificação de saúde

Com o servidor em execução, acesse:

http://127.0.0.1:8000/health

## Estrutura principal

- `web_app.py` — rotas e interface web.
- `app/` — módulos de geração, configuração, otimização e banco de dados.
- `tests/` — testes automatizados.
- `outputs/` — imagens geradas.
- `geraarteia.db` — banco de dados local.
- `iniciar.ps1` — inicialização local.

## Observações

A primeira geração pode demorar devido ao carregamento do modelo. O consumo de memória varia conforme o hardware, a resolução e as configurações utilizadas.

O histórico e as imagens locais devem ser preservados ao atualizar o projeto.
