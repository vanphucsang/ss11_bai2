from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timezone
from database import get_db, Base, engine
from model import SmartHomePlanModel
from schema import SmartHomePlanCreate, SmartHomePlanResponse

app = FastAPI(
    title="Smart Home Plans Management"
)

Base.metadata.create_all(bind=engine)


def build_response(status_code, message, error, data, path):
    return {
        "statusCode": status_code,
        "message": message,
        "error": error,
        "data": data,
        "path": path,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content=exc.detail)


@app.post("/smart-home-plans")
def create_plan(plan: SmartHomePlanCreate, request: Request, db: Session = Depends(get_db)):
    existing = db.query(SmartHomePlanModel).filter(SmartHomePlanModel.plan_code == plan.plan_code).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=build_response(400, "Plan code already exists", "Bad Request", None, str(request.url.path))
        )

    try:
        new_plan = SmartHomePlanModel(
            plan_code=plan.plan_code,
            plan_name=plan.plan_name,
            device_quantity=plan.device_quantity,
            price=plan.price
        )
        db.add(new_plan)
        db.commit()
        db.refresh(new_plan)
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=build_response(500, "Internal Server Error", "Internal Server Error", None, str(request.url.path))
        )

    data = SmartHomePlanResponse.model_validate(new_plan).model_dump()
    return build_response(201, "Them goi thiet bi thanh cong", None, data, str(request.url.path))


@app.get("/smart-home-plans")
def get_plans(request: Request, db: Session = Depends(get_db)):
    plans = db.query(SmartHomePlanModel).all()
    data = [SmartHomePlanResponse.model_validate(plan).model_dump() for plan in plans]
    return build_response(200, "Lay danh sach thanh cong", None, data, str(request.url.path))


@app.get("/smart-home-plans/{plan_id}")
def get_plan_detail(plan_id: int, request: Request, db: Session = Depends(get_db)):
    plan = db.query(SmartHomePlanModel).filter(SmartHomePlanModel.id == plan_id).first()
    if not plan:
        raise HTTPException(
            status_code=404,
            detail=build_response(404, "Plan not found", "Not Found", None, str(request.url.path))
        )

    data = SmartHomePlanResponse.model_validate(plan).model_dump()
    return build_response(200, "Lay chi tiet thanh cong", None, data, str(request.url.path))
