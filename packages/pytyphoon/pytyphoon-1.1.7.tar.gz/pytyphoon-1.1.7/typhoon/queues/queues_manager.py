from typhoon.base_manager import BaseManager
from .priority_queue_collection import PriorityQueueCollection
from .simple import SimpleQueue
from .message_handler import MessageHandler


class QueuesManager(BaseManager):

    def __init__(self, config, fetcher_callback):

        super().__init__(fetcher_callback, config, "queues")

        self.status = False

        self.readable_queues = (
            "priority",
            "deferred",
            "retries"
        )

        self.queues = {
            "retries": SimpleQueue(self.config, name="retries"),
            "results": SimpleQueue(self.config, name="results"),
            "deferred": SimpleQueue(self.config, name="deferred"),
            "exceptions": SimpleQueue(self.config, name="exceptions"),
            "priority": PriorityQueueCollection(self.config)
        }

        self.message_handler = MessageHandler(self.config, self.on_task_handler)

    def init(self):

        self.queues["priority"].set_callback(self.message_handler.on_message_priority)

        self.queues["deferred"].set_callback(self.message_handler.on_message_deferred)
        self.queues["deferred"].init_writer()
        self.queues["deferred"].init_reader()

        self.queues["retries"].set_callback(self.message_handler.on_message_retries)
        self.queues["retries"].init_writer()
        self.queues["retries"].init_reader()

        # Only write
        self.queues["exceptions"].init_writer()
        self.queues["results"].init_writer()

    def on_task_handler(self, task):
        # print(time.time() - self.start_time)
        self.loop.create_task(self.callback(task))

    def start(self):
        self.init()
        # self.start_time = time.time()
        self.status = True
        print("Start Manager Queues")
        self.queues["deferred"].start()
        self.queues["priority"].start()
        self.queues["retries"].start()
        # self.init_queue_checkers()

    def stop(self):
        self.status = False
        print("Stop Manager Queues")
        self.queues["deferred"].pause()
        self.queues["retries"].pause()
        self.queues["priority"].pause()
