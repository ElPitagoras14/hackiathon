from fastapi import APIRouter, Request, Response, Depends
from loguru import logger
from sqlalchemy import func
from packages.ai.llm import generate_insights
from .config import company_settings 

from packages.companies.config import company_settings  # <- solicitado
from packages.ai.agent import analyze_company, credit_decision
from queues.ai_agent import analyze_company, credit_decision

from queues import celery_app
from ...utils.responses import (
    InternalServerErrorResponse,
    NotFoundResponse,
    SuccessResponse,
)
from ...databases.postgres import (
    DatabaseSession,
    Company as CompanyDB,
    FinancialInfo as FinancialInfoDB,
    CreditRequest as CreditRequestDB,
)
from packages.auth import auth_scheme
from .schemas import CompanyInfo, CreditRequestInfo
from .responses import (
    TaskOut,
    Task,
    CreditRequest,
    CreditRequestList,
    CreditRequestOut,
    Company,
    CompanyList,
    CompanyListOut,
    FinancialInfo,
)


company_router = APIRouter()


@company_router.get("")
async def get_all_company(
    request: Request,
    response: Response,
    current_user=Depends(auth_scheme),
):
    request_id = request.state.request_id
    try:
        with DatabaseSession() as db:
            latest_fi_subq = (
                db.query(
                    FinancialInfoDB.company_id,
                    func.max(FinancialInfoDB.created_at).label(
                        "latest_created_at"
                    ),
                )
                .filter(FinancialInfoDB.status == "COMPLETED")
                .group_by(FinancialInfoDB.company_id)
                .subquery()
            )

            companies_with_fi = (
                db.query(CompanyDB, FinancialInfoDB)
                .filter(CompanyDB.user_id == current_user["id"])
                .outerjoin(
                    latest_fi_subq, latest_fi_subq.c.company_id == CompanyDB.id
                )
                .outerjoin(
                    FinancialInfoDB,
                    (FinancialInfoDB.company_id == CompanyDB.id)
                    & (
                        FinancialInfoDB.created_at
                        == latest_fi_subq.c.latest_created_at
                    ),
                )
                .all()
            )
            parsed_companies = [
                Company(
                    id=company.id,
                    user_id=company.user_id,
                    name=company.name,
                    ruc=company.ruc,
                    ig_url=company.ig_url,
                    industry=company.industry,
                    financial_info=(
                        FinancialInfo(
                            id=financial_info.id,
                            company_id=financial_info.company_id,
                            account_status=financial_info.account_status,
                            status=financial_info.status,
                            average_cash_flow=financial_info.average_cash_flow,
                            debt_ratio=financial_info.debt_ratio,
                            income_variability=financial_info.income_variability,
                            platform_reviews=financial_info.platform_reviews,
                            social_media_activity=financial_info.social_media_activity,
                            suppliers_reviews=financial_info.suppliers_reviews,
                            customer_reviews=financial_info.customer_reviews,
                            payment_compliance=financial_info.payment_compliance,
                            on_time_delivery=financial_info.on_time_delivery,
                            income_simulation=financial_info.income_simulation,
                            reputation_simulation=financial_info.reputation_simulation,
                            created_at=financial_info.created_at,
                        )
                        if financial_info
                        else None
                    ),
                )
                for company, financial_info in companies_with_fi
            ]
            return CompanyListOut(
                request_id=request_id,
                process_time=0,
                func="get_all_company",
                message="Company retrieved",
                payload=CompanyList(
                    items=parsed_companies,
                    total=len(parsed_companies),
                ),
            )
    except Exception as e:
        logger.error(f"Error getting company: {e}")
        response.status_code = 500
        return InternalServerErrorResponse(
            request_id=request_id, message=str(e), func="get_all_company"
        )


@company_router.post("")
async def create_company(
    request: Request,
    response: Response,
    company_info: CompanyInfo,
    current_user=Depends(auth_scheme),
):
    request_id = request.state.request_id
    try:
        with DatabaseSession() as db:
            company = CompanyDB(
                user_id=current_user["id"],
                name=company_info.name,
                ruc=company_info.ruc,
                ig_url=company_info.ig_url,
                industry=company_info.industry,
            )
            db.add(company)
            db.commit()
            db.refresh(company)
            logger.info(f"Company {company.id} created")
            return SuccessResponse(
                request_id=request_id,
                process_time=0,
                func="create_company",
                message="Company created",
            )
    except Exception as e:
        logger.error(f"Error creating company: {e}")
        response.status_code = 500
        return InternalServerErrorResponse(
            request_id=request_id, message=str(e), func="create_company"
        )


@company_router.post("/scrape-info")
async def scrape_info(
    request: Request,
    response: Response,
    company_id: int,
    current_user=Depends(auth_scheme),
):
    request_id = request.state.request_id
    try:
        with DatabaseSession() as db:
            company = (
                db.query(CompanyDB).filter(CompanyDB.id == company_id).first()
            )
            if not company:
                return NotFoundResponse(
                    request_id=request_id,
                    process_time=0,
                    func="scrape_info",
                    message="Company not found",
                )

            financial_info = (
                db.query(FinancialInfoDB)
                .filter(
                    (FinancialInfoDB.company_id == company_id)
                    & (FinancialInfoDB.status == "PENDING")
                )
                .first()
            )

            if financial_info:
                return TaskOut(
                    request_id=request_id,
                    process_time=0,
                    func="get_info",
                    message="Task already enqueued",
                    payload=Task(id=None),
                )

            financial_info = FinancialInfoDB(
                company_id=company_id,
            )
            db.add(financial_info)
            db.commit()
            db.refresh(financial_info)

            task = celery_app.send_task(
                "scrape_task",
                args=[
                    financial_info.id,
                    company.ruc,
                    company.ig_url,
                ],
            )

            task_id = task.id
            logger.info(f"Task {task_id} enqueued")
            return TaskOut(
                request_id=request_id,
                process_time=0,
                func="scrape",
                message="Task enqueued",
                payload=Task(id=task_id),
            )
    except Exception as e:
        logger.error(f"Error scraping: {e}")
        response.status_code = 500
        return InternalServerErrorResponse(
            request_id=request_id, message=str(e), func="get_info"
        )


@company_router.get("/credit-requests")
async def get_all_credit_requests(
    request: Request,
    response: Response,
    company_id: int,
    current_user=Depends(auth_scheme),
):
    request_id = request.state.request_id
    try:
        with DatabaseSession() as db:
            company = (
                db.query(CompanyDB).filter(CompanyDB.id == company_id).first()
            )
            if not company:
                return NotFoundResponse(
                    request_id=request_id,
                    process_time=0,
                    func="get_all_credit_requests",
                    message="Company not found",
                )
            credit_requests = (
                db.query(CreditRequestDB)
                .filter(CreditRequestDB.company_id == company_id)
                .all()
            )
            parsed_credit_requests = [
                CreditRequest(
                    id=credit_request.id,
                    company_id=credit_request.company_id,
                    amount=credit_request.amount,
                    reason=credit_request.reason,
                    status=credit_request.status,
                    created_at=credit_request.created_at,
                )
                for credit_request in credit_requests
            ]
            return CreditRequestOut(
                request_id=request_id,
                process_time=0,
                func="get_all_credit_requests",
                message="Credit requests retrieved",
                payload=CreditRequestList(
                    items=parsed_credit_requests,
                    total=len(parsed_credit_requests),
                ),
            )
    except Exception as e:
        logger.error(f"Error getting credit requests: {e}")
        response.status_code = 500
        return InternalServerErrorResponse(
            request_id=request_id,
            message=str(e),
            func="get_all_credit_requests",
        )


@company_router.get("/llm-insights")
async def get_llm_insights(
    request: Request,
    response: Response,
    company_id: int,
    current_user=Depends(auth_scheme),
):
    request_id = request.state.request_id
    try:
        with DatabaseSession() as db:
            company = db.query(CompanyDB).filter(CompanyDB.id == company_id).first()
            if not company:
                return NotFoundResponse(
                    request_id=request_id,
                    process_time=0,
                    func="get_llm_insights",
                    message="Company not found",
                )

            latest_fi = (
                db.query(FinancialInfoDB)
                .filter(
                    (FinancialInfoDB.company_id == company_id)
                    & (FinancialInfoDB.status == "COMPLETED")
                )
                .order_by(FinancialInfoDB.created_at.desc())
                .first()
            )
            if not latest_fi:
                return NotFoundResponse(
                    request_id=request_id,
                    process_time=0,
                    func="get_llm_insights",
                    message="No hay información financiera completada aún",
                )

            # Ajusta estos campos a los tuyos reales si difieren
            metrics = {
                "sales": latest_fi.income_simulation or 0,
                "cash_flow": latest_fi.average_cash_flow or 0,
                "current_solvency": 1 - (latest_fi.debt_ratio or 0),
                "asset_turnover": latest_fi.on_time_delivery or 0,
                "ig_engagement": latest_fi.social_media_activity or 0,
            }

            tips = generate_insights(metrics)

            return SuccessResponse(
                request_id=request_id,
                process_time=0,
                func="get_llm_insights",
                message="Insights generados",
                payload={"insights": tips},
            )
    except Exception as e:
        logger.exception(e)
        response.status_code = 500
        return InternalServerErrorResponse(
            request_id=request_id, message=str(e), func="get_llm_insights"
        )


@company_router.post("/credit-request")
async def create_credit_request(
    request: Request,
    response: Response,
    credit_request: CreditRequestInfo,
    current_user=Depends(auth_scheme),
):
    request_id = request.state.request_id
    try:
        with DatabaseSession() as db:
            company = (
                db.query(CompanyDB)
                .filter(CompanyDB.id == credit_request.company_id)
                .first()
            )
            if not company:
                return NotFoundResponse(
                    request_id=request_id,
                    process_time=0,
                    func="create_credit_request",
                    message="Company not found",
                )

            # Crear la solicitud inicialmente
            cr = CreditRequestDB(
                company_id=credit_request.company_id,
                amount=credit_request.amount,
                reason="",          # lo llenamos luego
                status="PENDING",   # lo actualizamos luego
            )
            db.add(cr)
            db.commit()
            db.refresh(cr)

            # Obtener la última info financiera COMPLETED
            latest_fi = (
                db.query(FinancialInfoDB)
                .filter(
                    (FinancialInfoDB.company_id == company.id)
                    & (FinancialInfoDB.status == "COMPLETED")
                )
                .order_by(FinancialInfoDB.created_at.desc())
                .first()
            )

            if not latest_fi:
                # Si no hay info financiera, dejamos PENDING
                return SuccessResponse(
                    request_id=request_id,
                    process_time=0,
                    func="create_credit_request",
                    message="Credit request created (PENDING). No hay información financiera completada aún.",
                )

            # Armar métricas para el agente/LLM (ajusta campos a los tuyos reales)
            metrics = {
                "uid": str(company.id),
                "sales": latest_fi.income_simulation or 0,
                "cash_flow": latest_fi.average_cash_flow or 0,
                "assets": None,
                "liabilities": None,
                "equity": None,
                "current_solvency": 1 - (latest_fi.debt_ratio or 0),
                "asset_turnover": latest_fi.on_time_delivery or 0,
                "ig_engagement": latest_fi.social_media_activity or 0,
            }

            # 1) Corre el agente para decisión numérica (si lo tienes)
            decision = credit_decision(metrics, float(credit_request.amount))

            # 2) Pide insights al LLM (texto)
            tips = generate_insights(metrics)

            # Actualiza STATUS (APROBADO/DENEGADO) y REASON (multilínea)
            is_ok = bool(decision.get("approved", False))
            cr.status = "APROBADO" if is_ok else "DENEGADO"

            reasons = []
            # si tu decision trae razones, únelas
            if "insights" in decision and isinstance(decision["insights"], list):
                reasons.extend([str(x) for x in decision["insights"]])

            # agrega tips del LLM
            if tips:
                reasons.extend([str(x) for x in tips])

            cr.reason = "\n".join(reasons) if reasons else ""
            db.commit()
            db.refresh(cr)

            logger.info(f"Credit request {cr.id} updated -> {cr.status}")

            return SuccessResponse(
                request_id=request_id,
                process_time=0,
                func="create_credit_request",
                message=f"Credit request {cr.status}",
            )
    except Exception as e:
        logger.error(f"Error creating credit request: {e}")
        response.status_code = 500
        return InternalServerErrorResponse(
            request_id=request_id, message=str(e), func="create_credit_request"
        )


@company_router.post("/analyze-with-llm")
async def analyze_with_llm(
    request: Request,
    response: Response,
    company_id: int,
    amount: float = 0,
    current_user=Depends(auth_scheme),
):
    """
    2da función: calcula métricas + genera insights con LLM y (opcional) una decisión preliminar.
    """
    request_id = request.state.request_id
    try:
        with DatabaseSession() as db:
            company = db.query(CompanyDB).filter(CompanyDB.id == company_id).first()
            if not company:
                return NotFoundResponse(
                    request_id=request_id,
                    process_time=0,
                    func="analyze_with_llm",
                    message="Company not found",
                )

            # asume que los PDFs/JSON se generan por fuera con el uid = company.ruc o similar
            uid = company.ruc or str(company.id)
            vals = analyze_company(uid)  # calcula + LLM insights
            decision = credit_decision(vals, amount or 1.0)

            return SuccessResponse(
                request_id=request_id,
                process_time=0,
                func="analyze_with_llm",
                message="Análisis generado con LLM",
                payload={
                    "metrics": vals,
                    "decision": decision,
                    "model": company_settings.MODEL,  # para auditar qué modelo usamos
                },
            )
    except Exception as e:
        logger.error(f"Error analyze_with_llm: {e}")
        response.status_code = 500
        return InternalServerErrorResponse(
            request_id=request_id, message=str(e), func="analyze_with_llm"
        )


# ---- FIX en create_credit_request ----
@company_router.post("/credit-request")
async def create_credit_request(
    request: Request,
    response: Response,
    credit_request: CreditRequestInfo,
    current_user=Depends(auth_scheme),
):
    request_id = request.state.request_id
    try:
        with DatabaseSession() as db:
            company = (
                db.query(CompanyDB)
                .filter(CompanyDB.id == credit_request.company_id)
                .first()
            )
            if not company:
                return NotFoundResponse(
                    request_id=request_id,
                    process_time=0,
                    func="create_credit_request",
                    message="Company not found",
                )

            # ANALIZA + DECIDE
            uid = company.ruc or str(company.id)
            vals = analyze_company(uid)
            decision = credit_decision(vals, credit_request.amount)

            status_text = "APROBADO" if decision["approved"] else "DENEGADO"
            reason_text = "\n".join(f"- {r}" for r in decision.get("insights", [])) or "Sin observaciones."

            credit_req = CreditRequestDB(
                company_id=credit_request.company_id,
                amount=credit_request.amount,
                status=status_text,     # MAYÚSCULAS
                reason=reason_text,     # texto multilinea
            )
            db.add(credit_req)
            db.commit()
            db.refresh(credit_req)

            logger.info(f"Credit request {credit_req.id} created / {status_text}")

            return SuccessResponse(
                request_id=request_id,
                process_time=0,
                func="create_credit_request",
                message=f"Credit request {status_text}",
            )
    except Exception as e:
        logger.error(f"Error creating credit request: {e}")
        response.status_code = 500
        return InternalServerErrorResponse(
            request_id=request_id, message=str(e), func="create_credit_request"
        )
    