# Makefile — Atalhos para gerenciar o ambiente do Python Agent
#
# Uso:
#   make up      → copia .env.example se necessário, builda e sobe o container
#   make down    → derruba o container
#   make logs    → mostra logs da API em tempo real
#   make test    → valida os casos mínimos obrigatórios do desafio
#   make shell   → abre bash dentro do container da API

# Detecta docker compose v2 ou v1
DC := $(shell docker compose version > /dev/null 2>&1 && echo "docker compose" || echo "docker-compose")

.PHONY: up down logs test shell

# ── up ────────────────────────────────────────────────────────────
up:
	@[ -f .env ] || (cp .env.example .env && echo "✔ .env criado a partir de .env.example")
	$(DC) up -d --build
	@echo ""
	@echo "✔ Serviços iniciados."
	@echo "  API:     http://localhost:8000"
	@echo "  Swagger: http://localhost:8000/docs"
	@echo "  UI:      http://localhost:8000"
	@echo ""
	@echo "  Ollama esperado em: localhost:11434 (rodando no host)"

# ── down ─────────────────────────────────────────────────────────
down:
	$(DC) down
	@echo "✔ Serviços encerrados."

# ── logs ─────────────────────────────────────────────────────────
logs:
	$(DC) logs -f api

# ── shell ────────────────────────────────────────────────────────
shell:
	$(DC) exec api bash

# ── test ─────────────────────────────────────────────────────────
# Valida os casos mínimos obrigatórios do gabarito do desafio.
test:
	@echo "══ Teste 1: O que é composição? ══"
	@curl -s -X POST http://localhost:8000/messages \
	  -H "Content-Type: application/json" \
	  -d '{"message":"O que é composição?"}' | python3 -m json.tool
	@echo ""

	@echo "══ Teste 2: Qual o papel da Tool de conhecimento? ══"
	@curl -s -X POST http://localhost:8000/messages \
	  -H "Content-Type: application/json" \
	  -d '{"message":"Qual o papel da Tool de conhecimento?"}' | python3 -m json.tool
	@echo ""

	@echo "══ Teste 3: A tool deve responder diretamente ao usuário? ══"
	@curl -s -X POST http://localhost:8000/messages \
	  -H "Content-Type: application/json" \
	  -d '{"message":"A tool deve responder diretamente ao usuário?"}' | python3 -m json.tool
	@echo ""

	@echo "══ Teste 4: Quando usar herança? ══"
	@curl -s -X POST http://localhost:8000/messages \
	  -H "Content-Type: application/json" \
	  -d '{"message":"Quando usar herança?"}' | python3 -m json.tool
	@echo ""

	@echo "══ Teste 5: Qual o papel da orquestração? ══"
	@curl -s -X POST http://localhost:8000/messages \
	  -H "Content-Type: application/json" \
	  -d '{"message":"Qual o papel da orquestração?"}' | python3 -m json.tool
	@echo ""

	@echo "══ Teste 6: Onde colocar regra de negócio? ══"
	@curl -s -X POST http://localhost:8000/messages \
	  -H "Content-Type: application/json" \
	  -d '{"message":"Onde colocar regra de negócio, no endpoint ou no fluxo interno?"}' | python3 -m json.tool
	@echo ""

	@echo "══ Teste 7: Fallback obrigatório ══"
	@curl -s -X POST http://localhost:8000/messages \
	  -H "Content-Type: application/json" \
	  -d '{"message":"Qual a cotação do dólar hoje?"}' | python3 -m json.tool
	@echo ""

	@echo "══ Teste 8: session_id — primeira chamada ══"
	@curl -s -X POST http://localhost:8000/messages \
	  -H "Content-Type: application/json" \
	  -d '{"message":"O que é composição?","session_id":"sessao-teste"}' | python3 -m json.tool
	@echo ""

	@echo "══ Teste 9: session_id — continuidade ══"
	@curl -s -X POST http://localhost:8000/messages \
	  -H "Content-Type: application/json" \
	  -d '{"message":"Pode resumir em uma frase?","session_id":"sessao-teste"}' | python3 -m json.tool
	@echo ""

	@echo "✔ Testes concluídos. Verifique os sources acima."
