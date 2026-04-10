from datetime import datetime
from typing import Optional
from typing_extensions import Annotated
from pydantic import BaseModel, StringConstraints

class AddressCreate(BaseModel):
    first_name: Annotated[str, StringConstraints(min_length=4, to_lower=True)]
    last_name: Annotated[str, StringConstraints(min_length=4, to_lower=True)]
    phone_number: Annotated[str, StringConstraints(pattern=r'^\d{7,15}$')]
    country_code: str
    country: str
    state: str
    city: str
    zip_code: str
    address: str
    is_default: bool

    class Config:
        from_attributes = True


class AddressResponse(BaseModel):
    id: int
    user_id: int
    first_name: str
    last_name: str
    country_code: Optional[str] = None
    phone_number: str
    country: str
    state: str
    city: str
    zip_code: str
    address: str
    is_default: bool
    created_at: datetime

    class Config:
        from_attributes = True


class AddressUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    country_code: Optional[str] = None
    phone_number: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    zip_code: Optional[str] = None
    address: Optional[str] = None
    is_default: Optional[bool] = None

    class Config:
        from_attributes = True

