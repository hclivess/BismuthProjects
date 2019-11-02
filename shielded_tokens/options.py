import os.path as path
from sys import exit
import json

class Get:
    # "param_name":["type"] or "param_name"=["type","property_name"]
    vars={
        "port":["str"],
        "verify":["bool","verify"],
        "testnet":["bool"],
        "regnet":["bool"],
        "version":["str","version"],
        "version_allow":["list"],
        "thread_limit":["int","thread_limit"],
        "rebuild_db":["bool","rebuild_db"],
        "debug":["bool","debug"],
        "purge":["bool","purge"],
        "pause":["int","pause"],
        "ledger_path":["str","ledger_path"],
        "hyper_path":["str","hyper_path"],
        "hyper_recompress":["bool","hyper_recompress"],
        "full_ledger":["bool","full_ledger"],
        "ban_threshold":["int"],
        "tor":["bool","tor"],
        "debug_level":["str","debug_level"],
        "allowed":["str","allowed"],
        "ram":["bool","ram"],
        "node_ip":["str","node_ip"],
        "light_ip":["dict"],
        "reveal_address":["bool"],
        "accept_peers":["bool"],
        "banlist":["list"],
        "whitelist":["list"],
        "nodes_ban_reset":["int"],
        "mempool_allowed": ["list"],
        "terminal_output": ["bool"],
        "gui_scaling": ["str"],
        "mempool_ram": ["bool"],
        "egress": ["bool"],
        "trace_db_calls": ["bool"],
        "heavy3_path": ["str"],
        "mempool_path": ["str"],
    }

    # Optional default values so we don't bug if they are not in the config.
    # For compatibility
    defaults = {
        "testnet": False,
        "regnet": False,
        "trace_db_calls": False,
        "mempool_ram": True,
        "heavy3_path": "./heavy3a.bin",
        "mempool_path": "./mempool.db",
    }

    def load_file(self, filename):
        #print("Loading",filename)
        with open(filename) as fp:
            for line in fp:
                if '=' in line:
                    left,right = map(str.strip,line.rstrip("\n").split("="))
                    if "mempool_ram_conf" == left:
                        print("Inconsistent config, param is now mempool_ram in config.txt")
                        exit()
                    if not left in self.vars:
                        # Warn for unknown param?
                        continue
                    params = self.vars[left]
                    if params[0] == "int":
                        right = int(right)
                    elif params[0] == "dict":
                        try:
                            right = json.loads(right)
                        except: #compatibility
                            right = [item.strip() for item in right.split(",")]
                    elif params[0] == "list":
                        right = [item.strip() for item in right.split(",")]
                    elif params[0] == "bool":
                        if right.lower() in ["false", "0", "", "no"]:
                            right = False
                        else:
                            right = True

                    else:
                        # treat as "str"
                        pass
                    if len(params) > 1:
                        # deal with properties that do not match the config name.
                        left = params[1]
                    setattr(self, left, right)
        # Default genesis to keep compatibility
        self.genesis = "4edadac9093d9326ee4b17f869b14f1a2534f96f9c5d7b48dc9acaed"
        for key, default in self.defaults.items():
            if key not in self.__dict__:
                setattr(self, key, default)

        #print(self.__dict__)

    def read(self):
        # first of all, load from default config so we have all needed params
        self.load_file("config.txt")
        # then override with optional custom config
        if path.exists("config_custom.txt"):
            self.load_file("config_custom.txt")
        """
        if "regnet" in self.version:
            print("Regnet, forcing ram = False")
            self.ram = False
        """
