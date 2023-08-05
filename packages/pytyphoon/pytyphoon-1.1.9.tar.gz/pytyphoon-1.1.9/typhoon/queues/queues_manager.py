from typhoon.base_manager import BaseManager
from .priority_queue_collection import PriorityQueueCollection
from .simple import SimpleQueue
from .message_handler import MessageHandler


class QueuesManager(BaseManager):

    def __init__(self, config, callback):

        super().__init__(callback, config, "queues")

        self.message_handler = MessageHandler(self.config, self.on_task_handler)
        self.status = False

        self.handlers = {
            "retries": self.message_handler.on_message_retries,
            "priority": self.message_handler.on_message_priority,
            "deferred": self.message_handler.on_message_deferred
        }
        self.queues = {}
        self.init_queues()

    def init_queues(self):
        for q in self.config["queues"]:
            if q == "priority": continue
            self.queues[q] = SimpleQueue(self.config, name=q)

        self.queues["priority"] = PriorityQueueCollection(self.config)

    def add_handler(self, name, callback):
        self.handlers[name] = callback

    def init(self):
        for q in self.queues:
            if q == "priority": continue
            if self.queues[q].config_queue.get("writable"):
                self.queues[q].init_writer()

            if self.queues[q].config_queue.get("readable") and self.handlers.get(q):
                self.queues[q].set_callback(self.handlers[q])
                self.queues[q].init_reader()

    def on_task_handler(self, task):
        self.loop.create_task(self.callback(task))

    def start(self):
        self.init()
        self.status = True
        for q in self.queues:
            if self.queues[q].config_queue.get("readable"):
                self.queues[q].start()
        print("Start Manager Queues")

    def stop(self):
        self.status = False
        for q in self.queues:
            if self.queues[q].config_queue.get("readable"):
                self.queues[q].pause()
        print("Stop Manager Queues")