from fastapi import FastAPI, HTTPException, status, Depends, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
from typing import Optional, Any
from fastapi.responses import JSONResponse

from database import get_db, Base, engine
from services import create_ship, get_ship
import models  # ensure models loaded before create_all

Base.metadata.create_all(bind=engine)

app = FastAPI()


class CreateShipment(BaseModel):
    tracking_number: str
    status: str = Field(default="PREPARING")


class ShipmentOut(BaseModel):
    id: int
    tracking_number: str
    status: str

    class Config:
        from_attributes = True


class BaseResponse(BaseModel):
    status_code: int
    message: str
    data: Optional[Any] = None
    error: Optional[Any] = None
    timestamp: str
    path: str

def to_dict(ship):
    return {
        "id": ship.id,
        "tracking_number": ship.tracking_number,
        "status": ship.status
    }

def success_response(status_code: int, message: str, data: Any, path: str):
    return BaseResponse(
        status_code=status_code,
        message=message,
        data=data,
        error=None,
        timestamp=datetime.now().isoformat(),
        path=path
    )


def fail_response(status_code: int, message: str, error, path: str):
    return JSONResponse(
        status_code=status_code,
        content={
            "status_code": status_code,
            "message": message,
            "data": None,
            "error": error,
            "timestamp": datetime.now().isoformat(),
            "path": path
        }
    )


@app.exception_handler(HTTPException)
def http_exception_handler(request: Request, exc: HTTPException):
    return fail_response(
        status_code=exc.status_code,
        message=exc.detail,
        error="HTTPException",
        path=request.url.path
    )


@app.exception_handler(Exception)
def global_exception_handler(request: Request, exc: Exception):
    return fail_response(
        status_code=500,
        message="System error",
        error=str(exc),
        path=request.url.path
    )


@app.get("/connect")
def test_connect(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"msg": "Connection successful"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/shipments", status_code=status.HTTP_201_CREATED)
def create_shipment(
    request: Request,
    shipment: CreateShipment,
    db: Session = Depends(get_db)
):

    result = create_ship(
        db=db,
        tracking_number=shipment.tracking_number,
        status=shipment.status
    )

    return success_response(
        status_code=201,
        message="Create shipment successfully",
        data=to_dict(result),
        path=request.url.path
    )


@app.get("/shipments")
def get_shipments(
    request: Request,
    db: Session = Depends(get_db)
):

    result = get_ship(db=db)

    return success_response(
        status_code=200,
        message="Get shipments successfully",
        data=[to_dict(i) for i in result],
        path=request.url.path
    )