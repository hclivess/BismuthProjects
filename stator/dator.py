import socks
from bisbasic.connections import send, receive
import time

class Socket():
    def __init__(self):
        self.s = socks.socksocket()
        self.s.connect(("127.0.0.1", 5658))

    def get_status(self):
        send(self.s, "statusjson")
        reply = receive(self.s)
        return reply

    def get_blocksafter(self, block):
        send(self.s, "api_getblocksince")
        send(self.s, block)
        reply = receive(self.s)
        return reply

    def get_diffsafter(self, block):
        send(self.s, "api_getdiffsafter")
        send(self.s, block)
        reply = receive(self.s)
        return reply

class Status():
    def refresh(self, socket):

        self.status = socket.get_status()

        self.protocolversion = self.status['protocolversion']
        self.address = self.status['address']
        self.testnet = self.status['testnet']
        self.timeoffset = self.status['timeoffset']
        self.connections = self.status['connections']
        self.connections_list = self.status['connections_list']
        self.difficulty = self.status['difficulty']
        self.blocks = self.status['blocks']
        self.threads = self.status['threads']
        self.uptime = self.status['uptime']
        self.consensus = self.status['consensus']
        self.consensus_percent = self.status['consensus_percent']
        self.server_timestamp = self.status['server_timestamp']

        return self.status

class History():
    def __init__(self):
        self.blocks = []
        self.diffs = []
        self.stata = []

    def truncate(self):
        self.stata = self.stata[:10]


class Updater():
    def __init__(self):
        self.status = Status()
        self.history = History()
        self.last_block = None

    def update(self):
        self.socket = Socket()

        self.history.truncate()

        new_data = self.status.refresh(self.socket)

        if self.last_block != new_data["blocks"]: #if new block, can skip blocks when syncing, better do it through plugins
            self.history.stata.append(new_data)
            self.last_block = new_data["blocks"]

        del self.history.blocks[:]
        self.history.blocks.append(self.socket.get_blocksafter(self.status.blocks - 30))
        self.history.blocks.append(self.socket.get_blocksafter(self.status.blocks - 20))
        self.history.blocks.append(self.socket.get_blocksafter(self.status.blocks - 10))

        del self.history.diffs[:]
        self.history.diffs.append(self.socket.get_diffsafter(self.status.blocks - 30))
        self.history.diffs.append(self.socket.get_diffsafter(self.status.blocks - 20))
        self.history.diffs.append(self.socket.get_diffsafter(self.status.blocks - 10))

        print(self.history.diffs)

        #print(self.history.stata)
        #print(self.history.diffs)
        #print(self.history.blocks)
if __name__ == "__main__":
    update = Updater()
