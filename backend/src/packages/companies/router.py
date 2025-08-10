from fastapi import APIRouter, Request, Response, Depends
from loguru import logger

from queues import celery_app
from utils.responses import (
    InternalServerErrorResponse,
    NotFoundResponse,
    SuccessResponse,
)
from databases.postgres import (
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
)


company_router = APIRouter()


@company_router.get("/company")
async def get_all_company(
    request: Request,
    response: Response,
    current_user=Depends(auth_scheme),
):
    request_id = request.state.request_id
    try:
        with DatabaseSession() as db:
            companies = (
                db.query(CompanyDB)
                .filter(CompanyDB.user_id == current_user["id"])
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
                )
                for company in companies
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


@company_router.post("/scrape-info")
async def scrape_info(
    request: Request,
    response: Response,
    company_info: CompanyInfo,
    current_user=Depends(auth_scheme),
):
    request_id = request.state.request_id
    try:
        with DatabaseSession() as db:
            company = (
                db.query(CompanyDB)
                .filter(CompanyDB.ruc == company_info.ruc)
                .first()
            )
            if not company:
                company = Company(
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

            financial_info = (
                db.query(FinancialInfoDB)
                .filter(
                    (FinancialInfoDB.company_id == company.id)
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
                company_id=company.id,
            )
            db.add(financial_info)
            db.commit()
            db.refresh(financial_info)

            task = celery_app.send_task(
                "scrape_task",
                args=[
                    financial_info.id,
                    company_info.ruc,
                    company_info.ig_url,
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

            credit_request = CreditRequestDB(
                company_id=credit_request.company_id,
                amount=credit_request.amount,
                status="PENDING",
            )
            db.add(credit_request)
            db.commit()
            db.refresh(credit_request)
            logger.info(f"Credit request {credit_request.id} created")
            return SuccessResponse(
                request_id=request_id,
                process_time=0,
                func="create_credit_request",
                message="Credit request created",
            )
    except Exception as e:
        logger.error(f"Error creating credit request: {e}")
        response.status_code = 500
        return InternalServerErrorResponse(
            request_id=request_id, message=str(e), func="create_credit_request"
        )
