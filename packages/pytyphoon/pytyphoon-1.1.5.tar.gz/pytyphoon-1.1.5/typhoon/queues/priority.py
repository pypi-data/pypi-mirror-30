from .base import BaseQueue


class PriorityQueue(BaseQueue):
    def __init__(self, project_name, config, loop, name, postfix):
        super().__init__(project_name, config, loop, name, postfix)

    def message_handler(self, message):
        message.enable_async()
        self.callback(message)
