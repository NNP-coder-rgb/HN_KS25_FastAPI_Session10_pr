from sqlalchemy.orm import Session
from fastapi import HTTPException
from models import ShipmentModel


def create_ship(db: Session, tracking_number: str, status: str):

    checking = db.query(ShipmentModel).filter(
        ShipmentModel.tracking_number == tracking_number
    ).first()

    if checking:
        raise HTTPException(
            status_code=400,
            detail="Mã vận đơn này đã được khởi tạo trước đó"
        )

    new_ship = ShipmentModel(
        tracking_number=tracking_number,
        status=status
    )

    try:
        db.add(new_ship)
        db.commit()
        db.refresh(new_ship)
        return new_ship
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


def get_ship(db: Session):
    return db.query(ShipmentModel).all()