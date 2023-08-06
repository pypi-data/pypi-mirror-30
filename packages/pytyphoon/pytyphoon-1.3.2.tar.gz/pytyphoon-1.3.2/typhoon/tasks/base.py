import time
import json


class BaseTask:
    def __init__(self, config, task, type_):

        self.type = type_
        self.config = config
        self.task = task
        self.url = self.task["url"]
        self.added_at = time.time()
        self.created_at = time.time()
        self.task_id = self.task["taskid"]

    def serialize(self):
        return json.dumps(self.task)

    def set_timestamp(self):
        self.added_at = time.time()
