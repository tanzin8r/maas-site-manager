from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from datetime import timedelta
import logging
import time
from typing import (
    Any,
)
from uuid import uuid4

from fastapi import (
    Request,
    Response,
)
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncConnection
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from temporalio.client import (
    Client as TemporalClient,
)
from temporalio.common import RetryPolicy
from temporalio.contrib.pydantic import pydantic_data_converter
from temporallib.client import Client, Options  # type: ignore
from temporallib.encryption import EncryptionOptions  #  type: ignore

from msm.apiserver.db import Database
from msm.common.settings import Settings
from msm.common.workflows.sync import (
    DELETE_ITEMS_WF_NAME,
    DeleteItemsParams,
    S3Params,
)

logger = logging.getLogger("uvicorn.error")


class TransactionMiddleware(BaseHTTPMiddleware):
    """Run a request in a transaction, handling commit/rollback.

    This makes the database connection available as `request.state.conn`.
    """

    def __init__(self, app: ASGIApp, db: Database):
        super().__init__(app)
        self.db = db

    @asynccontextmanager
    async def get_connection(self) -> AsyncIterator[AsyncConnection]:
        """Return the connection in a transaction context manager."""
        async with self.db.engine.begin() as conn:
            yield conn

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        async with self.get_connection() as conn:
            request.state.conn = conn
            return await call_next(request)


class DatabaseMetricsMiddleware(BaseHTTPMiddleware):
    """Track database-related metrics.

    It requires the database connection to be available as
    `request.state.conn`.
    """

    def __init__(self, app: ASGIApp, db: Database):
        super().__init__(app)
        self.db = db

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        query_metrics = {"latency": 0.0, "count": 0}
        request.state.query_metrics = query_metrics

        def before(*args: Any) -> None:
            request.state.cur_query_start = time.perf_counter()

        def after(*args: Any) -> None:
            request.state.query_metrics["latency"] += (
                time.perf_counter() - request.state.cur_query_start
            )
            request.state.query_metrics["count"] += 1
            del request.state.cur_query_start

        conn = request.state.conn.sync_connection
        event.listen(conn, "before_cursor_execute", before)
        event.listen(conn, "after_cursor_execute", after)
        try:
            return await call_next(request)
        finally:
            event.remove(conn, "before_cursor_execute", before)
            event.remove(conn, "after_cursor_execute", after)


class TemporalClientProxy:
    def __init__(self, settings: Settings):
        self._settings = settings
        self._client: TemporalClient | None = None

    async def connect(self) -> None:
        options = Options(
            host=self._settings.temporal_server_address,
            queue=self._settings.temporal_task_queue,
            namespace=self._settings.temporal_namespace,
            tls_root_cas=self._settings.temporal_tls_root_cas,
            encryption=EncryptionOptions(),
        )
        self._client = await Client.connect(
            data_converter=pydantic_data_converter, client_opt=options
        )

    def get_client(self) -> TemporalClient:
        assert self._client is not None
        return self._client


class TemporalMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, temporal: TemporalClientProxy):
        super().__init__(app)
        self.temporal = temporal

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        request.state.temporal_client = self.temporal.get_client()
        return await call_next(request)


class S3Middleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        response = await call_next(request)
        if hasattr(request.state, "ids_to_delete"):
            await self.start_delete_workflow(
                request.state.temporal_client, request.state.ids_to_delete
            )
        return response

    async def start_delete_workflow(
        self, client: TemporalClient, ids_to_delete: list[int]
    ) -> None:
        settings = Settings()
        workflow_id = f"delete-items-{uuid4()}"
        logger.info(f"Starting delete workflow (ID {workflow_id})")
        await client.start_workflow(
            DELETE_ITEMS_WF_NAME,
            DeleteItemsParams(
                S3Params(
                    settings.s3_endpoint or "",
                    settings.s3_access_key or "",
                    settings.s3_secret_key or "",
                    settings.s3_bucket or "",
                    settings.s3_path or "",
                ),
                ids_to_delete,
            ),
            id=workflow_id,
            task_queue=settings.temporal_task_queue or "not-set",
            retry_policy=RetryPolicy(  # don't spin too fast
                initial_interval=timedelta(seconds=15),
                maximum_interval=timedelta(minutes=1),
            ),
            execution_timeout=timedelta(minutes=2),
        )
