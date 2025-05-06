import os
import uuid
from passlib.context import CryptContext
from Model.auth_modules import UserAuthentication,UserToken
from datetime import datetime,timedelta
import time
from jwt_token import create_access_token ,decode_token
import random

pwd_context=CryptContext(schemes=["bcrypt"],deprecated="auto")

def hash_password(password: str) -> str:
    """
    Hashes a plain text password using bcrypt.

    Args:
        password (str): The plain text password.

    Returns:
        str: The hashed password.
    """
    return pwd_context.hash(password)

def verify_password(hashed_password: str, plain_password: str) -> bool:
    """
    Verifies that a plain password matches its hashed version.
    Args:
        hashed_password (str): The hashed password from the database.
        plain_password (str): The plain password entered by the user.
    Returns:
        bool: True if the password matches, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)

def signup_user(request_body,db):
    """
    Registers a new user after verifying if the username, email, or phone number 
    already exists in the database. If any of these already exist, it returns 
    an error message. Otherwise, it creates a new user record.

    Args:
        request_body: User data (username, email, phone number, password).
        db: SQLAlchemy session object.

    Returns:
        A dictionary with status code and message.
    """
    start_time = time.time()
    try:

        # Check if the username already exists
        user_exist=db.query(UserAuthentication).filter_by(username=request_body.username).first()
    
        if user_exist:
            return {"status":409,"message":f"UserName '{request_body.username}' already exist."}
        # Check if the email already exists
        email_exist=db.query(UserAuthentication).filter_by(email=request_body.email).first()
        
        if email_exist:
            return {"status":409,"message":f"Email '{request_body.email}' already exist."}
        
        # Check if the phone number already exists
        phoneno_exist=db.query(UserAuthentication).filter_by(phoneno=request_body.phoneno).first()
        
        if phoneno_exist:
            return {"status":409,"message":f"{request_body.phoneno} phone number already exist."}
        
        # Add the new user to the database
        new_user = UserAuthentication(
            username=request_body.username,
            email=request_body.email,
            phoneno=request_body.phoneno,
            is_buyer=request_body.is_buyer if request_body.is_buyer is not None else True,
            address=request_body.address,
            city=request_body.city,
            state=request_body.state,
            pincode=request_body.pincode,
            country=request_body.country,
            gender=request_body.gender,
            is_active=True,
            created_at=datetime.utcnow(),
            password=hash_password(request_body.password)
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        end_time=time.time()
        total_time = end_time - start_time
        return {
        "status_code": 201,
        "message": f"User '{request_body.username}' created successfully. Time taken: {total_time:.4f} seconds."
    }
    except Exception as e:
        print(e)
        db.rollback() 
        return {"status": 500, "message": "An error occurred while processing your request."}


def signin_user(request_body,db):
    """
    Handles user sign-in by verifying email and password.
    Args:
        request_body: An object containing user credentials (email, password).
        db: Database session for querying user data.
    Returns:
        dict: A response containing status code and message.
    """
    try:
        # 
        user=db.query(UserAuthentication).filter_by(email=request_body.email).first()
        if not user :
           
            return {
                "status":404,
                "message":f"Email:'{request_body.email}' not found."}
        
        password_verify=verify_password(user.password,request_body.password)
        
        # Verify the provided password
        if password_verify:
            user.last_login=datetime.utcnow()
            db.commit()
            data={'user_id':user.id ,'Username':user.username,'Email id':user.email,"Phone number":user.phoneno,'is_admin':user.is_admin}
            token=create_access_token(data)
            
            token_entry=UserToken(user_id=user.id,token=token)
            db.add(token_entry)
            db.commit()
            db.refresh(token_entry)
            return {
                'status':200,
                "message":f"Login successfully for email:'{request_body.email}'.",
                "data":{"access_token":token,"token_type":"Bearer"}
                }
        else:
            return {
                "status":404,
                "message":f"Incorrect Password '{request_body.password}'"
            }
    except Exception as e:
        print(e)
        return {"status": 500, "message": "An error occurred while processing your request."}


def logout_user(token,db):
    try:
        token_entry=db.query(UserToken).filter_by(token=token).first()
        if token_entry:
            db.delete(token_entry)
            db.commit()
            return {'status':200,"message":"Logout Successfully."}
        return {'status':404,'message':'Token not found.'}
    except Exception as e:
        return {"status": 500, "message": "An error occurred while processing your request."}
    
    
def password_forget(email: str, db):
    try:
        user = db.query(UserAuthentication).filter_by(email=email).first()
        if not user:
            return {'status_code':404, 'message':"User not found."}

        otp = str(random.randint(100000, 999999))
        user.email_otp = otp
        user.otp_expiry = datetime.utcnow() + timedelta(minutes=10)  # OTP valid for 10 mins
        db.commit()

        # TODO: Send OTP via email service here (SMTP, SendGrid, etc.)
        # logger.info(f"Password reset OTP for {email}: {otp}")

        return {"status": 200, "message": "OTP has been sent to your email.",'data':{'otp':otp}}
    
    except Exception as e:
        # logger.error(f"Error during password forget: {str(e)}")
        return {'status_code':500, 'message':"Internal server error."}


def password_reset(email: str, otp: str, new_password: str, db):
    try:
        user = db.query(UserAuthentication).filter_by(email=email).first()
        if not user:
            return {'status_code':404, 'message':"User not found."}

        if user.email_otp != otp:
            return {'status_code':400, 'message':"Invalid OTP."}

        if user.otp_expiry and user.otp_expiry < datetime.utcnow():
            return {'status_code':400, 'message':"OTP has expired."}

        user.password = hash_password(new_password)
        user.email_otp = None
        user.otp_expiry = None
        db.commit()

        return {"status": 200, "message": "Password reset successful."}
    
    except Exception as e:
        print(e)
        # logger.error(f"Error during password reset: {str(e)}")
        return {'status_code':500, 'message':"Internal server error."}
    
    
PROFILE_PICTURE_DIR="profile_pictures"
def user_update(token,request_body,profile_picture,db):
    try:
        
        user_id = decode_token(token)
                # Fetch the logged-in user
        user = db.query(UserAuthentication).filter_by(id=user_id).first()
        if not user:
            return {'status_code':404, 'message':"User not found."}

        # Update fields only if provided
        if request_body.username is not None:
            username_exist = db.query(UserAuthentication).filter(
                UserAuthentication.username == request_body.username,
                UserAuthentication.id != user_id
            ).first()
            if username_exist:
                return {'status_code':409, 'message':"Username already taken."}
            user.username = request_body.username

        if request_body.phoneno is not None:
            phoneno_exist = db.query(UserAuthentication).filter(
                UserAuthentication.phoneno == request_body.phoneno,
                UserAuthentication.id != user_id
            ).first()
            if phoneno_exist:
                return {'status_code':400, 'message':"Phone number already taken."}
            user.phoneno = request_body.phoneno

        # Other fields
        if request_body.is_buyer not in ('', None):
            user.is_buyer = request_body.is_buyer

        if request_body.address not in ('', None):
            user.address = request_body.address

        if request_body.city not in ('', None):
            user.city = request_body.city

        if request_body.state not in ('', None):
            user.state = request_body.state

        if request_body.pincode not in ('', None):
            user.pincode = request_body.pincode

        if request_body.country not in ('', None):
            user.country = request_body.country

        if request_body.gender not in ('', None):
            user.gender = request_body.gender

        if request_body.is_admin not in ('', None):
            user.is_admin = request_body.is_admin
        # Save profile picture if provided
        if profile_picture:
            # Ensure the profile picture directory exists
            if not os.path.exists(PROFILE_PICTURE_DIR):
                os.makedirs(PROFILE_PICTURE_DIR)

            # Save the profile picture and get the path
            profile_picture_path = save_profile_picture(profile_picture)
            user.profile_picture = profile_picture_path

        # Update timestamp
        user.updated_at = datetime.utcnow()


        db.commit()
        db.refresh(user)

        return {
            "status_code": 200,
            "message": "User updated successfully."
        }


    except Exception as e:
        print("Error:", e)
        db.rollback()
        return {'status_code':500, 'message':"An error occurred while updating the user."}

def save_profile_picture(file) -> str:
    try:
        # Get the file extension (e.g., .jpg, .png)
        file_extension = file.filename.split('.')[-1]

        # Generate a unique file name using UUID (to avoid conflicts)
        file_name = f"{uuid.uuid4()}.{file_extension}"

        # Define the file path where the image will be saved
        file_path = os.path.join(PROFILE_PICTURE_DIR, file_name)

        # Save the uploaded file to the server
        with open(file_path, "wb") as f:
            f.write(file.file.read())

        # Return the path of the saved file
        return file_path
    except Exception as e:
        return {'status_code':500, 'message':f"Error saving the file: {str(e)}"}


def user_view(token, userid, db):
    """
    Retrieve user details based on the provided token.
    If the user is an admin, they can retrieve details of another user using `userid`.
    Non-admin users can only retrieve their own details.
    Args:
        token (str): JWT token containing the user ID.
        userid (int): Optional user ID to look up (admin-only).
        db (Session): SQLAlchemy database session.
    Returns:
        dict: Response containing user details or error information.
    """
    try:
        user_id = decode_token(token)
        requesting_user = db.query(UserAuthentication).filter_by(id=user_id).first()

        if not requesting_user:
            return {
                'status_code': 404,
                'message': "User not found."
            }

        # If user is admin and a target user ID is provided, fetch that user
        if requesting_user.is_admin:
            if not userid:
                return {
                    'status_code': 400,
                    'message': "User ID is required for admin view."
                }
            target_user = db.query(UserAuthentication).filter_by(id=userid).first()
            if not target_user:
                return {
                    'status_code': 404,
                    'message': "Target user not found."
                }
        else:
            # Non-admin users can only view their own data
            target_user = requesting_user

        # Prepare user data
        user_data = {
            'fullname': target_user.username,
            'email': target_user.email,
            'phoneno': target_user.phoneno,
            'is_buyer': target_user.is_buyer,
            'address': target_user.address,
            'city': target_user.city,
            'state': target_user.state,
            'pincode': target_user.pincode,
            'gender': target_user.gender,
            'profile_picture': target_user.profile_picture
        }

        return {
            'status_code': 200,
            'message': 'User details found successfully.',
            'data': user_data
        }

    except Exception as e:
        db.rollback()
        print(f"[ERROR] user_view: {e}")
        return {
            'status_code': 500,
            'message': "An unexpected error occurred while retrieving user details."
        }

def user_list(token,page,page_size,db):
    try:
        # Decode token to get user ID
        user_id = decode_token(token)

        # Fetch the requesting user's details
        requesting_user = db.query(UserAuthentication).filter_by(id=user_id).first()

        if not requesting_user:
            return {
                'status_code': 404,
                'message': "User not found."
            }

        # Only allow admins to view the user list
        
        if requesting_user.is_admin:
            
            offset = (page - 1) * page_size

            # Query all users with pagination
            users_query = db.query(UserAuthentication).offset(offset).limit(page_size).all()
            
            users_list = [
                {
                    'fullname': user.username,
                    'email': user.email,
                    'phoneno': user.phoneno,
                    'is_buyer': user.is_buyer,
                    'address': user.address,
                    'city': user.city,
                    'state': user.state,
                    'pincode': user.pincode,
                    'gender': user.gender,
                    'profile_picture': user.profile_picture
                }
                for user in users_query
            ]

            return {
                'status_code': 200,
                'message': f"Users retrieved successfully (Page {page}).",
                'data': users_list
            }
        else:
            return {
                'status_code': 403,
                'message': "Access denied. Admin privileges required."
            }

    except Exception as e:
        db.rollback()
        print(f"[ERROR] user_list: {e}")
        return {
            'status_code': 500,
            'message': "An unexpected error occurred while retrieving user details."
        }
