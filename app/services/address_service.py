from sqlalchemy.orm import Session
from app.models.address import Address

def create_address(db: Session, user_id: int, data):
    address = Address(
        user_id = user_id,
        address = data.address,
        city = data.city,
        state = data.state,
        zip_code = data.zip_code,
        country = data.country,
        first_name = data.first_name,
        last_name = data.last_name,
        phone_number = data.phone_number,
        is_default = data.is_default
    )
    db.add(address)
    db.commit()
    db.refresh(address)
    return address

def get_user_addresses(db: Session, user_id: int):
    return db.query(Address).filter(Address.user_id == user_id).all()


def update_address(db: Session, address_id: int, data):
    address = db.query(Address).filter(Address.id == address_id).first()

    if not address:
        return None
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(address, field, value)

    db.commit()
    db.refresh(address)
    return address

def delete_address(db: Session, address_id: int):
    address = db.query(Address).filter(Address.id == address_id).first()
    if not address:
        return None
    db.delete(address)
    db.commit()
    return address



