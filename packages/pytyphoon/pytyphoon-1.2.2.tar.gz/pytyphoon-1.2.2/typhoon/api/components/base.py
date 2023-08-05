class Base:

    def __init__(self, request, state):
        self.state = state
        self.component = None
        self.request = request
        self.method = self.request.method
        self.headers = self.request.headers
        self.cookies = self.request.cookies
        self.events = {}
        self.attributes = {}
        self.editable_attributes = []
        self.base_errors = {
            0: "Event not found"
        }

        self.errors = {
            0: "Attribute not found",
            100: "Attribute isn't editable",
            200: "Value not found",
            300: "Value isn't valid"
        }

    async def isValidEvent(self):
        body = await self.request.json()
        self.event = body["event"]

        if not self.events.get(self.event):
            raise Exception(self.base_errors[0])

    async def init(self):
        await self.isValidEvent()

        return await self.events[self.event]()

    def success_event(self):
        return {
            "status" : True,
            "event": self.event
        }

    def error_event(self, reason):
        return {
            "status": False,
            "event": self.event,
            "reason": reason
        }

    def validate_change(self, data):
        attribute = data.get("attribute")

        value = data.get("value")

        if not attribute:
            raise Exception(self.errors[0])

        if attribute not in self.editable_attributes:
            raise Exception(self.errors[100])

        if not value:
            raise Exception(self.errors[200])

    async def change(self):
        data = await self.request.json()

        try:
            self.validate_change(data)
            setattr(self.component, data["attribute"], int(data["value"]))
        except Exception as e:
            raise Exception(e)

        return {
            "change": True
        }
