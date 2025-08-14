import os


def setup_otel(app=None):
    """
    Optional OpenTelemetry bootstrap. No-ops if OTEL_EXPORTER_OTLP_ENDPOINT is unset.
    Provides:
      - FastAPI auto-instrumentation (traces)
      - OTLP/HTTP exporter (endpoint + headers via env)
    """
    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    if not endpoint:
        return  # disabled

    # Lazy imports so this file is safe when deps are missing
    from opentelemetry import metrics, trace
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.exporter.otlp.proto.http.metric_exporter import (
        OTLPMetricExporter,
    )
    from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

    svc_name = os.getenv("OTEL_SERVICE_NAME", "xo-core")
    resource = Resource.create({"service.name": svc_name})

    # Traces
    tp = TracerProvider(resource=resource)
    headers = os.getenv(
        "OTEL_EXPORTER_OTLP_HEADERS"
    )  # e.g. "Authorization=Bearer <token>"
    span_exporter = OTLPSpanExporter(
        endpoint=endpoint,
        headers=dict(h.split("=", 1) for h in headers.split(",")) if headers else None,
    )
    tp.add_span_processor(BatchSpanProcessor(span_exporter))
    trace.set_tracer_provider(tp)

    # Metrics (optional)
    mp = MeterProvider(
        resource=resource,
        metric_readers=[
            PeriodicExportingMetricReader(OTLPMetricExporter(endpoint=endpoint))
        ],
    )
    metrics.set_meter_provider(mp)

    # FastAPI autoinstrumentation
    if app is not None:
        FastAPIInstrumentor.instrument_app(app)
