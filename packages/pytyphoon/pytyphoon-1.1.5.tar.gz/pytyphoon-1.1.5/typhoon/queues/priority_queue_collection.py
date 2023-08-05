from .priority import PriorityQueue
import asyncio

class PriorityQueueCollection:
    def __init__(self, project_name, config, loop):
        self.loop = loop
        self.status = False
        self.config = config
        self.config_queue = self.config.queues["priority"]
        self.project_name = project_name
        self.queue_args = (self.project_name, self.config, self.loop, "priority")
        self.priorities = {
            1: PriorityQueue(*self.queue_args, postfix="1"),
            2: PriorityQueue(*self.queue_args, postfix="2"),
            3: PriorityQueue(*self.queue_args, postfix="3")
        }
        self.current_queue = None
        self.depth_checker_flag = False
        self.init()

    def set_callback(self, callback):
        self.callback = callback

    @property
    def concurrent(self):
        return self.config_queue["concurrent"]

    @concurrent.setter
    def concurrent(self, value):
        self.config_queue["concurrent"] = value
        for p in self.priorities:
            q = self.priorities[p]
            setattr(q, 'concurrent', value)

    @property
    def msg_timeout(self):
        return self.config_queue["msg_timeout"]

    @msg_timeout.setter
    def msg_timeout(self, value):
        self.config_queue["msg_timeout"] = value
        for p in self.priorities:
            q = self.priorities[p]
            q.msg_timeout = value

    def pause(self):
        for p in self.priorities:
            q = self.priorities[p]
            q.pause()
        self.status = False

    def start(self):
        self.status = True
        for p in self.priorities:
            q = self.priorities[p]
            q.init_reader()
        self.choose_active_queue()
        if not self.depth_checker_flag:
            self.loop.create_task(self.depth_checker())

    def is_busy(self):
        return any([self.priorities[it].is_busy() for it in self.priorities])

    def is_depth(self, stats):
        status = False

        for stat in stats:
            if stat["depth"] > 0:
                status = True
                break

        return status

    async def run_pause_time(self):
        self.pause()
        print("--------------PAUSING---------------")
        await asyncio.sleep(self.config["pause_time"])
        print("--------------UNPAUSING---------------")
        self.choose_active_queue()

    def pause_waterflow(self, under):
        for priority in range(int(under) + 1, len(self.priorities)+1):
            self.priorities[priority].pause()

    def choose_active_queue(self):
        print("CHOOSING QUEUE")
        for priority in self.priorities:
            queue = self.priorities[priority]
            stats = self.priorities[priority].get_stats()

            if self.is_depth(stats):
                self.current_queue = priority
                self.status = True
                queue.start()
                self.pause_waterflow(priority)
                break
            else:
                queue.pause()
        else:
            self.current_queue = None

    def init(self):
        for p in self.priorities:
            queue = self.priorities[p]
            queue.set_callback(self.output)
            queue.init_writer()
            queue.msg_timeout = self.msg_timeout

    async def depth_checker(self):
        self.depth_checker_flag = True
        while True:
            # print("DEPTH CHECKER", self.status, self.current_queue)
            if not self.current_queue:
                print("ALL QUEUES ARE EMPTY")
                self.choose_active_queue()
                # await asyncio.sleep(self.config["priority_depth_check_delay"])
            elif self.status and not self.is_depth(self.priorities[self.current_queue].get_stats()):
                print("<<<<<<<<<'IF' WORKS>>>>>>>>>>>")
                self.pause()
                self.choose_active_queue()
            print("<<<<<<<<<<DEPTH CHECKER WORKS>>>>>>>>")
            await asyncio.sleep(self.config["priority_depth_check_delay"])

    def output(self, message):
        self.callback(message)
        if self.is_busy() and self.config["pause_time"]:
            self.loop.create_task(self.run_pause_time())
