"""
OpenTelemetry tracing setup. No-op when OTEL_ENABLED is false.
"""
from app.config import settings

def exclude_health_endpoints(scope):
    """Filter out health/readiness probes and metrics from traces."""
    path = scope.get("path", "")
    if path in ["/healthz", "/readyz", "/metrics"]:
        return None
    return path

def setup_telemetry(app, engine):
    """Configure OpenTelemetry tracing. Safe to call even when disabled."""
    if not settings.otel_enabled:
        print("⏭️  OpenTelemetry disabled")
        return

    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
        from opentelemetry.instrumentation.requests import RequestsInstrumentor

        resource = Resource.create({"service.name": settings.otel_service_name})
        provider = TracerProvider(resource=resource)

        exporter = OTLPSpanExporter(
            endpoint=settings.otel_exporter_otlp_endpoint,
            insecure=True,
        )
        provider.add_span_processor(BatchSpanProcessor(exporter))
        trace.set_tracer_provider(provider)

        FastAPIInstrumentor.instrument_app(app, excluded_urls="healthz,readyz,metrics")
        SQLAlchemyInstrumentor().instrument(engine=engine)
        RequestsInstrumentor().instrument()

        print(f"✅ OpenTelemetry enabled (exporting to {settings.otel_exporter_otlp_endpoint})")
    except Exception as e:
        print(f"⚠️  OpenTelemetry setup failed: {e}")