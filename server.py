import json

from aiohttp import web
from sqlalchemy.exc import IntegrityError

from models import Base, Session, Ads, engine


app = web.Application()


async def orm_context(app: web.Application):
    print("START")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()
    print("FINISH")


@web.middleware
async def session_middleware(request: web.Request, handler):
    async with Session() as session:
        request.session = session
        response = await handler(request)
        return response


app.cleanup_ctx.append(orm_context)
app.middlewares.append(session_middleware)


def get_http_error(error_class, message):
    error = error_class(
        body=json.dumps({"error": message}), content_type="application/json"
    )
    return error


async def get_advertisement_by_id(session: Session, advertisement_id: int):
    advertisement = await session.get(Ads, advertisement_id)
    if advertisement is None:
        raise get_http_error(web.HTTPNotFound, f"Advertisement with id {advertisement_id} not found")
    return advertisement


async def add_advertisement(session: Session, advertisement: Ads):
    try:
        session.add(advertisement)
        await session.commit()
    except IntegrityError as error:
        raise get_http_error(web.HTTPConflict, "Advertisement already exists")
    return advertisement


class AdsView(web.View):
    @property
    def advertisement_id(self):
        return int(self.request.match_info["advertisement_id"])

    @property
    def session(self) -> Session:
        return self.request.session

    async def get(self):
        advertisement = await get_advertisement_by_id(self.session, self.advertisement_id)
        return web.json_response(advertisement.dict)

    async def post(self):
        advertisement_data = await self.request.json()
        advertisement = Ads(**advertisement_data)
        advertisement = await add_advertisement(self.session, advertisement)
        return web.json_response({"id": advertisement.id})

    async def patch(self):
        advertisement = await get_advertisement_by_id(self.session, self.advertisement_id)
        advertisement_data = await self.request.json()
        for filed, value in advertisement_data.items():
            setattr(advertisement, filed, value)
        advertisement = await add_advertisement(self.session, advertisement)
        return web.json_response({"id": advertisement.id})

    async def delete(self):
        advertisement = await get_advertisement_by_id(self.session, self.advertisement_id)
        await self.session.delete(advertisement)
        await self.session.commit()
        return web.json_response({"status": "deleted"})


app.add_routes([web.post("/advertisement", AdsView)])
app.add_routes([web.get(r"/advertisement/{advertisement_id:\d+}", AdsView)])
app.add_routes([web.patch(r"/advertisement/{advertisement_id:\d+}", AdsView)])
app.add_routes([web.delete(r"/advertisement/{advertisement_id:\d+}", AdsView)])
web.run_app(app)
