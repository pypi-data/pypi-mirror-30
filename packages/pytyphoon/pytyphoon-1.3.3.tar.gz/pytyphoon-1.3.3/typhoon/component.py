import asyncio


class Component:

    def __init__(self, queues_manager):
        self.queues_manager = queues_manager

    def run(self):
        self.queues_manager.start()

    def stop(self):
        self.queues_manager.stop()
        for task in asyncio.Task.all_tasks():
            try:
                task.cancel()
            except:
                pass
