from collections.abc import Callable

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
        labelnames=("method", "handler", "status"),
        registry=registry,
    )
    queries_duration = Histogram(
        "db_queries_duration_seconds",
        "Latency of database queries per request in seconds",
        labelnames=("method", "handler", "status"),
        buckets=(0.001, 0.005, 0.01, 0.1, 0.25, 0.5, 1.0),
        registry=registry,
    )

    def instrumentation(info: metrics.Info) -> None:
        request = info.request
        queries_total.labels(
            method=info.method,
            handler=info.modified_handler,
            status=info.modified_status,
        ).inc(request.state.query_metrics["count"])
        queries_duration.labels(
            method=info.method,
            handler=info.modified_handler,
            status=info.modified_status,
        ).observe(request.state.query_metrics["latency"])

    return instrumentation


def instrument_prometheus(
    registry: CollectorRegistry,
    app: FastAPI,
    *sub_apps: FastAPI,
) -> Instrumentator:
    """Instrument and expose Prometheus endpoint on the specified app."""
    i = Instrumentator(registry=registry, excluded_handlers=["/metrics"])
    i.add(
        metrics.default(registry=registry),
        query_metrics(registry=registry),
    )
    for a in sub_apps:
        i.instrument(a)

    return i.expose(app)
