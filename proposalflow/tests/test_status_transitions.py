import pytest
from decimal import Decimal
from app.models import ProposalStatus
from app.services.proposals import (
    ProposalService,
    InvalidStatusTransitionError,
    AlreadyDecidedError,
)


@pytest.fixture
def draft_proposal(db_session, sample_customer):
    return ProposalService.create_proposal(
        db=db_session,
        customer_id=sample_customer.id,
        title="Desenvolvimento de Software",
        items_data=[
            {"description": "Desenvolvimento Frontend", "quantity": "10", "unit_price": "150.00"},
            {"description": "Desenvolvimento Backend", "quantity": "10", "unit_price": "150.00"},
        ],
        discount_percent=Decimal("5.00"),
    )


def test_initial_proposal_status(draft_proposal):
    assert draft_proposal.status == ProposalStatus.RASCUNHO.value
    assert draft_proposal.public_token is None
    assert draft_proposal.sent_at is None
    assert draft_proposal.decided_at is None


def test_transition_rascunho_to_enviada(db_session, draft_proposal):
    sent = ProposalService.send_proposal(db_session, draft_proposal.id)
    assert sent.status == ProposalStatus.ENVIADA.value
    assert sent.public_token is not None
    assert len(sent.public_token) >= 32
    assert sent.sent_at is not None


def test_token_non_enumerable_and_unique(db_session, sample_customer):
    prop1 = ProposalService.create_proposal(
        db=db_session,
        customer_id=sample_customer.id,
        title="Proposta 1",
        items_data=[{"description": "Item 1", "quantity": "1", "unit_price": "100.00"}],
    )
    prop2 = ProposalService.create_proposal(
        db=db_session,
        customer_id=sample_customer.id,
        title="Proposta 2",
        items_data=[{"description": "Item 2", "quantity": "1", "unit_price": "200.00"}],
    )
    sent1 = ProposalService.send_proposal(db_session, prop1.id)
    sent2 = ProposalService.send_proposal(db_session, prop2.id)

    # Tokens são strings opacas, com entropia criptográfica e distintos
    assert sent1.public_token != sent2.public_token
    assert not sent1.public_token.isdigit()
    assert not sent2.public_token.isdigit()
    assert str(prop1.id) != sent1.public_token
    assert str(prop2.id) != sent2.public_token



def test_cannot_resend_already_sent_proposal(db_session, draft_proposal):
    ProposalService.send_proposal(db_session, draft_proposal.id)
    with pytest.raises(InvalidStatusTransitionError, match="Apenas propostas com status 'rascunho' podem ser enviadas"):
        ProposalService.send_proposal(db_session, draft_proposal.id)


def test_transition_enviada_to_aceita(db_session, draft_proposal):
    sent = ProposalService.send_proposal(db_session, draft_proposal.id)
    token = sent.public_token

    accepted, was_modified = ProposalService.decide_proposal_by_token(
        db_session, token, ProposalStatus.ACEITA.value
    )
    assert was_modified is True
    assert accepted.status == ProposalStatus.ACEITA.value
    assert accepted.decided_at is not None


def test_transition_enviada_to_recusada(db_session, draft_proposal):
    sent = ProposalService.send_proposal(db_session, draft_proposal.id)
    token = sent.public_token

    refused, was_modified = ProposalService.decide_proposal_by_token(
        db_session, token, ProposalStatus.RECUSADA.value
    )
    assert was_modified is True
    assert refused.status == ProposalStatus.RECUSADA.value
    assert refused.decided_at is not None


def test_cannot_decide_rascunho(db_session, draft_proposal):
    # Proposta em rascunho nem sequer tem token público
    # Se tentarmos decidir com token arbitrário ou forçando
    draft_proposal.public_token = "token_de_rascunho"
    db_session.commit()

    with pytest.raises(InvalidStatusTransitionError, match="Apenas propostas com status 'enviada' podem receber decisão"):
        ProposalService.decide_proposal_by_token(
            db_session, "token_de_rascunho", ProposalStatus.ACEITA.value
        )


def test_idempotent_decision_repeat(db_session, draft_proposal):
    sent = ProposalService.send_proposal(db_session, draft_proposal.id)
    token = sent.public_token

    # Primeira decisão
    prop, modified1 = ProposalService.decide_proposal_by_token(
        db_session, token, ProposalStatus.ACEITA.value
    )
    assert modified1 is True
    assert prop.status == ProposalStatus.ACEITA.value
    first_decided_at = prop.decided_at

    # Repetição da mesma decisão (idempotente)
    prop2, modified2 = ProposalService.decide_proposal_by_token(
        db_session, token, ProposalStatus.ACEITA.value
    )
    assert modified2 is False
    assert prop2.status == ProposalStatus.ACEITA.value
    assert prop2.decided_at == first_decided_at


def test_cannot_change_decision_once_accepted_or_refused(db_session, draft_proposal):
    sent = ProposalService.send_proposal(db_session, draft_proposal.id)
    token = sent.public_token

    # Aceita
    ProposalService.decide_proposal_by_token(db_session, token, ProposalStatus.ACEITA.value)

    # Tenta recusar após aceita -> deve falhar
    with pytest.raises(AlreadyDecidedError, match="já foi aceita"):
        ProposalService.decide_proposal_by_token(
            db_session, token, ProposalStatus.RECUSADA.value
        )

    # Nova proposta para testar o inverso
    prop_b = ProposalService.create_proposal(
        db=db_session,
        customer_id=draft_proposal.customer_id,
        title="Outra proposta",
        items_data=[{"description": "Item", "quantity": "1", "unit_price": "100.00"}],
    )
    sent_b = ProposalService.send_proposal(db_session, prop_b.id)
    ProposalService.decide_proposal_by_token(db_session, sent_b.public_token, ProposalStatus.RECUSADA.value)

    # Tenta aceitar após recusada -> deve falhar
    with pytest.raises(AlreadyDecidedError, match="já foi recusada"):
        ProposalService.decide_proposal_by_token(
            db_session, sent_b.public_token, ProposalStatus.ACEITA.value
        )
