import secrets
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from datetime import datetime, timezone
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session

from app.models import Customer, Proposal, ProposalItem, ProposalStatus


class ProposalServiceError(Exception):
    """Exceção base para erros do serviço de propostas."""
    pass


class ValidationError(ProposalServiceError):
    """Erro de validação de dados de entrada ou regras de negócio."""
    pass


class InvalidStatusTransitionError(ProposalServiceError):
    """Erro lançado ao tentar transição de status não permitida."""
    pass


class NotFoundError(ProposalServiceError):
    """Erro quando recurso solicitado não é encontrado."""
    pass


class AlreadyDecidedError(ProposalServiceError):
    """Erro quando uma decisão diferente é tentada sobre proposta já decidida."""
    pass


def quantize_money(amount: Decimal) -> Decimal:
    """Arredonda valor monetário para 2 casas decimais usando ROUND_HALF_UP."""
    return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def format_currency_br(val: Decimal | float | int | None) -> str:
    """Formata valor decimal no formato monetário brasileiro: R$ X.XXX,XX."""
    if val is None:
        return "R$ 0,00"
    if not isinstance(val, Decimal):
        val = Decimal(str(val))
    val = quantize_money(val)
    parts = f"{val:,.2f}".split(".")
    integer_part = parts[0].replace(",", ".")
    decimal_part = parts[1]
    return f"R$ {integer_part},{decimal_part}"


def calculate_item_total(quantity: Decimal, unit_price: Decimal) -> Decimal:
    """Calcula total do item: quantidade * preço unitário."""
    if quantity <= 0:
        raise ValidationError("A quantidade deve ser maior que zero.")
    if unit_price <= 0:
        raise ValidationError("O preço unitário deve ser maior que zero.")
    return quantize_money(quantity * unit_price)


def calculate_proposal_totals(
    items_pricing: List[Tuple[Decimal, Decimal]],
    discount_percent: Decimal,
) -> Tuple[Decimal, Decimal, Decimal]:
    """Calcula subtotal, valor do desconto e total geral da proposta."""
    if discount_percent < Decimal("0.00") or discount_percent > Decimal("100.00"):
        raise ValidationError("O desconto deve estar entre 0% e 100%.")

    subtotal = Decimal("0.00")
    for qty, price in items_pricing:
        subtotal += calculate_item_total(qty, price)

    subtotal = quantize_money(subtotal)
    discount_factor = discount_percent / Decimal("100.00")
    discount_amount = quantize_money(subtotal * discount_factor)
    total = quantize_money(subtotal - discount_amount)

    if total < Decimal("0.00"):
        total = Decimal("0.00")

    return subtotal, discount_amount, total


class ProposalService:
    @staticmethod
    def create_customer(
        db: Session,
        name: str,
        email: Optional[str] = None,
        company: Optional[str] = None,
    ) -> Customer:
        if not name or not name.strip():
            raise ValidationError("O nome do cliente é obrigatório.")

        customer = Customer(
            name=name.strip(),
            email=email.strip() if email and email.strip() else None,
            company=company.strip() if company and company.strip() else None,
        )
        db.add(customer)
        db.commit()
        db.refresh(customer)
        return customer

    @staticmethod
    def list_customers(db: Session) -> List[Customer]:
        return db.query(Customer).order_by(Customer.name.asc()).all()

    @staticmethod
    def get_customer(db: Session, customer_id: int) -> Optional[Customer]:
        return db.query(Customer).filter(Customer.id == customer_id).first()

    @staticmethod
    def create_proposal(
        db: Session,
        customer_id: int,
        title: str,
        items_data: List[dict],
        discount_percent: Decimal = Decimal("0.00"),
    ) -> Proposal:
        customer = ProposalService.get_customer(db, customer_id)
        if not customer:
            raise NotFoundError("Cliente informado não existe.")

        if not title or not title.strip():
            raise ValidationError("O título da proposta é obrigatório.")

        if not items_data or len(items_data) == 0:
            raise ValidationError("A proposta deve possuir pelo menos um item.")

        try:
            discount_percent = Decimal(str(discount_percent))
        except (InvalidOperation, TypeError, ValueError):
            raise ValidationError("Percentual de desconto inválido.")

        if discount_percent < Decimal("0.00") or discount_percent > Decimal("100.00"):
            raise ValidationError("O desconto deve estar entre 0% e 100%.")

        validated_items = []
        pricing_tuples = []
        for index, item_raw in enumerate(items_data, start=1):
            desc = item_raw.get("description", "").strip() if item_raw.get("description") else ""
            if not desc:
                raise ValidationError(f"A descrição do item {index} é obrigatória.")

            try:
                qty = Decimal(str(item_raw.get("quantity", "")))
            except (InvalidOperation, TypeError, ValueError):
                raise ValidationError(f"A quantidade do item {index} é inválida.")

            try:
                price = Decimal(str(item_raw.get("unit_price", "")))
            except (InvalidOperation, TypeError, ValueError):
                raise ValidationError(f"O preço unitário do item {index} é inválido.")

            if qty <= Decimal("0.00"):
                raise ValidationError(f"A quantidade do item {index} deve ser maior que zero.")
            if price <= Decimal("0.00"):
                raise ValidationError(f"O preço unitário do item {index} deve ser maior que zero.")

            item_total = calculate_item_total(qty, price)
            validated_items.append({
                "description": desc,
                "quantity": qty,
                "unit_price": quantize_money(price),
                "total_price": item_total,
            })
            pricing_tuples.append((qty, price))

        subtotal, discount_amount, total = calculate_proposal_totals(pricing_tuples, discount_percent)

        proposal = Proposal(
            customer_id=customer_id,
            title=title.strip(),
            status=ProposalStatus.RASCUNHO.value,
            discount_percent=quantize_money(discount_percent),
            subtotal=subtotal,
            discount_amount=discount_amount,
            total=total,
            public_token=None,
        )
        db.add(proposal)
        db.flush()

        for it in validated_items:
            db_item = ProposalItem(
                proposal_id=proposal.id,
                description=it["description"],
                quantity=it["quantity"],
                unit_price=it["unit_price"],
                total_price=it["total_price"],
            )
            db.add(db_item)

        db.commit()
        db.refresh(proposal)
        return proposal

    @staticmethod
    def list_proposals(db: Session) -> List[Proposal]:
        return db.query(Proposal).order_by(Proposal.created_at.desc()).all()

    @staticmethod
    def get_proposal(db: Session, proposal_id: int) -> Optional[Proposal]:
        return db.query(Proposal).filter(Proposal.id == proposal_id).first()

    @staticmethod
    def get_proposal_by_token(db: Session, token: str) -> Optional[Proposal]:
        if not token:
            return None
        return db.query(Proposal).filter(Proposal.public_token == token).first()

    @staticmethod
    def send_proposal(db: Session, proposal_id: int) -> Proposal:
        proposal = ProposalService.get_proposal(db, proposal_id)
        if not proposal:
            raise NotFoundError("Proposta não encontrada.")

        if proposal.status != ProposalStatus.RASCUNHO.value:
            raise InvalidStatusTransitionError(
                f"Apenas propostas com status 'rascunho' podem ser enviadas. Status atual: '{proposal.status}'."
            )

        if not proposal.items or len(proposal.items) == 0:
            raise ValidationError("Não é possível enviar uma proposta sem itens.")

        if not proposal.public_token:
            proposal.public_token = secrets.token_urlsafe(32)

        proposal.status = ProposalStatus.ENVIADA.value
        proposal.sent_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(proposal)
        return proposal

    @staticmethod
    def decide_proposal_by_token(
        db: Session,
        token: str,
        decision: str,
    ) -> Tuple[Proposal, bool]:
        """
        Processa a decisão pública (aceitar ou recusar).
        Retorna (proposta, was_modified).
        Se a decisão já foi aplicada anteriormente (mesmo status), é idempotente (was_modified=False).
        Se já estiver decidida com status diferente, rejeita com erro.
        """
        if decision not in (ProposalStatus.ACEITA.value, ProposalStatus.RECUSADA.value):
            raise ValidationError(f"Decisão inválida: '{decision}'.")

        proposal = ProposalService.get_proposal_by_token(db, token)
        if not proposal:
            raise NotFoundError("Proposta não encontrada para o link informado.")

        # Idempotência: mesma decisão já tomada
        if proposal.status == decision:
            return proposal, False

        # Tentativa de mudar decisão já tomada
        if proposal.status in (ProposalStatus.ACEITA.value, ProposalStatus.RECUSADA.value):
            raise AlreadyDecidedError(
                f"Esta proposta já foi {proposal.status} anteriormente e não pode ser alterada."
            )

        # Só pode decidir proposta enviada
        if proposal.status != ProposalStatus.ENVIADA.value:
            raise InvalidStatusTransitionError(
                f"Apenas propostas com status 'enviada' podem receber decisão. Status atual: '{proposal.status}'."
            )

        proposal.status = decision
        proposal.decided_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(proposal)
        return proposal, True
