from typhoon.base_manager import BaseManager
from .priority_queue_collection import PriorityQueueCollection
from .simple import SimpleQueue

class QueuesManager(BaseManager):

    def __init__(self, config, callback):

        super().__init__(callback, config, "queues")

        self.status = False
        self.queues = {}
        self.init_queues()

    def init_queues(self):
        for q in self.config["queues"]:
            if q == "priority": continue
            self.queues[q] = SimpleQueue(self.config, name=q)

        self.queues["priority"] = PriorityQueueCollection(self.config)
        self.queues["priority"].set_callback(self.on_message)

    def get_topic_queues(self):
        queues = []
        for q in self.queues:
            if q == "priority": continue
            queues.append(self.queues[q].topic)

        for p in self.queues["priority"].priorities:
            q = self.queues["priority"].priorities[p]
            queues.append(q.topic)

        return queues

    def init(self):
        for q in self.queues:
            if q == "priority": continue
            if self.queues[q].config_queue.get("writable"):
                self.queues[q].init_writer()

            if self.queues[q].config_queue.get("readable"):
                self.queues[q].set_callback(self.on_message)
                self.queues[q].init_reader()

    def on_message(self, qname, task):
        self.loop.create_task(self.callback(qname, task))

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