from typhoon.proxy import Proxy
import time
import json
import asyncio


class BaseTask:
    def __init__(self, config, task):
        self.failed = 0
        self.retries = 0

        self.config = config
        self.task = task
        self.url = self.task["url"]
        self.added_at = time.time()
        self.created_at = time.time()
        self.task_id = self.task.get("taskid", "")
        self.data = self.task["fetch"].get("data")
        self.strategy = self.task["fetch"]["strategy"]
        self.save = self.task["fetch"].get("save", {})
        self.headers = self.task["fetch"].get("headers")
        self.user_agent_required = self.task["fetch"].get("user_agent_required", False)
        self.user_agent_type = self.task["fetch"].get("user_agent_required", "desktop")
        self.cookies = self.task["fetch"].get("cookies")
        self.stream = self.task["fetch"].get("stream", False)
        self.method = self.task["fetch"].get("method", "GET").upper()
        self.timeout = self.task["fetch"].get("timeout", self.config["task_timeout"])
        self.user_agent_checker()

    def reset_retries(self):
        self.retries = 0

    def reset_failed(self):
        self.failed = 0

    def serialize(self):
        return json.dumps(self.task)

    def get_user_agent_mobile(self):
        return "some mobile agent"

    def get_user_agent_tablet(self):
        return "some tablet agent"

    def get_user_agent_desktop(self):
        return "some desktop agent"

    def set_user_agent(self):
        self.user_agent_choice = {
            "desktop": self.get_user_agent_desktop,
            "tablet": self.get_user_agent_tablet,
            "mobile": self.get_user_agent_mobile
        }
        self.headers["User-Agent"] = self.user_agent_choice[self.user_agent_type]()

    def user_agent_checker(self):
        if not self.headers and self.user_agent_required:
            self.headers = {}
        if self.user_agent_required and not self.headers.get("User-Agent"):
            self.set_user_agent()

    async def set_proxy(self, retry_flag=False):
        self.proxy = self.task["fetch"].get("proxy") if not retry_flag else None
        if self.task["fetch"].get("is_proxy_required"):
            while not self.proxy:
                self.proxy = (await Proxy.next_proxy(self.config, self.url)).get("proxy")
                if not self.proxy:
                    print("Waiting for proxy")
                    await asyncio.sleep(5)

        if self.proxy and "http://" not in self.proxy:
            self.proxy = "http://" + self.proxy.replace("https://", "")

    def set_timestamp(self):
        self.added_at = time.time()