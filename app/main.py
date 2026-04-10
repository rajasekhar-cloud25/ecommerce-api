from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.utils import get_openapi
from app.dependencies import NotAuthenticatedException
from fastapi.responses import RedirectResponse
from app.database import engine, Base, SessionLocal
from app.routers import (
    auth, product, category, cart, wishlist, address,
    order, review, pages, admin,
)

from prometheus_fastapi_instrumentator import Instrumentator
from app.otel import setup_telemetry
from app.seed_data import seed_database
from app.services.search_sync import reindex_all_products
from app.otel import setup_telemetry
# Import models so SQLAlchemy registers them before create_all
import app.models.user
import app.models.category
import app.models.product
import app.models.cart
import app.models.wishlist
import app.models.order
import app.models.review
import app.models.address

from app.seed_data import seed_database


# 1. Create tables
Base.metadata.create_all(bind=engine)


# 2. Define lifespan BEFORE creating app
@asynccontextmanager
async def lifespan(app: FastAPI):
    db = SessionLocal()
    try:
        seed_database(db)
        reindex_all_products(db)  # no-op if OpenSearch disabled
    finally:
        db.close()
    yield

# 3. Create app
app = FastAPI(
    title='Ecommerce API',
    redirect_slashes=False,
    lifespan=lifespan,
)

# 4. Set up OpenTelemetry (no-op if disabled)
setup_telemetry(app, engine)

# prometheus metrics
Instrumentator().instrument(app).expose(app)

# 4. Static + templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.exception_handler(NotAuthenticatedException)
async def auth_exception_handler(request, exc):
    return RedirectResponse(url="/login", status_code=302)


# 5. Custom OpenAPI
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Ecommerce API",
        version="1.0.0",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "Bearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method["security"] = [{"Bearer": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# 6. Routers
app.include_router(auth.router)
app.include_router(product.router)
app.include_router(category.router)
app.include_router(cart.router)
app.include_router(wishlist.router)
app.include_router(address.router)
app.include_router(order.router)
app.include_router(review.router)
app.include_router(pages.router)   # this handles GET / for the shop
app.include_router(admin.router)


# 7. Login + register pages (these stay because pages.py doesn't have them)
@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


# 9. Health endpoints for Kubernetes
@app.get("/healthz")
def health_check():
    """Liveness probe — is the app process alive?"""
    return {"status": "ok"}

@app.get("/readyz")
def readiness_check():
    """Readiness probe — is the app ready to serve traffic?"""
    return {"status": "ready"}