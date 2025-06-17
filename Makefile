.PHONY: up otimizacao

otimizacao:
	@if [ -z "$$(sudo docker images -q smartapsus/otimizacao:0.1)" ]; then \
		echo "Imagem smartapsus/otimizacao:0.1 não encontrada. Gerando..."; \
		sudo docker build -t smartapsus/otimizacao:0.1 -f servico_otimizacao/Dockerfile_otimizacao servico_otimizacao; \
	else \
		echo "Imagem smartapsus/otimizacao:0.1 já existe."; \
	fi

up: otimizacao
	sudo docker compose up --build
