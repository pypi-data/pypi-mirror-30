import random
import json
from aiohttp import web
import socket
import asyncio
import aiohttp
class BaseApi:
    def __init__(self, state):
        self.loop = asyncio.get_event_loop()
        self.state = state
        self.components = {}
        self.app = web.Application()
        self.port = None
        self.errors = {
            0: "Format isn't json",
            100: "Component isn't valid",
            200: "Event not found"
        }

    def init_router(self):
        pass

    async def request_register(self, session):
        register_service = self.state["register_service"]
        async with session.post("http://{}:{}".format(register_service["host"], register_service["port"]), json={
            "component":"registration",
            "event":"register",
            "additional":{
                "component": self.state["component_name"],
                "port": self.port,
            }
        }) as response:
            return response, await response.read()

    async def register_component(self):

        async with aiohttp.ClientSession() as session:
            response, content = await self.request_register(session)

    def up(self):
        self.init_router()
        self.port = self.get_port()
        if self.state["register_service"]:
            self.loop.create_task(self.register_component())

        web.run_app(self.app, port=self.port)

    def get_port(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        port = None
        for p in range(8000, 65535):
            try:
                s.bind(("", int(p)))
                s.listen(1)
                port = s.getsockname()[1]
                s.close()
                break
            except Exception as e:
                continue
        return port

    def close(self):
        self.app.shutdown()

    async def handler(self, request):

        response = None

        try:
            await self.isValidRequest(request)
            body = await request.json()
            controller = self.components[body["component"]](request, self.state)
            response = await controller.init()

        except Exception as e:

            return self.sendError(e)

        return web.Response(text=json.dumps(response), headers={
            "Content-Type": "application/json"
        })

    async def isValidRequest(self, request):

        body = None

        try:
            body = await request.json()
        except:
            raise Exception(self.errors[0])

        component = body.get('component')
        event = body.get("event")

        if not self.components.get(component):
            raise Exception(self.errors[100])

        if not event:
            raise Exception(self.errors[200])

    def sendError(self, e):
        error = self.getError(e)
        return web.Response(text=json.dumps(error), headers={
            "Content-Type": "application/json"
        })

    def getError(self, e):
        return {
            "status": False,
            "message": str(e)
        }