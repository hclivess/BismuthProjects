import socks
from bisbasic.connections import send, receive
from bisbasic.essentials import format_raw_tx
from diff_simple import difficulty
import time

class Socket():
    def __init__(self):
        self.connect()

    def connect(self):
        self.s = socks.socksocket()
        self.s.connect(("127.0.0.1", 5658))

    def get_status(self):
        responded = False
        while not responded:
            try:
                send(self.s, "statusjson")
                reply = receive(self.s, timeout=1)
                responded = True
                return reply
            except Exception as e:
                print(f"Error: {e}")
                self.connect()

    def get_getblockrange(self, block, limit):
        responded = False
        while not responded:
            try:
                send(self.s, "api_getblockrange")
                send(self.s, block)
                send(self.s, limit)

                reply = receive(self.s, timeout=1)

                responded = True

                return reply
            except Exception as e:
                print(f"Error: {e}")
                self.connect()




class Status():
    def refresh(self, socket):

        self.status = socket.get_status()

        #non-chartable instants
        self.protocolversion = self.status['protocolversion']
        self.address = self.status['address']
        self.testnet = self.status['testnet']
        self.timeoffset = self.status['timeoffset']
        self.connections_list = self.status['connections_list']
        self.uptime = self.status['uptime']
        self.server_timestamp = self.status['server_timestamp']

        #chartable instants
        self.connections = self.status['connections']
        self.threads = self.status['threads']
        self.consensus = self.status['consensus']
        self.consensus_percent = self.status['consensus_percent']

        #non-instants
        self.difficulty = self.status['difficulty']
        self.blocks = self.status['blocks']

        #self.diffstatus = socket.get_diff()

        #instants from diffget
        #self.diff_dropped = self.diffstatus['diff_dropped']
        #self.time_to_generate = self.diffstatus['time_to_generate']
        #self.block_time = self.diffstatus['block_time']
        #self.diff_adjustment = self.diffstatus['diff_adjustment']
        #self.hashrate = self.diffstatus['hashrate']

        return self.status

class History():
    """saves status calls and the last block range call"""
    def __init__(self):
        self.blocks = []
        self.stata = []

    def truncate(self):
        self.stata = self.stata[:10]


class Updater():
    def __init__(self):
        self.status = Status()
        self.history = History()
        self.last_block = 0

    def update(self):
        self.socket = Socket()

        self.history.truncate()

        new_data = self.status.refresh(self.socket)

        if self.last_block < new_data["blocks"]: #if new block, status part can skip blocks when syncing
            self.history.stata.append([new_data])
            self.last_block = new_data["blocks"]

        self.history.blocks = self.socket.get_getblockrange(self.status.blocks -50, 50)
        print (self.history.blocks) #last block


        #difficulty()

        print(self.history.blocks)

if __name__ == "__main__":
    update = Updater()
