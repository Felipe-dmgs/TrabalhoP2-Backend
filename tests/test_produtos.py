import pytest
from fastapi.testclient import TestClient

def test_listar_produtos_banco_vazio(client: TestClient) -> None:
    response = client.get("/produtos")
    assert response.status_code == 200
    assert response.json() == []

def test_criar_produto_e_persistencia(client: TestClient) -> None:
    produto_payload = {"nome": "Teclado Mecânico", "preco": 250.00, "estoque": 10, "ativo": True}
    
    response = client.post("/produtos", json=produto_payload)
    assert response.status_code == 201
    
    dados_retornados = response.json()
    assert "id" in dados_retornados
    assert dados_retornados["nome"] == produto_payload["nome"]
    assert dados_retornados["preco"] == produto_payload["preco"]


def test_criar_produto_e_verificar_na_listagem(client: TestClient) -> None:
    produto_payload = {"nome": "Mouse Gamer", "preco": 120.00, "estoque": 15, "ativo": True}
    client.post("/produtos", json=produto_payload)
    
    response = client.get("/produtos")
    assert response.status_code == 200
    
    lista_produtos = response.json()
    assert len(lista_produtos) == 1
    assert lista_produtos[0]["nome"] == "Mouse Gamer"

def test_buscar_produto_id(client: TestClient) -> None:
    produto_payload = {"nome": "Monitor 24", "preco": 850.00, "estoque": 5, "ativo": True}
    post_response = client.post("/produtos", json=produto_payload)
    produto_id = post_response.json()["id"]
    
    response = client.get(f"/produtos/{produto_id}")
    assert response.status_code == 200
    assert response.json()["nome"] == "Monitor 24"

def test_buscar_produto_id_inexistente(client: TestClient) -> None:
    response = client.get("/produtos/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Produto não encontrado"

def test_deletar_produto(client: TestClient) -> None:
    produto_payload = {"nome": "Fone Ouvido", "preco": 50.00, "estoque": 30, "ativo": True}
    post_response = client.post("/produtos", json=produto_payload)
    produto_id = post_response.json()["id"]
    
    response = client.delete(f"/produtos/{produto_id}")
    
    assert response.status_code == 204  
    assert response.content == b""     

def test_deletar_produto_e_confirmar_com_get(client: TestClient) -> None:
    produto_payload = {"nome": "Webcam HD", "preco": 180.00, "estoque": 8, "ativo": True}
    post_response = client.post("/produtos", json=produto_payload)
    produto_id = post_response.json()["id"]
    
    client.delete(f"/produtos/{produto_id}")
    
    get_response = client.get(f"/produtos/{produto_id}")
    assert get_response.status_code == 404

def test_deletar_produto_inexistente(client: TestClient) -> None:
    response = client.delete("/produtos/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Produto não encontrado"


@pytest.mark.parametrize(
    "payload_invalido",
    [
        {"nome": "", "preco": 50.0, "estoque": 10},
        {"nome": "Cabo HDMI", "preco": 0.0, "estoque": 10},
        {"nome": "Cabo HDMI", "preco": -5.5, "estoque": 10},
        {"nome": "Cabo HDMI", "preco": 50.0, "estoque": -1},
        {"preco": 50.0, "estoque": 10}
    ]
)
def test_criar_produto_payload_invalido(client: TestClient, payload_invalido: dict) -> None:
    response = client.post("/produtos", json=payload_invalido)
    assert response.status_code == 422


def test_validar_banco_isolado_parte_1(client: TestClient) -> None:
    produto_payload = {"nome": "Produto Isolamento", "preco": 10.0, "estoque": 1, "ativo": True}
    client.post("/produtos", json=produto_payload)
    
    response = client.get("/produtos")
    assert len(response.json()) == 1

def test_validar_banco_isolado_parte_2(client: TestClient) -> None:
    response = client.get("/produtos")
    assert response.status_code == 200
    assert response.json() == []


def test_atualizar_produto(client: TestClient) -> None:

    produto_payload = {"nome": "Teclado Antigo", "preco": 100.00, "estoque": 5, "ativo": True}
    post_response = client.post("/produtos", json=produto_payload)
    produto_id = post_response.json()["id"]

    payload_atualizado = {"nome": "Teclado Mecânico RGB", "preco": 250.00, "estoque": 15, "ativo": True}
    

    response = client.put(f"/produtos/{produto_id}", json=payload_atualizado)
    
    assert response.status_code == 200
    dados_retornados = response.json()
    assert dados_retornados["nome"] == "Teclado Mecânico RGB"
    assert dados_retornados["preco"] == 250.00
    assert dados_retornados["estoque"] == 15