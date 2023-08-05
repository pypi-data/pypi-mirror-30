import aioredis


class CacheStorage:

    def __init__(self, config, loop):
        self.config = config["redis"]["debug"] if config["debug"] else config["redis"]["production"]
        loop.create_task(self.init_connection())

    async def init_connection(self):
        self.host = self.config["host"]
        self.port = self.config["port"]
        self.password = self.config["password"]
        self.redis_con = await aioredis.create_redis(address=(self.host, self.port), password=self.password)

    async def set(self, key, value):
        await self.redis_con.set(key, value)

    async def set_ex(self, key, value, time_in_sec):
        await self.redis_con.setex(key, time_in_sec, value)

    async def get(self, key):
        return await self.redis_con.get(key)

    async def increment(self, key, amount=1):
        await self.redis_con.incrby(key, amount)


# IT'S ONLY FOR METHODS TESTING
if __name__ == "__main__":
    import asyncio
    config = {
        "redis_host": "localhost",
        "redis_port": 6379,
        "redis_password": None
    }
    loop = asyncio.get_event_loop()

    async def main():
        r = CacheStorage(config, loop)
        print(r.redis_con)
        await r.set("sec", "11101234123")
        print(r.get("sec"))

    loop.run_until_complete(main())
