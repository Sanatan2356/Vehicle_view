from fastapi import APIRouter,Depends,UploadFile,File,Query
from typing import Optional
from sqlalchemy.orm import Session
from database import get_db
from Schemas.auth_schemas import SignUp,SignIn,UpdateUserRequest
from Viewer.auth_viewer import signup_user,signin_user,logout_user,password_forget,password_reset,user_update,user_view,user_list

user_route=APIRouter(tags=['Authentication'])


@user_route.post("/user_signup")
def user_signup(request_body:SignUp,db:Session=Depends(get_db)):
    return signup_user(request_body,db)

@user_route.post("/user_signin")
def user_signin(request_body:SignIn,db:Session=Depends(get_db)):
    return signin_user(request_body,db)
        
@user_route.post("/user_logout")
def uesr_logout(token:str,db:Session=Depends(get_db)):
    return logout_user(token,db)

@user_route.post("/forget_password")
def forget_password(email:str,db:Session=Depends(get_db)):
    return password_forget(email,db)

@user_route.post("/reset_password")
def reset_password(email:str,otp:int,new_password:Optional[str]=None,db:Session=Depends(get_db)):
    return password_reset(email,otp,new_password,db)

@user_route.put('/update_user')
def update_user(token:str,request_body:UpdateUserRequest =Depends(UpdateUserRequest.as_form),profile_photo:Optional[UploadFile]=File(None),db:Session=Depends(get_db)):
    return user_update(token,request_body,profile_photo,db)

@user_route.get('/view_user')
def view_user(token: str, id: Optional[int]=  None, db: Session = Depends(get_db)):
    return user_view(token, id, db)

@user_route.get('/user_list')
def list_user(token:str,page: int = Query(1, ge=1),per_page: int = Query(5, ge=1, le=100),db:Session=Depends(get_db)):
    return user_list(token,page,per_page,db)
