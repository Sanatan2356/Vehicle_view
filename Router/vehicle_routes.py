from fastapi import APIRouter,Depends,UploadFile,File,Query
from sqlalchemy.orm import Session
from typing import Optional,Union,Literal,List
from Schemas.vehicle_schemas import VehicleSchemas,CompanyModel,CompanyUpdateModel,BrandModel,BrandUpdateModel,VehicleUpdateSchemas
from database import get_db
from Viewer.vehicle_viewer import (
    add_vehicle, upload_vehicle, vehicle_data, fetch_vehicles_from_db,
    manage_company, manage_brand, manage_model, entities_view, update_vehicle,delete_vehicle
)


vehicle_route=APIRouter(tags=['Vehicle'])

@vehicle_route.post("/add_vehicle")
def vehicle_add(token:str,request_body:VehicleSchemas=Depends(VehicleSchemas.as_form),vehicle_photos:Optional[List[UploadFile]]=File(None),db:Session=Depends(get_db)):
    return add_vehicle(token,request_body,vehicle_photos,db)

@vehicle_route.post('/upload_vehicle')
def vehicle_upload(token:str,file:UploadFile=File(...),db:Session=Depends(get_db)):
    return upload_vehicle(token,file,db)

@vehicle_route.put('/update_vehicle')
def vehicle_update(token:str,request_body:VehicleUpdateSchemas,vehicle_photos:Optional[List[UploadFile]]=File(None),db:Session=Depends(get_db)):
    return update_vehicle(token,request_body,vehicle_photos,db)

@vehicle_route.put('/delete_vehicle')
def vehicle_delte(token:str,vehicle_number:str,db:Session=Depends(get_db)):
    return delete_vehicle(token,vehicle_number,db)

@vehicle_route.get('/vehicle_details/{vehicle_id}')
def vehicle_details(token:str,vehicle_id:Optional[int]=None,db:Session=Depends(get_db)):
    return vehicle_data(token,vehicle_id,db)

@vehicle_route.post('/vehicles_list')
def get_all_vehicles(token:str,request_body:dict,  page: int = Query(1, ge=1),per_page: int = Query(5, ge=1, le=100),db:Session=Depends(get_db)):
    return fetch_vehicles_from_db(token,request_body,db,page,per_page)

@vehicle_route.post('/manage_company')
def company_manage(token:str, request_body: Union[CompanyModel, CompanyUpdateModel],operation:Literal["create", "update", "delete"] = Query(...),
db: Session = Depends(get_db)):
    return manage_company(token,request_body, db, operation)

@vehicle_route.post('/brand_manage')
def brand_manage(token:str,request_body: Union[BrandModel, BrandUpdateModel],operation:Literal["create", "update", "delete"] = Query(...),
    db: Session = Depends(get_db)):
    return manage_brand(token,request_body,db,operation)

@vehicle_route.post('/manage_model')
def model_manage(
    token:str,
    request_body: Union[BrandModel, BrandUpdateModel],
    operation: Literal["create", "update", "delete"] = Query(...),
    db: Session = Depends(get_db)
):
    return manage_model(token,request_body,db,operation)

@vehicle_route.get('/view_entities')
def view_entities(token:str,
    entity_type: Literal["model", "brand", "company"] = Query(..., alias="type"),
    page: int = Query(1, ge=1),
    per_page: int = Query(5, ge=1, le=100),
    db: Session = Depends(get_db)
):
    return entities_view(token,entity_type, db, page, per_page)

# bookmark

@vehicle_route.post("/bookmark/")
def manage_bookmark(token:str,vehicle_name:str,db:Session=Depends(get_db)):
    return bookmark_manage(token,vehicle_name,db)
