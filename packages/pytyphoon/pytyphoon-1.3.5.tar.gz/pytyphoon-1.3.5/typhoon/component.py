import asyncio
from typhoon.queues.queues_manager import QueuesManager


class BaseComponent:

    def __init__(self, config):
        self.loop = asyncio.get_event_loop()
        self.config = config
        self.queues_manager = QueuesManager(self.config, self.on_message)

    def on_message(self, queue_name, message):
        raise NotImplementedError

    def run(self):
        self.queues_manager.start()

    def stop(self):
        self.queues_manager.stop()
        for task in asyncio.Task.all_tasks():
            try:
                task.cancel()
            except:
                pass
