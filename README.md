# Python Agent Challenge

Solução simples e documentada para o desafio de agente Python com orquestração de fluxo por IA e base de conhecimento em Markdown.

## Tecnologias

- **Python 3.11+**
- **FastAPI** - framework web com Swagger automático
- **Ollama** - LLM local (modelo `qwen2.5:1.5b`)
- **Requests** - chamadas HTTP

## Diagrama do Projeto

 -> Visão geral

O agente recebe uma pergunta, consulta uma base de conhecimento em Markdown via HTTP, combina o contexto recuperado com a pergunta e envia tudo ao LLM para gerar uma resposta rastreável por fonte.

<img src='diagrama.svg' alt='Diagrama do LLM'>
