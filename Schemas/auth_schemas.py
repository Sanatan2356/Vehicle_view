from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from fastapi import Form
class SignUp(BaseModel):
    fullname:str
    email:str
    phoneno:Optional[int]
    is_buyer:Optional[bool]
    password:str
    confirm_password:str

class VerifyMobile(BaseModel):
    phoneno:int
    otp:str

class LocationCreate(BaseModel):
    phone_number:int
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    pincode: Optional[str]
    country: Optional[str]


class SignIn(BaseModel):
    email:Optional[str]
    phone_number:Optional[int]
    password:Optional[str]



class UpdateUserRequest(BaseModel):
    username: Optional[str] = None
    phoneno: Optional[int] = None
    is_buyer: Optional[bool] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    country: Optional[str] = None
    gender: Optional[str] = None
    is_admin: Optional[bool] = None

    @classmethod
    def as_form(
        cls,
        username: Optional[str] = Form(None),
        phoneno: Optional[int] = Form(None),
        is_buyer: Optional[bool] = Form(None),
        address: Optional[str] = Form(None),
        city: Optional[str] = Form(None),
        state: Optional[str] = Form(None),
        pincode: Optional[str] = Form(None),
        country: Optional[str] = Form(None),
        gender: Optional[str] = Form(None),
        is_admin: Optional[bool]= Form(None)
    ):
        return cls(
            username=username,
            phoneno=phoneno,
            is_buyer=is_buyer,
            address=address,
            city=city,
            state=state,
            pincode=pincode,
            country=country,
            gender=gender,
            is_admin=is_admin
        )

