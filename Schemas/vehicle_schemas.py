from pydantic import BaseModel
from datetime import date,datetime
from typing import Optional
from fastapi import Form

class VehicleSchemas(BaseModel):
    vehicle_number:str	
    company:str
    model:str
    manufacturing_year :int
    brand:str
    fuel_type:str
    color:str
    vehicle_reg_date:date
    last_service_date:date
    mileage	:float
    country:str
    
    @classmethod
    def as_form(
        cls,
        vehicle_number:str	= Form(None),
        company:str= Form(None),
        model:str= Form(None),
        manufacturing_year :int= Form(None),
        brand:str = Form(None),
        fuel_type:str = Form(None),
        color:str= Form(None),
        vehicle_reg_date:date= Form(None),
        last_service_date:date= Form(None),
        mileage	:float= Form(None),
        country:str= Form(None)
        ):
        
        return cls(vehicle_number=vehicle_number,
                   company=company,
                   model=model,
                   manufacturing_year=manufacturing_year,
                   brand=brand,
                   fuel_type=fuel_type,
                   color=color,
                   vehicle_reg_date=vehicle_reg_date,
                   last_service_date=last_service_date,
                   mileage=mileage,
                   country=country)

class VehicleUpdateSchemas(BaseModel):
    vehicle_number:str	
    company:Optional[str]=None
    model:Optional[str]=None
    manufacturing_year :Optional[int]=None
    brand:Optional[str]=None
    fuel_type:Optional[str]=None
    color:Optional[str]=None
    vehicle_reg_date:Optional[date]=None
    last_service_date:Optional[date]=None
    mileage	:Optional[float]=None
    country:Optional[str]=None

    @classmethod
    def as_form(
        cls,
        vehicle_number:str	= Form(None),
        company:str= Form(None),
        model:str= Form(None),
        manufacturing_year :int= Form(None),
        brand:str = Form(None),
        fuel_type:str = Form(None),
        color:str= Form(None),
        vehicle_reg_date:date= Form(None),
        last_service_date:date= Form(None),
        mileage	:float= Form(None),
        country:str= Form(None)
        ):
        
        return cls(vehicle_number=vehicle_number,
                   company=company,
                   model=model,
                   manufacturing_year=manufacturing_year,
                   brand=brand,
                   fuel_type=fuel_type,
                   color=color,
                   vehicle_reg_date=vehicle_reg_date,
                   last_service_date=last_service_date,
                   mileage=mileage,
                   country=country)


class CompanyModel(BaseModel):
    name:str
    country:str

class CompanyUpdateModel(BaseModel):
    id:str
    name:Optional[str]=None
    country:Optional[str]=None


class BrandModel(BaseModel):
    name: str
    company_name: str

    class Config:
        orm_mode = True

class BrandUpdateModel(BaseModel):
    id: int
    name: Optional[str] = None
    company_name: Optional[int] = None

    class Config:
        orm_mode = True

class VehicleModelModel(BaseModel):
    name: str
    brand_id: int

    class Config:
        orm_mode = True

class VehicleModelUpdateModel(BaseModel):
    id: int
    name: Optional[str] = None
    brand_id: Optional[int] = None

    class Config:
        orm_mode = True