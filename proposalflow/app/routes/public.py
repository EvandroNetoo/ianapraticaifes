from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ProposalStatus
from app.schemas import PublicProposalResponse
from app.services.proposals import (
    ProposalService,
    ProposalServiceError,
    NotFoundError,
    ValidationError,
    AlreadyDecidedError,
    InvalidStatusTransitionError,
    format_currency_br,
)

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
templates.env.globals["format_currency"] = format_currency_br


@router.get("/p/{token}", response_class=HTMLResponse, name="public_proposal_view")
def public_proposal_page(
    token: str,
    request: Request,
    db: Session = Depends(get_db),
):
    proposal = ProposalService.get_proposal_by_token(db, token)
    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proposta não encontrada ou link inválido.",
        )

    return templates.TemplateResponse(
        request=request,
        name="public/proposal_view.html",
        context={
            "proposal": proposal,
        },
    )


@router.post("/p/{token}/aceitar")
def accept_proposal_action(
    token: str,
    request: Request,
    db: Session = Depends(get_db),
):
    try:
        proposal, was_modified = ProposalService.decide_proposal_by_token(
            db=db,
            token=token,
            decision=ProposalStatus.ACEITA.value,
        )
        return RedirectResponse(
            url=f"/p/{token}",
            status_code=status.HTTP_303_SEE_OTHER,
        )
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (AlreadyDecidedError, InvalidStatusTransitionError, ValidationError) as e:
        proposal = ProposalService.get_proposal_by_token(db, token)
        if not proposal:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proposta não encontrada.")
        return templates.TemplateResponse(
            request=request,
            name="public/proposal_view.html",
            context={
                "proposal": proposal,
                "error": str(e),
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )


@router.post("/p/{token}/recusar")
def refuse_proposal_action(
    token: str,
    request: Request,
    db: Session = Depends(get_db),
):
    try:
        proposal, was_modified = ProposalService.decide_proposal_by_token(
            db=db,
            token=token,
            decision=ProposalStatus.RECUSADA.value,
        )
        return RedirectResponse(
            url=f"/p/{token}",
            status_code=status.HTTP_303_SEE_OTHER,
        )
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (AlreadyDecidedError, InvalidStatusTransitionError, ValidationError) as e:
        proposal = ProposalService.get_proposal_by_token(db, token)
        if not proposal:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proposta não encontrada.")
        return templates.TemplateResponse(
            request=request,
            name="public/proposal_view.html",
            context={
                "proposal": proposal,
                "error": str(e),
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )


# API endpoints


def _to_public_schema(proposal) -> PublicProposalResponse:
    return PublicProposalResponse(
        title=proposal.title,
        customer_name=proposal.customer.name,
        customer_company=proposal.customer.company,
        status=proposal.status,
        discount_percent=proposal.discount_percent,
        subtotal=proposal.subtotal,
        discount_amount=proposal.discount_amount,
        total=proposal.total,
        items=proposal.items,
        sent_at=proposal.sent_at,
        decided_at=proposal.decided_at,
    )


@router.get("/api/p/{token}", response_model=PublicProposalResponse)
def api_public_proposal(token: str, db: Session = Depends(get_db)):
    proposal = ProposalService.get_proposal_by_token(db, token)
    if not proposal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proposta não encontrada.")
    return _to_public_schema(proposal)


@router.post("/api/p/{token}/aceitar", response_model=PublicProposalResponse)
def api_public_accept(token: str, db: Session = Depends(get_db)):
    try:
        proposal, _ = ProposalService.decide_proposal_by_token(
            db, token, ProposalStatus.ACEITA.value
        )
        return _to_public_schema(proposal)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (AlreadyDecidedError, InvalidStatusTransitionError, ValidationError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/api/p/{token}/recusar", response_model=PublicProposalResponse)
def api_public_refuse(token: str, db: Session = Depends(get_db)):
    try:
        proposal, _ = ProposalService.decide_proposal_by_token(
            db, token, ProposalStatus.RECUSADA.value
        )
        return _to_public_schema(proposal)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (AlreadyDecidedError, InvalidStatusTransitionError, ValidationError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
