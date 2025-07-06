import logging
import os

from opentelemetry import trace
from opentelemetry.context import Context
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import ReadableSpan, SpanProcessor, TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased
from opentelemetry.trace import Span

from app.core.app_config import app_settings
from app.core.async_context import request_id_var

logger = logging.getLogger(__name__)


class RequestIdSpanProcessor(SpanProcessor):
    def on_start(self, span: Span, parent_context: Context | None = None) -> None:
        try:
            request_id = request_id_var.get()
            if request_id:
                span.set_attribute("request_id", request_id)
        except LookupError:
            pass

    def on_end(self, span: ReadableSpan) -> None:
        pass  # No-op


def configure_otel(app, engine):
    if os.getenv("ENABLE_OTEL", "false").lower() != "true":
        logger.info("OpenTelemetry is disabled.")
        return

    sampler = TraceIdRatioBased(app_settings.otel_sample_rate)

    tracer_provider = TracerProvider(
        sampler=sampler,
        resource=Resource.create({SERVICE_NAME: app_settings.otel_service_name}),
    )

    trace.set_tracer_provider(tracer_provider)

    # Inject request_id into all spans
    tracer_provider.add_span_processor(RequestIdSpanProcessor())

    # Choose exporter
    exporter_type = app_settings.otel_exporter
    if exporter_type == "console":
        exporter = ConsoleSpanExporter()
        logger.info("Configured OpenTelemetry with ConsoleSpanExporter.")
    else:
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
            OTLPSpanExporter,
        )

        exporter = OTLPSpanExporter(
            endpoint=app_settings.otel_exporter_otlp_endpoint,
            timeout=5,
        )
        logger.info("Configured OpenTelemetry with OTLPSpanExporter.")

    # Export spans in batches
    span_processor = BatchSpanProcessor(
        exporter,
        schedule_delay_millis=5000,
        max_export_batch_size=100,
        max_queue_size=1000,
    )
    tracer_provider.add_span_processor(span_processor)

    # Instrument FastAPI and SQLAlchemy
    FastAPIInstrumentor().instrument_app(app)
    SQLAlchemyInstrumentor().instrument(engine=engine.sync_engine)

    logger.info(
        f"OpenTelemetry tracing enabled with sample rate: {app_settings.otel_sample_rate}"
    )
