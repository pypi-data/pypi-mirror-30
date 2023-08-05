import nsq
import json
import requests


class BaseQueue:
    def __init__(self, project_name, config, loop, name, postfix):
        self.name = name
        self.loop = loop
        self.status = False
        self.addresses = []
        self.config = config
        self.config_queue = self.config.queues[self.name]
        self.project_name = project_name
        self.channel = self.config_queue["channel"]
        self.topic = "fetcher_{}_{}".format(self.project_name, self.config_queue["topic"] + postfix)
        self.init()

    def init(self):
        if self.config.debug:
            self.nsqlookupd_ip = "localhost:4161"
        else:
            self.nsqlookupd_ip = "nsqlookupd:4161"

    def init_writer(self):
        if self.config.debug:
            self.writer = nsq.Writer(['localhost:4150'])
        else:
            self.writer = nsq.Writer(self.get_nsqd_ips())

    def init_reader(self):
        if self.config.debug:
            self.reader = nsq.Reader(
                topic=self.topic, channel=self.channel, message_handler=self.message_handler, max_in_flight=self.concurrent,
                lookupd_connect_timeout=10, requeue_delay=10, msg_timeout=self.msg_timeout,
                nsqd_tcp_addresses="localhost:4150", max_backoff_duration=256
            )

            if not self.status:
                self.reader.set_max_in_flight(0)

                self.get_nsqd_ips()

        else:
            self.reader = nsq.Reader(
                topic=self.topic, channel=self.channel, message_handler=self.message_handler,
                lookupd_connect_timeout=10, requeue_delay=10, msg_timeout=self.msg_timeout,
                lookupd_http_addresses=[self.nsqlookupd_ip], max_in_flight=self.concurrent, max_backoff_duration=256
            )

            if not self.status:
                self.reader.set_max_in_flight(0)

    @property
    def msg_timeout(self):
        return self.config_queue["msg_timeout"]

    @msg_timeout.setter
    def msg_timeout(self, value):
        self.config_queue["msg_timeout"] = value
        self.init_reader()

    def is_busy(self):
        return self.reader.is_starved()

    def pause(self):
        self.status = False
        self.reader.set_max_in_flight(0)

    def set_callback(self, callback):
        self.callback = callback

    @property
    def concurrent(self):
        return self.config_queue["concurrent"]

    @concurrent.setter
    def concurrent(self, value):
        self.config_queue["concurrent"] = value
        if self.status:
            print("change concurrent on " + self.topic, self.concurrent)
            self.reader.set_max_in_flight(0)
            self.init_reader()
            self.reader.set_max_in_flight(self.concurrent)

    def start(self):
        print("CALL start from q: ", self.status, self.topic, self.concurrent, self.is_busy())
        if not self.status:
            self.status = True
            print("Start Queue", self.topic, self.concurrent)

            self.reader.set_max_in_flight(self.concurrent)

    def get_nsqd_ips(self):
        data = requests.get("http://{}/nodes".format(self.nsqlookupd_ip)).content
        nodes = json.loads(data.decode())
        address = []
        for producer in nodes.get("producers"):
            ip = producer["remote_address"].split(':')[0]
            self.addresses.append(ip)
            address.append("{}:{}".format(ip, 4150))

        return address

    def delay_push(self, message, delay):

        self.writer.dpub(self.topic, delay*1000, message.encode())

    def push(self, message):
        self.writer.pub(self.topic, message.encode())

    def get_stats(self):
        stats = []
        for ip in self.addresses:
            data = json.loads(requests.get('http://{}:4151/stats?format=json&topic={}'.format(ip,self.topic)).content.decode())
            for topic in data["topics"]:
                if topic["topic_name"] != self.topic:
                    continue

                for channel in topic["channels"]:
                    if channel["channel_name"] != self.channel:
                        continue
                    stats.append(channel)
        return stats

    async def queue_checker(self, message):
        raise NotImplementedError

    def message_handler(self, message):
        raise NotImplementedError
