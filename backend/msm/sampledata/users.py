from sqlalchemy.ext.asyncio import AsyncConnection

from msm.common.password import hash_password
from msm.sampledata.db import (
    ModelCollection,
    SampleDataModel,
)


async def make_fixture_users(conn: AsyncConnection) -> list[SampleDataModel]:
    collection = ModelCollection("user")
    collection.add(
        email="admin@example.com",
        username="admin",
        full_name="MAAS Admin",
        password=hash_password("admin"),
        is_admin=True,
    )
    collection.add(
        email="user@example.com",
        username="user",
        full_name="MAAS User",
        password=hash_password("user"),
        is_admin=False,
    )
    return await collection.create(conn)


async def purge_users(conn: AsyncConnection) -> None:
    """Delete all users"""
    return await ModelCollection("user").purge(conn)
