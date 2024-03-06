from datetime import timedelta
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncConnection

from msm.sampledata._db import (
    ModelCollection,
    SampleDataModel,
)
from msm.time import now_utc


async def make_fixture_sites(conn: AsyncConnection) -> list[SampleDataModel]:
    collection = ModelCollection("site")
    collection.add(
        city="London",
        postal_code="SE1 1JA",
        country="GB",
        coordinates=(-0.092200, 51.501990),
        name="Canonical Group Limited",
        note="4th Floor",
        state="",
        address="201 Borough High Street",
        timezone="Europe/London",
        url="https://london.canonical.example.com",
        accepted=True,
        auth_id=uuid4(),
    )
    collection.add(
        city="Austin",
        postal_code="TX 78701",
        country="US",
        coordinates=(-97.741057, 30.269612),
        name="Canonical USA Inc.",
        note="Perry Brooks Building - Suite 300",
        state="",
        address="720 Brazos Street",
        timezone="America/Chicago",
        url="https://austin.canonical.example.com",
        accepted=True,
        auth_id=uuid4(),
    )
    collection.add(
        city="Boston",
        postal_code="MA 024251",
        country="US",
        coordinates=(-71.059615, 42.358859),
        name="Canonical USA Inc. 001",
        note="Suite 210",
        state="",
        address="18 Tremont Street",
        timezone="America/Chicago",
        url="https://boston.canonical.example.com",
        accepted=True,
        auth_id=uuid4(),
    )
    collection.add(
        city="Shanghai",
        postal_code="200030",
        country="CN",
        coordinates=(121.436829, 31.187270),
        name="Canonical China",
        note="上海市漕溪北路331号12楼1246室",
        state="",
        address="No. 331 North Caoxi Road",
        timezone="Asia/Shanghai",
        url="https://shanghai.canonical.example.com",
        accepted=False,
        auth_id=uuid4(),
    )
    collection.add(
        city="Beijing",
        postal_code="100004",
        country="CN",
        coordinates=(116.448690, 39.908447),
        name="Canonical China 001",
        note="China World Office 1; 北京市朝阳区建国门外大街1号国贸写字楼1座11层1118-19室",
        state="Chaoyang District",
        address="1 Jianguomenwai Avenue",
        timezone="Asia/Shanghai",
        url="https://shanghai.canonical.example.com",
        accepted=True,
        auth_id=uuid4(),
    )
    collection.add(
        city="Taipei City",
        postal_code="號12 樓",
        country="TW",
        coordinates=(121.543406, 25.058098),
        name="Canonical Group Limited - Taiwan Branch",
        note="105402 台北市松山區民生東路三段100",
        state="Songshan Dist.",
        address="12F.,No. 100,Sec. 3,Minsheng E. Rd.",
        timezone="Asia/Taipei",
        url="https://taiwan.canonical.example.com",
        accepted=True,
        auth_id=uuid4(),
    )
    collection.add(
        city="Douglas",
        postal_code="IM99 1TT",
        country="IM",
        coordinates=(-4.481012, 54.153072),
        name="Canonical Limited",
        note="2nd Floor - Clarendon House",
        state="",
        address="ictoria Street",
        timezone="Europe/London",
        url="https://canonical.example.com",
        accepted=False,
        auth_id=uuid4(),
    )
    collection.add(
        city="Tokyo",
        postal_code="100-0014",
        country="JP",
        coordinates=(139.740669, 35.673242),
        name="Canonical Japan K.K",
        note="3rd Floor - Sanno Park Tower",
        state="",
        address="2-11-1 Nagata-cho Chiyoda-ku",
        timezone="Japan",
        url="https://japan.canonical.example.com",
        accepted=True,
        auth_id=uuid4(),
    )
    collection.add(
        city="Tokyo",
        postal_code="100-0014",
        country="JP",
        coordinates=(139.740669, 35.673242),
        name="Canonical Japan K.K",
        note="Duplicate",
        state="",
        address="2-11-1 Nagata-cho Chiyoda-ku",
        timezone="Japan",
        url="https://japan.canonical.example.com",
        accepted=True,
        auth_id=uuid4(),
    )
    sites = await collection.create(conn)

    collection = ModelCollection("site_data")

    now = now_utc()
    collection.add(
        site_id=sites[0].id,
        machines_allocated=10,
        machines_deployed=1,
        machines_ready=8,
        machines_error=1,
        machines_other=2,
        last_seen=now - timedelta(minutes=10),
    )
    collection.add(
        site_id=sites[1].id,
        machines_allocated=11,
        machines_deployed=0,
        machines_ready=8,
        machines_error=3,
        machines_other=0,
        last_seen=now - timedelta(seconds=30),
    )
    collection.add(
        site_id=sites[2].id,
        machines_allocated=12,
        machines_deployed=2,
        machines_ready=4,
        machines_error=6,
        machines_other=1,
        last_seen=now - timedelta(hours=1),
    )
    collection.add(
        site_id=sites[3].id,
        machines_allocated=13,
        machines_deployed=0,
        machines_ready=13,
        machines_error=0,
        machines_other=0,
        last_seen=now - timedelta(seconds=5),
    )
    collection.add(
        site_id=sites[4].id,
        machines_allocated=14,
        machines_deployed=13,
        machines_ready=1,
        machines_error=0,
        machines_other=4,
        last_seen=now - timedelta(days=1),
    )
    collection.add(
        site_id=sites[5].id,
        machines_allocated=15,
        machines_deployed=2,
        machines_ready=10,
        machines_error=3,
        machines_other=7,
        last_seen=now - timedelta(minutes=20),
    )
    await collection.create(conn)
    return sites
