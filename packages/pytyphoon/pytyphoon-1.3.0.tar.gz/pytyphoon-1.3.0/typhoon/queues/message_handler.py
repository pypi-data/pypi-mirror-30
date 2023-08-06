import asyncio
from typhoon.tasks.async import AsyncTask


class MessageHandler:
    def __init__(self, config, callback):
        self.callback = callback
        self.loop = asyncio.get_event_loop()
        self.config = config

    def on_message(self, qname, message):
        self.callback(qname, message)
