from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.address import AddressCreate, AddressUpdate, AddressResponse
from app.services.address_service import create_address, update_address, delete_address, get_user_addresses
from app.services.auth_dependency import get_current_user
from app.models.user import User
from app.models.address import Address
from fastapi import Form
from fastapi.responses import RedirectResponse
from app.dependencies import get_current_user_or_redirect

router = APIRouter(prefix="/address", tags=["Address"])

@router.post("/", response_model=AddressResponse)
def user_create_address(data: AddressCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    address = create_address(db, current_user.id, data)
    return address

@router.get("/", response_model=list[AddressResponse])
def user_get_addresses(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    addresses = get_user_addresses(db, current_user.id)
    if not addresses:
        raise HTTPException(status_code=404, detail="No addresses found")
    return addresses

@router.put("/{address_id}", response_model=AddressResponse)
def user_update_address(address_id: int, data: AddressUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    address = update_address(db, address_id, data)
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    return address

@router.delete("/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
def user_delete_address(address_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    address = delete_address(db, address_id)
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")

from fastapi import Form
from fastapi.responses import RedirectResponse
from app.dependencies import get_current_user_or_redirect


@router.post("/add-form")
def create_address_form(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user_or_redirect),
        first_name: str = Form(...),
        last_name: str = Form(...),
        country_code: str = Form(...),
        phone_number: str = Form(...),
        country: str = Form(...),
        state: str = Form(...),
        city: str = Form(...),
        zip_code: str = Form(...),
        address: str = Form(...),
        is_default: bool = Form(False),
):
    # If this is the user's first address, make it default automatically
    existing = get_user_addresses(db, current_user.id)
    if not existing:
        is_default = True

    new_address = Address(
        user_id=current_user.id,
        first_name=first_name.lower(),
        last_name=last_name.lower(),
        country_code=country_code,
        phone_number=phone_number,
        country=country,
        state=state,
        city=city,
        zip_code=zip_code,
        address=address,
        is_default=is_default,
    )
    db.add(new_address)
    db.commit()
    db.refresh(new_address)

    # Redirect to checkout if came from there, else back to addresses page
    return RedirectResponse(url="/addresses?added=1", status_code=302)


@router.post("/delete-form")
def delete_address_form(
        address_id: int = Form(...),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user_or_redirect),
):
    delete_address(db, address_id)
    return RedirectResponse(url="/addresses", status_code=302)


@router.post("/set-default-form")
def set_default_address_form(
        address_id: int = Form(...),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user_or_redirect),
):
    # Unset any existing default
    addresses = get_user_addresses(db, current_user.id)
    for addr in addresses:
        addr.is_default = (addr.id == address_id)
    db.commit()
    return RedirectResponse(url="/addresses", status_code=302)