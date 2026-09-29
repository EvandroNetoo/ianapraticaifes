from decimal import Decimal, InvalidOperation
from typing import List, Optional
from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Customer, Proposal
from app.schemas import (
    CustomerCreate,
    CustomerResponse,
    ProposalCreate,
    ProposalResponse,
)
from app.services.proposals import (
    ProposalService,
    ProposalServiceError,
    ValidationError,
    NotFoundError,
    InvalidStatusTransitionError,
    format_currency_br,
)

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
templates.env.globals["format_currency"] = format_currency_br


@router.get("/", response_class=RedirectResponse)
def root():
    return RedirectResponse(url="/propostas", status_code=status.HTTP_303_SEE_OTHER)


# ----------------- Clientes -----------------


@router.get("/clientes", response_class=HTMLResponse)
def list_customers_page(request: Request, db: Session = Depends(get_db)):
    customers = ProposalService.list_customers(db)
    return templates.TemplateResponse(
        request=request,
        name="admin/customers.html",
        context={
            "customers": customers,
            "active_nav": "customers",
        },
    )


@router.post("/clientes")
def create_customer_form(
    request: Request,
    name: str = Form(...),
    company: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    try:
        ProposalService.create_customer(db, name=name, email=email, company=company)
        return RedirectResponse(url="/clientes", status_code=status.HTTP_303_SEE_OTHER)
    except ProposalServiceError as e:
        customers = ProposalService.list_customers(db)
        return templates.TemplateResponse(
            request=request,
            name="admin/customers.html",
            context={
                "customers": customers,
                "active_nav": "customers",
                "error": str(e),
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )


@router.get("/api/clientes", response_model=List[CustomerResponse])
def api_list_customers(db: Session = Depends(get_db)):
    return ProposalService.list_customers(db)


@router.post("/api/clientes", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
def api_create_customer(payload: CustomerCreate, db: Session = Depends(get_db)):
    try:
        return ProposalService.create_customer(
            db, name=payload.name, email=payload.email, company=payload.company
        )
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ----------------- Propostas -----------------


@router.get("/propostas", response_class=HTMLResponse)
def list_proposals_page(request: Request, db: Session = Depends(get_db)):
    proposals = ProposalService.list_proposals(db)
    return templates.TemplateResponse(
        request=request,
        name="admin/proposals_list.html",
        context={
            "proposals": proposals,
            "active_nav": "proposals",
        },
    )


@router.get("/propostas/nova", response_class=HTMLResponse)
def new_proposal_page(
    request: Request,
    customer_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    customers = ProposalService.list_customers(db)
    return templates.TemplateResponse(
        request=request,
        name="admin/proposal_create.html",
        context={
            "customers": customers,
            "selected_customer_id": customer_id,
            "active_nav": "proposals",
        },
    )


@router.post("/propostas")
async def create_proposal_handler(
    request: Request,
    db: Session = Depends(get_db),
):
    # Detect if content is JSON or Form
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        data = await request.json()
        try:
            p_data = ProposalCreate(**data)
            items_raw = [item.model_dump() for item in p_data.items]
            proposal = ProposalService.create_proposal(
                db=db,
                customer_id=p_data.customer_id,
                title=p_data.title,
                items_data=items_raw,
                discount_percent=p_data.discount_percent,
            )
            return ProposalResponse.model_validate(proposal)
        except (ValidationError, NotFoundError) as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

    # Form Submission
    form = await request.form()
    customer_id_raw = form.get("customer_id")
    title = form.get("title", "")
    discount_raw = form.get("discount_percent", "0.00")

    item_descs = form.getlist("item_description")
    item_qtys = form.getlist("item_quantity")
    item_prices = form.getlist("item_unit_price")

    customers = ProposalService.list_customers(db)

    try:
        if not customer_id_raw:
            raise ValidationError("Selecione um cliente.")
        customer_id = int(customer_id_raw)

        items_data = []
        for d, q, p in zip(item_descs, item_qtys, item_prices):
            if d or q or p:
                items_data.append({
                    "description": d,
                    "quantity": q,
                    "unit_price": p,
                })

        proposal = ProposalService.create_proposal(
            db=db,
            customer_id=customer_id,
            title=title,
            items_data=items_data,
            discount_percent=Decimal(discount_raw) if discount_raw else Decimal("0.00"),
        )
        return RedirectResponse(
            url=f"/propostas/{proposal.id}",
            status_code=status.HTTP_303_SEE_OTHER,
        )
    except (ValidationError, NotFoundError, ValueError, InvalidOperation) as e:
        return templates.TemplateResponse(
            request=request,
            name="admin/proposal_create.html",
            context={
                "customers": customers,
                "selected_customer_id": int(customer_id_raw) if customer_id_raw and customer_id_raw.isdigit() else None,
                "prefill_title": title,
                "error": str(e),
                "active_nav": "proposals",
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )


@router.get("/propostas/{proposal_id}", response_class=HTMLResponse)
def view_proposal_page(
    proposal_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    proposal = ProposalService.get_proposal(db, proposal_id)
    if not proposal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proposta não encontrada.")

    public_url = ""
    if proposal.public_token:
        public_url = str(request.base_url).rstrip("/") + f"/p/{proposal.public_token}"

    return templates.TemplateResponse(
        request=request,
        name="admin/proposal_detail.html",
        context={
            "proposal": proposal,
            "public_url": public_url,
            "active_nav": "proposals",
        },
    )


@router.post("/propostas/{proposal_id}/enviar")
def send_proposal_action(
    proposal_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    try:
        ProposalService.send_proposal(db, proposal_id)
        return RedirectResponse(
            url=f"/propostas/{proposal_id}",
            status_code=status.HTTP_303_SEE_OTHER,
        )
    except (NotFoundError, InvalidStatusTransitionError, ValidationError) as e:
        proposal = ProposalService.get_proposal(db, proposal_id)
        if not proposal:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proposta não encontrada.")
        public_url = str(request.base_url).rstrip("/") + f"/p/{proposal.public_token}" if proposal.public_token else ""
        return templates.TemplateResponse(
            request=request,
            name="admin/proposal_detail.html",
            context={
                "proposal": proposal,
                "public_url": public_url,
                "error": str(e),
                "active_nav": "proposals",
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )


# API endpoints


@router.get("/api/propostas", response_model=List[ProposalResponse])
def api_list_proposals(db: Session = Depends(get_db)):
    return ProposalService.list_proposals(db)


@router.get("/api/propostas/{proposal_id}", response_model=ProposalResponse)
def api_get_proposal(proposal_id: int, db: Session = Depends(get_db)):
    proposal = ProposalService.get_proposal(db, proposal_id)
    if not proposal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proposta não encontrada.")
    return proposal


@router.post("/api/propostas/{proposal_id}/enviar", response_model=ProposalResponse)
def api_send_proposal(proposal_id: int, db: Session = Depends(get_db)):
    try:
        return ProposalService.send_proposal(db, proposal_id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (InvalidStatusTransitionError, ValidationError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
