import pytest
from decimal import Decimal
from app.services.proposals import (
    ProposalService,
    ValidationError,
    calculate_item_total,
    calculate_proposal_totals,
    format_currency_br,
    quantize_money,
)


def test_quantize_money():
    assert quantize_money(Decimal("10.555")) == Decimal("10.56")
    assert quantize_money(Decimal("10.554")) == Decimal("10.55")
    assert quantize_money(Decimal("0")) == Decimal("0.00")


def test_format_currency_br():
    assert format_currency_br(Decimal("1250.50")) == "R$ 1.250,50"
    assert format_currency_br(Decimal("0.00")) == "R$ 0,00"
    assert format_currency_br(Decimal("1000000.99")) == "R$ 1.000.000,99"
    assert format_currency_br(None) == "R$ 0,00"


def test_calculate_item_total_valid():
    total = calculate_item_total(Decimal("2"), Decimal("150.00"))
    assert total == Decimal("300.00")

    # Quantidade decimal (ex: horas)
    total_fractional = calculate_item_total(Decimal("2.5"), Decimal("100.00"))
    assert total_fractional == Decimal("250.00")


def test_calculate_item_total_invalid_quantity():
    with pytest.raises(ValidationError, match="A quantidade deve ser maior que zero"):
        calculate_item_total(Decimal("0"), Decimal("100.00"))

    with pytest.raises(ValidationError, match="A quantidade deve ser maior que zero"):
        calculate_item_total(Decimal("-1"), Decimal("100.00"))


def test_calculate_item_total_invalid_unit_price():
    with pytest.raises(ValidationError, match="O preço unitário deve ser maior que zero"):
        calculate_item_total(Decimal("1"), Decimal("0.00"))

    with pytest.raises(ValidationError, match="O preço unitário deve ser maior que zero"):
        calculate_item_total(Decimal("1"), Decimal("-50.00"))


def test_calculate_proposal_totals_single_and_multiple_items():
    # Um item
    subtotal, discount, total = calculate_proposal_totals(
        [(Decimal("1"), Decimal("500.00"))],
        discount_percent=Decimal("0.00"),
    )
    assert subtotal == Decimal("500.00")
    assert discount == Decimal("0.00")
    assert total == Decimal("500.00")

    # Múltiplos itens
    items = [
        (Decimal("2"), Decimal("100.00")),   # 200.00
        (Decimal("1"), Decimal("350.50")),   # 350.50
        (Decimal("10"), Decimal("15.25")),   # 152.50
    ]
    subtotal, discount, total = calculate_proposal_totals(items, discount_percent=Decimal("10.00"))
    assert subtotal == Decimal("703.00")
    assert discount == Decimal("70.30")
    assert total == Decimal("632.70")


def test_calculate_proposal_totals_discount_boundaries():
    items = [(Decimal("1"), Decimal("1000.00"))]

    # Limite 0%
    subtotal, discount, total = calculate_proposal_totals(items, discount_percent=Decimal("0.00"))
    assert subtotal == Decimal("1000.00")
    assert discount == Decimal("0.00")
    assert total == Decimal("1000.00")

    # Limite 100%
    subtotal, discount, total = calculate_proposal_totals(items, discount_percent=Decimal("100.00"))
    assert subtotal == Decimal("1000.00")
    assert discount == Decimal("1000.00")
    assert total == Decimal("0.00")


def test_calculate_proposal_totals_invalid_discount():
    items = [(Decimal("1"), Decimal("100.00"))]

    with pytest.raises(ValidationError, match="O desconto deve estar entre 0% e 100%"):
        calculate_proposal_totals(items, discount_percent=Decimal("-0.01"))

    with pytest.raises(ValidationError, match="O desconto deve estar entre 0% e 100%"):
        calculate_proposal_totals(items, discount_percent=Decimal("100.01"))


def test_create_proposal_without_items(db_session, sample_customer):
    with pytest.raises(ValidationError, match="A proposta deve possuir pelo menos um item"):
        ProposalService.create_proposal(
            db=db_session,
            customer_id=sample_customer.id,
            title="Proposta Vazia",
            items_data=[],
            discount_percent=Decimal("0.00"),
        )


def test_create_proposal_with_invalid_item_fields(db_session, sample_customer):
    # Descrição vazia
    with pytest.raises(ValidationError, match="A descrição do item 1 é obrigatória"):
        ProposalService.create_proposal(
            db=db_session,
            customer_id=sample_customer.id,
            title="Proposta Inválida",
            items_data=[{"description": "", "quantity": "1", "unit_price": "100.00"}],
        )

    # Quantidade negativa
    with pytest.raises(ValidationError, match="A quantidade do item 1 deve ser maior que zero"):
        ProposalService.create_proposal(
            db=db_session,
            customer_id=sample_customer.id,
            title="Proposta Inválida",
            items_data=[{"description": "Item", "quantity": "-1", "unit_price": "100.00"}],
        )

    # Preço zerado
    with pytest.raises(ValidationError, match="O preço unitário do item 1 deve ser maior que zero"):
        ProposalService.create_proposal(
            db=db_session,
            customer_id=sample_customer.id,
            title="Proposta Inválida",
            items_data=[{"description": "Item", "quantity": "1", "unit_price": "0.00"}],
        )
