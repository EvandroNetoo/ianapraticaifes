import pytest
from decimal import Decimal
from app.models import ProposalStatus
from app.services.proposals import ProposalService


def test_customer_creation_and_listing(client):
    # Cadastrar cliente via form
    response = client.post(
        "/clientes",
        data={"name": "Empresa Alfa", "company": "Alfa Holding", "email": "alfa@exemplo.com"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "Empresa Alfa" in response.text
    assert "Alfa Holding" in response.text


def test_customer_creation_validation(client):
    # Nome vazio deve falhar
    response = client.post(
        "/clientes",
        data={"name": "   ", "company": "Empresa", "email": "teste@exemplo.com"},
    )
    assert response.status_code == 400
    assert "O nome do cliente é obrigatório" in response.text


def test_full_proposal_lifecycle_and_public_link(client, db_session, sample_customer):
    # 1. Criar proposta via form
    create_resp = client.post(
        "/propostas",
        data={
            "customer_id": str(sample_customer.id),
            "title": "Projeto Piloto de Inteligência Artificial",
            "discount_percent": "10.00",
            "item_description": ["Fase 1: Diagnóstico", "Fase 2: Implementação"],
            "item_quantity": ["1", "2"],
            "item_unit_price": ["1000.00", "2000.00"],
        },
        follow_redirects=True,
    )
    assert create_resp.status_code == 200
    assert "Projeto Piloto de Inteligência Artificial" in create_resp.text
    assert "rascunho" in create_resp.text

    # Recupera proposta do banco
    proposals = ProposalService.list_proposals(db_session)
    assert len(proposals) == 1
    prop = proposals[0]

    # Verifica cálculos: (1*1000) + (2*2000) = 5000; desc 10% = 500; total = 4500
    assert prop.subtotal == Decimal("5000.00")
    assert prop.discount_amount == Decimal("500.00")
    assert prop.total == Decimal("4500.00")

    # 2. Enviar proposta para o cliente
    send_resp = client.post(f"/propostas/{prop.id}/enviar", follow_redirects=True)
    assert send_resp.status_code == 200
    assert "enviada" in send_resp.text

    db_session.refresh(prop)
    assert prop.status == ProposalStatus.ENVIADA.value
    assert prop.public_token is not None
    token = prop.public_token

    # 3. Acessar link público com token correto
    pub_resp = client.get(f"/p/{token}")
    assert pub_resp.status_code == 200
    html = pub_resp.text

    # Verifica dados necessários
    assert "Projeto Piloto de Inteligência Artificial" in html
    assert sample_customer.name in html
    assert "Fase 1: Diagnóstico" in html
    assert "Fase 2: Implementação" in html
    assert "R$ 5.000,00" in html  # Subtotal
    assert "R$ 500,00" in html    # Desconto
    assert "R$ 4.500,00" in html  # Total
    assert "Aceitar Proposta" in html
    assert "Recusar Proposta" in html

    # Verifica minimização de dados e segurança (não deve vazar links admin ou ids do banco no corpo público)
    assert 'href="/clientes"' not in html
    assert 'href="/propostas/nova"' not in html
    assert 'class="navbar"' not in html
    assert f"#{prop.id}" not in html

    # 4. Aceitar a proposta pelo link público
    accept_resp = client.post(f"/p/{token}/aceitar", follow_redirects=True)
    assert accept_resp.status_code == 200
    assert "Proposta Aceita!" in accept_resp.text
    assert "Aceitar Proposta" not in accept_resp.text  # Botões de decisão não devem mais aparecer

    db_session.refresh(prop)
    assert prop.status == ProposalStatus.ACEITA.value
    assert prop.decided_at is not None

    # 5. Idempotência: clicar novamente em aceitar
    repeat_resp = client.post(f"/p/{token}/aceitar", follow_redirects=True)
    assert repeat_resp.status_code == 200
    assert "Proposta Aceita!" in repeat_resp.text

    # 6. Tentativa de recusar proposta que já foi aceita -> deve ser rejeitada
    refuse_after_accept = client.post(f"/p/{token}/recusar")
    assert refuse_after_accept.status_code == 400
    assert "já foi aceita" in refuse_after_accept.text

    # 7. No painel administrativo, o histórico reflete status 'aceita'
    list_resp = client.get("/propostas")
    assert list_resp.status_code == 200
    assert "aceita" in list_resp.text


def test_public_link_non_existent_token(client):
    response = client.get("/p/token-inexistente-123456789")
    assert response.status_code == 404


def test_public_refusal_flow(client, db_session, sample_customer):
    prop = ProposalService.create_proposal(
        db=db_session,
        customer_id=sample_customer.id,
        title="Proposta Para Recusa",
        items_data=[{"description": "Consultoria", "quantity": "1", "unit_price": "800.00"}],
    )
    ProposalService.send_proposal(db_session, prop.id)
    token = prop.public_token

    # Recusar pelo link público
    refuse_resp = client.post(f"/p/{token}/recusar", follow_redirects=True)
    assert refuse_resp.status_code == 200
    assert "Proposta Recusada" in refuse_resp.text
    assert "Aceitar Proposta" not in refuse_resp.text

    db_session.refresh(prop)
    assert prop.status == ProposalStatus.RECUSADA.value
    assert prop.decided_at is not None

    # Idempotência: recusar novamente
    repeat_refuse = client.post(f"/p/{token}/recusar", follow_redirects=True)
    assert repeat_refuse.status_code == 200
    assert "Proposta Recusada" in repeat_refuse.text

    # Tentar aceitar proposta já recusada -> erro 400
    accept_after_refuse = client.post(f"/p/{token}/aceitar")
    assert accept_after_refuse.status_code == 400
    assert "já foi recusada" in accept_after_refuse.text


def test_public_and_admin_json_api(client, sample_customer):
    # Criar proposta via API JSON
    payload = {
        "customer_id": sample_customer.id,
        "title": "API Proposal",
        "discount_percent": "5.00",
        "items": [
            {"description": "Dev", "quantity": "2", "unit_price": "200.00"},
        ],
    }
    create_res = client.post("/propostas", json=payload)
    assert create_res.status_code == 200
    data = create_res.json()
    proposal_id = data["id"]
    assert data["status"] == "rascunho"
    assert data["subtotal"] == "400.00"
    assert data["discount_amount"] == "20.00"
    assert data["total"] == "380.00"

    # Enviar via API
    send_res = client.post(f"/api/propostas/{proposal_id}/enviar")
    assert send_res.status_code == 200
    token = send_res.json()["public_token"]
    assert token is not None

    # Consultar API pública
    pub_res = client.get(f"/api/p/{token}")
    assert pub_res.status_code == 200
    pub_data = pub_res.json()
    assert pub_data["title"] == "API Proposal"
    assert pub_data["customer_name"] == sample_customer.name
    assert "id" not in pub_data  # Minimização de dados: sem id interno
    assert "customer_id" not in pub_data

    # Decidir via API pública
    accept_res = client.post(f"/api/p/{token}/aceitar")
    assert accept_res.status_code == 200
    assert accept_res.json()["status"] == "aceita"

