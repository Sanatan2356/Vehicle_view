import  pandas as pd
import traceback
import os
import uuid
import shutil
from fastapi import Depends
from datetime import datetime
from sqlalchemy.orm import Session
from Model.vehicle_module import Vehicle, Brand, Company, VehicleModel
from Model.auth_modules import UserAuthentication
from database import get_db
from jwt_token import decode_token


# VEHICLE 

def add_vehicle(token,request_body,vehicle_photos, db: Session):
    try:
        user_id = decode_token(token)
        user=db.query(UserAuthentication).filter_by(id= user_id).first()
        if not user:
            return {'status_code':404,"message":'User not found'}
        # Only allow admin users to add vehicles
        if not (user.is_admin or not user.is_buyer):
            return {"status_code": 403, "message": "Only admin users or sellers can add vehicles"}
        # Check if vehicle already exists
        vehicle_exist = db.query(Vehicle).filter_by(vehicle_number=request_body.vehicle_number).first()
        if vehicle_exist:
            return {
                'status': 409,
                "message": f"Vehicle with number {request_body.vehicle_number} already exists."
            }

        # Check if company exists, otherwise add it
        company = get_or_create_company(db, request_body.company, request_body.country)

        # Check if brand exists, otherwise add it
        brand = get_or_create_brand(db, request_body.brand, company.id)

        # Check if model exists, otherwise add it
        model = get_or_create_model(db, request_body.model, brand.id)

        # Add vehicle with all relationships by ID
        vehicle = Vehicle(
            vehicle_number=request_body.vehicle_number,
            company_id=company.id,       # assign company_id
            brand_id=brand.id,            # assign brand_id
            model_id=model.id,            # assign model_id
            manufacturing_year=request_body.manufacturing_year,
            fuel_type=request_body.fuel_type,
            color=request_body.color,
            vehicle_reg_date=request_body.vehicle_reg_date,
            last_service_date=request_body.last_service_date,
            mileage=request_body.mileage
        )
        
        if vehicle_photos:
            vehicle_photos_path = save_vehicle_photos(request_body.vehicle_number,vehicle_photos)
            vehicle.vehicle_photos = vehicle_photos_path
            
        db.add(vehicle)
        db.commit()
        db.refresh(vehicle)

        return {"status": 201, "message": f"Vehicle {request_body.vehicle_number} added successfully."}

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        print(traceback.format_exc())
        return {"status": 500, "message": "An unexpected error occurred. Please try again later."}
    

PHOTO_BASE_DIR='vehicle_photos'
def save_vehicle_photos(vehicle_number, files):
    folder = os.path.join(PHOTO_BASE_DIR, vehicle_number)
    os.makedirs(folder, exist_ok=True)

    saved_paths = []

    for file in files:
        ext = file.filename.split(".")[-1]
        filename = f"{uuid.uuid4()}.{ext}"
        path = os.path.join(folder, filename)

        with open(path, "wb") as f:
            f.write(file.file.read())

        saved_paths.append(path)

    return saved_paths

def get_or_create_company(db: Session, company_name: str, country: str):
    """Helper function to get or create a company."""
    company = db.query(Company).filter_by(name=company_name).first()
    if not company:
        company = Company(name=company_name, country=country)
        db.add(company)
        db.commit()
        db.refresh(company)
    return company

def get_or_create_brand(db: Session, brand_name: str, company_id: int):
    """Helper function to get or create a brand."""
    brand = db.query(Brand).filter_by(name=brand_name).first()
    if not brand:
        brand = Brand(name=brand_name, company_id=company_id)
        db.add(brand)
        db.commit()
        db.refresh(brand)
    return brand

def get_or_create_model(db: Session, model_name: str, brand_id: int):
    """Helper function to get or create a model."""
    model = db.query(VehicleModel).filter_by(name=model_name).first()
    if not model:
        model = VehicleModel(name=model_name, brand_id=brand_id)
        db.add(model)
        db.commit()
        db.refresh(model)
    return model

def vehicle_data(token,vehicle_id,db):
    try:
        user_id = decode_token(token)
        user=db.query(UserAuthentication).filter_by(id= user_id).first()
        if not user:
            return {'status_code':404,"message":'User not found'}
        
        vehicle=db.query(Vehicle).filter_by(id=vehicle_id).first()
        if vehicle:
            data={'vehicle_number':vehicle.vehicle_number,
                  'manufacturing_year':vehicle.manufacturing_year,
                  'fuel_type':vehicle.fuel_type,
                  'color':vehicle.color,
                  'vehicle_reg_date':vehicle.vehicle_reg_date,
                  'last_service_date':vehicle.last_service_date,
                  'mileage':vehicle.mileage,
                  'company':vehicle.company.name,
                  'brand':vehicle.brand.name,
                  'model':vehicle.model.name}
            return {'status_code':200,'message':'Vehicle found.','data':data}
        else:
            return {'status_code':404,'message':'Vehicle not found.'}

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        print(traceback.format_exc())
        return {"status": 500, "message": "An unexpected error occurred. Please try again later."}

def fetch_vehicles_from_db(token,request_body,db,page,per_page):
    try:
        user_id = decode_token(token)
        user=db.query(UserAuthentication).filter_by(id= user_id).first()
        if not user:
            return {'status_code':404,"message":'User not found'}
        
        offset = (page - 1) * per_page
        query = db.query(Vehicle).offset(offset).limit(per_page)
        for key, value in request_body.items():
            if hasattr(Vehicle, key):  
                query = query.filter(getattr(Vehicle, key) == value)

        vehicles_list = query.all()  
        total=total = db.query(Vehicle).count()
        data = []
        for vehicle in vehicles_list:
            data.append({
                'vehicle_number': vehicle.vehicle_number,
                'manufacturing_year': vehicle.manufacturing_year,
                'fuel_type': vehicle.fuel_type,
                'color': vehicle.color,
                'vehicle_reg_date': vehicle.vehicle_reg_date,
                'last_service_date': vehicle.last_service_date,
                'mileage': vehicle.mileage,
                'company':vehicle.company.name,
                'brand':vehicle.brand.name,
                'model':vehicle.model.name
            })
        return {"status": 200,
                 "message": "Vehicles fetched successfully.",
                "data": data,
                'pagination': {
                        'page': page,
                        'per_page': per_page,
                        'total': total
                    }}

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        print(traceback.format_exc())
        return {"status": 500, "message": "An unexpected error occurred. Please try again later."}
      
def update_vehicle(token,request_body,vehicle_photos,db):
    try:
        user_id = decode_token(token)
        user=db.query(UserAuthentication).filter_by(id= user_id).first()
        if not user:
            return {'status_code':404,"message":'User not found'}
        # Only allow admin users to add vehicles
        if not (user.is_admin or not user.is_buyer):
            return {"status_code": 403, "message": "Only admin users or sellers can add vehicles"}
        
        vehicle=db.query(Vehicle).filter_by(vehicle_number=request_body.vehicle_number).first()
        if not vehicle:
            return {'status_code':404,'message':f"Vehicle '{request_body.vehicle_number}' is not found."}
        company = db.query(Company).filter_by(name=request_body.company).first()
        if not company:
            return {'status_code': 404, 'message': f"Company '{request_body.company}' is not found."}

        brand = db.query(Brand).filter_by(name=request_body.brand).first()
        if not brand:
            return {'status_code': 404, 'message': f"Brand '{request_body.brand}' is not found."}

        model = db.query(VehicleModel).filter_by(name=request_body.model).first()
        if not model:
            return {'status_code': 404, 'message': f"Model '{request_body.model}' is not found."}

        # Conditional field updates
        if request_body.manufacturing_year not in ('', None):
            vehicle.manufacturing_year = request_body.manufacturing_year

        if request_body.fuel_type not in ('', None):
            vehicle.fuel_type = request_body.fuel_type

        if request_body.color not in ('', None):
            vehicle.color = request_body.color

        if request_body.vehicle_reg_date not in ('', None):
            vehicle.vehicle_reg_date = request_body.vehicle_reg_date

        if request_body.last_service_date not in ('', None):
            vehicle.last_service_date = request_body.last_service_date

        if request_body.mileage not in ('', None):
            vehicle.mileage = request_body.mileage

        if request_body.country not in ('', None):
            vehicle.country = request_body.country

        # Assign foreign key references
        vehicle.company_id = company.id
        vehicle.brand_id = brand.id
        vehicle.model_id = model.id
        
        if vehicle_photos:
            delete_vehicle_photo_dir(vehicle.vehicle_number)

            # 2. Save new photo files
            new_photo_paths = save_vehicle_photos(vehicle.vehicle_number, vehicle_photos)

            # 3. Update DB field
            vehicle.vehicle_photos = new_photo_paths

            db.commit()

        return {'status_code':200,'message':f"vehicle '{request_body.vehicle_number}' is updated successfully."}
         
        
                    
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        print(traceback.format_exc())
        return {"status": 500, "message": "An unexpected error occurred. Please try again later."}
        
def delete_vehicle_photo_dir(vehicle_number: str):
    photo_dir = os.path.join("vehicle_photos", vehicle_number)
    if os.path.exists(photo_dir):
        shutil.rmtree(photo_dir)
        
def delete_vehicle(token,vehicle_number,db:Session):
    try:
        user_id = decode_token(token)
        user=db.query(UserAuthentication).filter_by(id= user_id).first()
        if not user:
            return {'status_code':404,"message":'User not found'}
        # Only allow admin users to add vehicles
        if not (user.is_admin or not user.is_buyer) :
            return {"status_code": 403, "message": "Only admin users or sellers can delete vehicles"}
        vehicle=db.query(Vehicle).filter_by(vehicle_number=vehicle_number).first()
        if not vehicle :
            return {'status_code':404,'message':f"Vehicle '{vehicle_number}' not found."}
        vehicle.delete()
        db.commit()
        return {'status_code':200,'message':f"Vehicle '{vehicle_number}' is deleted successfully."}
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        print(traceback.format_exc())
        return {"status": 500, "message": "An unexpected error occurred. Please try again later."}
        
# COMPANY
def manage_company(token,request_body, db: Session, operation: str):
    try:
        user_id = decode_token(token)
        user=db.query(UserAuthentication).filter_by(id= user_id).first()
        if not user:
            return {'status_code':404,"message":'User not found'}
        # Only allow admin users to add vehicles
        if  not user.is_admin :
            return {"status_code": 403, "message": "Only admin users can add company"}
        
        
        
        
        if operation == 'create':
            company_exist = db.query(Company).filter_by(name=request_body.company_name).first()
            if company_exist:
                return {'status_code': 409, 'message': 'Company already exists.'}
            
            company = Company(name=request_body.company_name, country=request_body.country)
            db.add(company)
            db.commit()
            db.refresh(company)
            return {'status_code': 201, 'message': 'Company created successfully.'}
        
        elif operation == 'update':
            company = db.query(Company).filter_by(id=request_body.company_id).first()
            if company:
                if request_body.name:
                    company.name = request_body.name
                if request_body.country:
                    company.country = request_body.country
                db.commit()
                db.refresh(company)
                return {'status_code': 200, 'message': 'Company updated successfully.'}
            else:
                return {'status_code': 404, 'message': 'Company not found.'}
        
        elif operation == 'delete':
            company = db.query(Company).filter_by(id=request_body.company_id).first()
            if company:
                db.delete(company)
                db.commit()
                return {'status_code': 200, 'message': 'Company deleted successfully.'}
            else:
                return {'status_code': 404, 'message': 'Company not found.'}
        
        else:
            return {'status_code': 400, 'message': 'Invalid operation.'}
        
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        print(traceback.format_exc())
        return {"status_code": 500, "message": "An unexpected error occurred. Please try again later."}

# BRAND
def manage_brand(token,request_body, db, action):
    try:
        user_id = decode_token(token)
        user=db.query(UserAuthentication).filter_by(id= user_id).first()
        if not user:
            return {'status_code':404,"message":'User not found'}
        # Only allow admin users to add vehicles
        if not user.is_admin :
            return {"status_code": 403, "message": "Only admin users can add brand"}
        
        if action == 'create':
            brand_exist = db.query(Brand).filter_by(name=request_body.name).first()
            company = db.query(Company).filter_by(name=request_body.company_name).first()
            if not company:
                return {'status_code': 404, 'message': f"Company '{request_body.company_name}' not found."}
            if brand_exist:
                return {'status_code': 409, 'message': f"Brand '{request_body.name}' already exists."}
            data = Brand(name=request_body.name, company_id=company.id)
            db.add(data)
            db.commit()
            db.refresh(data)
            return {'status_code': 201, 'message': 'Brand created successfully.'}

        elif action == 'update':
            brand = db.query(Brand).filter_by(id=request_body.id).first()
            company = db.query(Company).filter_by(name=request_body.company_name).first()
            if not company:
                return {'status_code': 404, 'message': f"Company '{request_body.company_name}' not found."}
            if not brand:
                return {'status_code': 404, 'message': f"Brand with ID '{request_body.id}' not found."}
            brand.name = request_body.name
            brand.company_id = company.id
            db.commit()
            return {'status_code': 200, 'message': 'Brand updated successfully.'}

        elif action == 'delete':
            brand = db.query(Brand).filter_by(id=request_body.id).first()
            if brand:
                db.delete(brand)
                db.commit()
                return {'status_code': 200, 'message': 'Brand deleted successfully.'}
            else:
                return {'status_code': 404, 'message': 'Brand not found.'}

        else:
            return {'status_code': 400, 'message': 'Invalid action specified.'}
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        print(traceback.format_exc())
        return {"status_code": 500, "message": "An unexpected error occurred. Please try again later."}

# MODEL
def manage_model(token,request_body, db, action):
    try:
        user_id = decode_token(token)
        user=db.query(UserAuthentication).filter_by(id= user_id).first()
        if not user:
            return {'status_code':404,"message":'User not found'}
        # Only allow admin users to add vehicles
        if not user.is_admin :
            return {"status_code": 403, "message": "Only admin users can add Model"}
        
        if action == 'create':
            model = db.query(VehicleModel).filter_by(name=request_body.name).first()
            brand = db.query(Brand).filter_by(name=request_body.brand_name).first()
            if not brand:
                return {'status_code': 404, 'message': f"Brand '{request_body.brand_name}' not found."}
            if model:
                return {'status_code': 409, 'message': f"model '{request_body.name}' already exists."}
            data = Brand(name=request_body.name, brand_id=brand.id)
            db.add(data)
            db.commit()
            db.refresh(data)
            return {'status_code': 201, 'message': 'Model created successfully.'}

        elif action == 'update':
            model = db.query(VehicleModel).filter_by(id=request_body.id).first()
            brand = db.query(Brand).filter_by(name=request_body.brand_name).first()
            if not brand:
                return {'status_code': 404, 'message': f"Brand '{request_body.brand_name}' not found."}
            if not model:
                return {'status_code': 404, 'message': f"Model '{model.name}' not found."}
            model.name = request_body.name
            model.brand_id = brand.id
            db.commit()
            return {'status_code': 200, 'message': 'Model updated successfully.'}
        elif action == 'delete':
            model = db.query(VehicleModel).filter_by(id=request_body.id).first()
            if model:
                db.delete(model)
                db.commit()
                return {'status_code': 200, 'message': 'Model deleted successfully.'}
            else:
                return {'status_code': 404, 'message': 'Model not found.'}
        else:
            return {'status_code': 400, 'message': 'Invalid action specified.'}
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        print(traceback.format_exc())
        return {"status_code": 500, "message": "An unexpected error occurred. Please try again later."}

# VIEW MODEL,BRAND,COMPANY
def entities_view(token,entity_type, db, page: int = 1, per_page: int = 15):
    try:
        
        user_id = decode_token(token)
        user=db.query(UserAuthentication).filter_by(id= user_id).first()
        if not user:
            return {'status_code':404,"message":'User not found'}
        
        offset = (page - 1) * per_page
        if entity_type == 'model':
            models = db.query(VehicleModel).offset(offset).limit(per_page).all()
            total = db.query(VehicleModel).count()
            if models:
                data = [
                    {
                        'model_name': model.name,
                        'brand_name': model.brand.name
                    }
                    for model in models
                ]
                return {
                    'status_code': 200,
                    'message': 'Models fetched successfully.',
                    'data': data,
                    'pagination': {
                        'page': page,
                        'per_page': per_page,
                        'total': total
                    }
                }
            return {'status_code': 404, 'message': "Models not found."}

        elif entity_type == 'brand':
            brands = db.query(Brand).offset(offset).limit(per_page).all()
            total = db.query(Brand).count()
            if brands:
                data = [
                    {
                        'brand_name': brand.name,
                        'company_name': brand.company.name
                    }
                    for brand in brands
                ]
                return {
                    'status_code': 200,
                    'message': 'Brands fetched successfully.',
                    'data': data,
                    'pagination': {
                        'page': page,
                        'per_page': per_page,
                        'total': total
                    }
                }
            return {'status_code': 404, 'message': "Brands not found."}

        elif entity_type == 'company':
            companies = db.query(Company).offset(offset).limit(per_page).all()
            total = db.query(Company).count()
            if companies:
                data = [
                    {
                        'company_name': company.name,
                        'country': company.country
                    }
                    for company in companies
                ]
                return {
                    'status_code': 200,
                    'message': 'Companies fetched successfully.',
                    'data': data,
                    'pagination': {
                        'page': page,
                        'per_page': per_page,
                        'total': total
                    }
                }
            return {'status_code': 404, 'message': "Companies not found."}

        else:
            return {'status_code': 400, 'message': 'Invalid entity type.'}

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        print(traceback.format_exc())
        return {"status_code": 500, "message": "An unexpected error occurred. Please try again later."}

def upload_vehicle(token,file_path, db: Session):
    try:    
        user_id = decode_token(token)
        user=db.query(UserAuthentication).filter_by(id= user_id).first()
        if not user:
            return {'status_code':404,"message":'User not found'}
        # Only allow admin users to add vehicles
        if not (user.is_admin or not user.is_buyer):
            return {"status_code": 403, "message": "Only admin users or sellers can add vehicles"}
            
        df = pd.read_csv(file_path.file)
        
        for _, row in df.iterrows():
            
            # First check/create company, brand, model
            company = get_or_create_company(db, row['company'],'india')
            brand = get_or_create_brand(db, row['brand'], company.id)
            model = get_or_create_model(db, row['model'], brand.id)
            
            vehicle = Vehicle(
                vehicle_number=row['vehicle_number'],
                company_id=company.id,
                brand_id=brand.id,
                model_id=model.id,
                manufacturing_year=row['manufacturing_year'],
                fuel_type=row['fuel_type'],
                color=row['color'],
                vehicle_reg_date=datetime.strptime(row['vehicle_reg_date'], "%Y-%m-%d").date() if pd.notna(row['vehicle_reg_date']) else None,
                last_service_date=datetime.strptime(row['last_service_date'], "%Y-%m-%d").date() if pd.notna(row['last_service_date']) else None,
                mileage=row['mileage']
            )
            db.add(vehicle)
        db.commit()
        return {'status_code':201,'message':'file upload successfully.'}
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        print(traceback.format_exc())
        return {"status_code": 500, "message": "An unexpected error occurred. Please try again later."}


def bookmark_manage(token,vehicle_name,db):
    try:
        pass
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        print(traceback.format_exc())
        return {"status_code": 500, "message": "An unexpected error occurred. Please try again later."}
    

        