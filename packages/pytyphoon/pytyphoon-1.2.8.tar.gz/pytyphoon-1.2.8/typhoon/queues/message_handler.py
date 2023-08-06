import asyncio
from typhoon.tasks.async import AsyncTask


class MessageHandler:
    def __init__(self, config, callback):
        self.callback = callback
        self.loop = asyncio.get_event_loop()
        self.config = config

    def prepare_task(self, task):
        self.loop.create_task(self.init_task(task))

    def on_message(self, qname, message):
        task = AsyncTask(message, self.config, qname)
        self.prepare_task(task)

    async def init_task(self, task):
        await task.init()
        self.callback(task)
