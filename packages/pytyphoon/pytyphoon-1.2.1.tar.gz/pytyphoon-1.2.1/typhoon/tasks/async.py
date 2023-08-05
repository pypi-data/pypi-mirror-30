from .base import BaseTask
import asyncio
import time
import json


class AsyncTask(BaseTask):
    def __init__(self, message, config, type_):
        self.type = type_
        self.message = message
        self.fetching_flag = True
        super().__init__(config, json.loads(message.body))

        self.config_queue = self.config.queues[self.type]

        self.max_retries = self.task["fetch"].get("max_retries", self.config["max_retries"])
        self.max_failed = self.task["fetch"].get("max_failed", self.config["max_failed"])  # max number of retries with 599 status only
        self.max_processor_retries = self.task["fetch"].get("max_processor_retries", self.config["max_processor_retries"])
        self.retries_delay = self.task["fetch"].get("retries_delay", self.config["default_retries_delay"])  # in seconds

    async def init(self):
        await self.set_proxy()
        self.set_error_response()
        self.set_timestamp()
        self.set_lines_limit()
        self.set_system_save()
        self.set_retries()
        self.set_failed()
        self.set_processor_retries()

    async def retry(self, status_code):
        await self.set_proxy(retry_flag=True)
        self.set_timestamp()
        self.task["fetch"]["save"]["system"].update([
            ("status_code", status_code),
            ("added_at", self.added_at),
            ("retries_delay", self.retries_delay),
            ("execute_at", self.added_at + self.retries_delay)
        ])
        self.update_retries_counter(status_code)

    def update_retries_counter(self, status_code):
        if status_code == 599:
            self.failed += 1
            self.task["fetch"]["save"]["system"]["failed"] = self.failed
        elif status_code == 200 and self.error_response:
            self.processor_retries += 1
            self.task["fetch"]["save"]["system"]["processor_retries"] = self.processor_retries
        else:
            self.retries += 1
            self.task["fetch"]["save"]["system"]["retries"] = self.retries

    def done(self):
        finished_at = time.time()
        self.task["fetch"]["save"]["system"].update([
            ("added_at", self.added_at),
            ("finished_at", finished_at),
            ("fetching_duration", finished_at - self.added_at)
        ])
        self.fetching_flag = False
        self.message.finish()

    async def fetching(self):
        while self.fetching_flag:
            self.message.touch()
            await asyncio.sleep(self.get_latency())

    def get_latency(self):
        return self.config_queue["msg_timeout"] - 1

    def set_system_save(self):
        if "system" not in self.task["fetch"]["save"]:
            self.task["fetch"]["save"]["system"] = {}

    def set_exception_definition(self, exception, error_def):
        type_, message = exception
        self.task["fetch"]["save"]["system"]["exception"] = {

            "type": str(type_) if type_ is not None else None,
            "message": str(message) if message is not None else None,
            "error_definition": error_def
        }

    def set_error_response(self):
        self.error_response = self.task.get("processor", {}).get("error_response", False)

    def set_lines_limit(self):
        """this attribute is used while streaming to set how much
        lines will be yielded from generator at once"""
        self.lines_limit = self.task["fetch"].get("lines_limit", 50)

    def set_retries(self):
        """all bad statuses except 599"""
        self.retries = self.task["fetch"]["save"]["system"].get("retries", 0)

    def set_failed(self):
        """599 status only"""
        self.failed = self.task["fetch"]["save"]["system"].get("failed", 0)

    def set_processor_retries(self):
        """successful status but wrong content has been
        detected by processor. e.g. google captcha"""
        self.processor_retries = self.task["fetch"]["save"]["system"].get("processor_retries", 0)