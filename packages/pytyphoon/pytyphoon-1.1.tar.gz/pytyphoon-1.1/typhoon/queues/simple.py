import asyncio
from .base import BaseQueue


class SimpleQueue(BaseQueue):
    def __init__(self, project_name, config, loop, name, postfix=""):
        super().__init__(project_name, config, loop, name, postfix)

    async def queue_checker(self, message):
        self.pause()
        print("##########   not priority PAUSING   ############")
        await asyncio.sleep(self.config["pause_time"])
        print("##########   not priority UNPAUSING   #########")
        self.start()

    def message_handler(self, message):
        message.enable_async()
        self.callback(message)
        if self.is_busy() and self.config["pause_time"]:
            self.loop.create_task(self.queue_checker(message))
