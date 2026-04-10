from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Raj Store"
    secret_key: str = "your-secret-key-change-this"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Database — defaults to SQLite for local dev, PostgreSQL in production via env var
    database_url: str = "sqlite:///db.ecommerce.db"

    # Redis cache
    redis_url: str = "redis://localhost:6379/0"
    cache_enabled: bool = False  # set True in production

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

    # OpenSearch (for log shipping)
    opensearch_enabled: bool = False
    opensearch_url: str = "http://localhost:9200"
    opensearch_index: str = "raj-store-logs"

    class Config:
        env_file = ".env"


settings = Settings()