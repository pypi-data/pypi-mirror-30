import asyncio
from typhoon.tasks.async import AsyncTask


class MessageHandler:
    def __init__(self, config, callback):
        self.callback = callback
        self.loop = asyncio.get_event_loop()
        self.config = config

    def prepare_task(self, task):
        self.loop.create_task(task.fetching())
        self.loop.create_task(self.init_task(task))

    def on_message_retries(self, message):
        task = AsyncTask(message, self.config, "retries")
        self.prepare_task(task)

    def on_message_priority(self, message):
        task = AsyncTask(message, self.config, "priority")
        self.prepare_task(task)

    def on_message_deferred(self, message):
        task = AsyncTask(message, self.config, "deferred")
        self.prepare_task(task)

    async def init_task(self, task):
        await task.init()
        self.callback(task)
