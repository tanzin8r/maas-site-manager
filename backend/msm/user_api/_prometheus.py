from typing import Callable

from fastapi import FastAPI
from prometheus_client import (
    CollectorRegistry,
    Counter,
    Histogram,
)
from prometheus_fastapi_instrumentator import (
    Instrumentator,
    metrics,
)


def query_metrics(
    registry: CollectorRegistry,
) -> Callable[[metrics.Info], None]:
    """Define instrumentation for tracking query metrics.

    This requires the `DatabaseMetricsMiddleware` to be installed.
    """
    queries_total = Counter(
        "db_queries_total",
        "Total number of database queries per request",
        labelnames=("handler", "method"),
        registry=registry,
    )
    queries_duration = Histogram(
        "db_queries_duration_seconds",
        "Latency of database queries per request in seconds",
        labelnames=("handler", "method"),
        buckets=(0.001, 0.005, 0.01, 0.1, 0.25, 0.5, 1.0),
        registry=registry,
    )

    def instrumentation(info: metrics.Info) -> None:
        request = info.request
        queries_total.labels(
            handler=info.modified_handler, method=info.method
        ).inc(request.state.query_metrics["count"])
        queries_duration.labels(
            handler=info.modified_handler, method=info.method
        ).observe(request.state.query_metrics["latency"])

    return instrumentation


def instrument_prometheus(
    app: FastAPI, registry: CollectorRegistry
) -> Instrumentator:
    """Instrument and expose Prometheus endpoint on the specified app."""
    return (
        Instrumentator(registry=registry, excluded_handlers=["/metrics"])
        .add(
            metrics.default(registry=registry),
            query_metrics(registry=registry),
        )
        .instrument(app)
        .expose(app)
    )
