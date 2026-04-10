from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Raj Store"
    secret_key: str = "your-secret-key-change-this"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Database — individual parts, assembled in database.py
    db_host: str = "localhost"
    db_port: str = "5432"
    db_name: str = "raj_store"
    db_user: str = "raj"
    db_password: str = ""

    # For local dev with SQLite, set this to override everything above
    database_url: str = ""

    # Redis
    redis_host: str = "localhost"
    redis_port: str = "6379"
    redis_password: str = ""
    redis_url: str = ""   # override for local dev
    cache_enabled: bool = False

    # Stripe
    stripe_secret_key: str = ""
    stripe_publishable_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_success_url: str = "http://127.0.0.1:8000/orders/stripe-success"
    stripe_cancel_url: str = "http://127.0.0.1:8000/cart?error=payment_cancelled"

    # OpenTelemetry
    otel_enabled: bool = False
    otel_service_name: str = "raj-store"
    otel_exporter_otlp_endpoint: str = "http://localhost:4317"

    # OpenSearch
    opensearch_enabled: bool = False
    opensearch_url: str = "http://localhost:9200"
    opensearch_index_products: str = "products"

    class Config:
        env_file = ".env"


settings = Settings()