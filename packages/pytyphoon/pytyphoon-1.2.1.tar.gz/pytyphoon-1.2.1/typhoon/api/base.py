import random
import json
from aiohttp import web

class BaseApi:
    def __init__(self, loop, state):
        self.loop = loop
        self.state = state
        self.components = {}
        self.app = web.Application()

        self.errors = {
            0: "Format isn't json",
            100: "Component isn't valid",
            200: "Event not found"
        }

    def init_router(self):
        pass

    def up(self):
        self.init_router()
        # ports = [it for it in range(8080, 8090)]
        # web.run_app(self.app, port=random.choice(ports))
        web.run_app(self.app)

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


