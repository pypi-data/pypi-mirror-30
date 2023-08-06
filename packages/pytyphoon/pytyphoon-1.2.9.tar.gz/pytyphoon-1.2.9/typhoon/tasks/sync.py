from .base import BaseTask


class SyncTask(BaseTask):
    def __init__(self, config, task):
        super().__init__(config, task)

    async def init(self):
        await self.set_proxy()