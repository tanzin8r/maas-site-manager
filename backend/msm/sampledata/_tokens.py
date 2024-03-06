from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncConnection

from msm.jwt import (
    JWT,
    TokenAudience,
    TokenPurpose,
)
from msm.sampledata._db import (
    ModelCollection,
    SampleDataModel,
)


async def make_fixture_tokens(
    conn: AsyncConnection, issuer: str, secret_key: str
) -> list[SampleDataModel]:
    collection = ModelCollection("token")
    for _ in range(10):
        token = JWT.create(
            issuer=issuer,
            subject=str(uuid4()),
            audience=TokenAudience.SITE,
            purpose=TokenPurpose.ENROLLMENT,
            key=secret_key,
        )
        collection.add(
            auth_id=token.subject,
            value=token.encoded,
            expired=token.expiration,
        )
    return await collection.create(conn)
