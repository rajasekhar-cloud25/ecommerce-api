from fastapi import Request, HTTPException, Depends, status
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from app.database import get_db
from app.config import settings
from app.models.user import User


class NotAuthenticatedException(Exception):
    """Raised when an HTML page request has no valid auth — triggers redirect to /login."""
    pass


def get_current_user(
        request: Request,
        db: Session = Depends(get_db)
):
    """For API endpoints — raises 401 if not authenticated."""
    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return user


def get_current_user_or_redirect(
        request: Request,
        db: Session = Depends(get_db)
):
    """For HTML pages — raises NotAuthenticatedException to trigger /login redirect."""
    try:
        return get_current_user(request, db)
    except HTTPException:
        raise NotAuthenticatedException()

def get_optional_user(request: Request, db: Session = Depends(get_db)):
    """Returns the current user if logged in, otherwise None. Never raises."""
    try:
        return get_current_user(request, db)
    except HTTPException:
        return None

def get_admin_user(
        request: Request,
        db: Session = Depends(get_db),
):
    """For admin API endpoints — requires logged in AND is_admin."""
    user = get_current_user(request, db)
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


def get_admin_user_or_redirect(
        request: Request,
        db: Session = Depends(get_db),
):
    """For admin HTML pages — redirects to /login if not logged in or not admin."""
    try:
        user = get_current_user(request, db)
    except HTTPException:
        raise NotAuthenticatedException()

    if not user.is_admin:
        raise NotAuthenticatedException()  # treat non-admin like not-authenticated

    return user