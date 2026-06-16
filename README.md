# Trabalho P2 - API de Produtos (FastAPI & SQLAlchemy)

Api desenvolvida para o gerenciamento de produtos de uma pequena loja, desenvolvido com SQLAlchemy, fastapi, dockerizando o banco e a api.

## 1. Instruções para Execução da Aplicação

Tanto a API quanto o banco de dados foram containerizados para rodar de forma integrada através do Docker Compose.

1. Certifique-se de que o Docker Desktop esteja rodando em sua máquina.
2. No terminal, navegue até a raiz do projeto.
3. Execute o comando abaixo para construir a imagem da API e subir os serviços em segundo plano:
   ```bash
      docker compose up -d --build
4. Após isso para rodar os testes só executar o comando abaixo:
   ```bash
      docker compose exec web pytest --cov=main -v --cov-report=term-missing