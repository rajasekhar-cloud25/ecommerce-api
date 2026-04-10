from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import UserRegister, UserLogin, UserResponse, Token
from app.services.auth_service import register_user, login_user, create_access_token
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from fastapi import Form
from app.services.email_service import send_welcome_email

router = APIRouter(prefix='/auth', tags=['Authentication'])

@router.post('/register', response_model=UserResponse)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    user = register_user(db, name=user_data.name, email=user_data.email, password=user_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    send_welcome_email(to=user.email, name=user.name)
    return user

@router.post('/login', response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = login_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    token = create_access_token({"sub": str(user.id), "email": user.email})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/login-form")
def login_form(
        request: Request,
        username: str = Form(...),
        password: str = Form(...),
        db: Session = Depends(get_db)
    ):

    user_login = login_user(db, username, password)

    if not user_login:
        return RedirectResponse(url="/login?error=1", status_code=302)

    token = create_access_token({"sub": str(user_login.id), "email": user_login.email})

    response = RedirectResponse(url="/", status_code=302)

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=1800
    )

    return response

@router.get("/logout")
def logout():
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie(key="access_token")
    return response


@router.post("/register-form")
def register_form(
        request: Request,
        name: str = Form(...),
        email: str = Form(...),
        password: str = Form(...),
        db: Session = Depends(get_db)
):

    user = register_user(db, name=name, email=email, password=password)
    if not user:
        return RedirectResponse(url="/register?error=1", status_code=302)
    send_welcome_email(to=user.email, name=user.name)
    return RedirectResponse(url="/login", status_code=302)