#!/usr/bin/env python3
"""
Cloudflare IP 测速工具 - 统一脚本
用法: python cf_tester.py <region>
region: jp, nl, sg, us, de, all
"""

import socket
import re
import time
import threading
import sys
from queue import Queue
from datetime import datetime

# ============ 配置 ============
CONFIG = {
    "jp": {
        "ip_ranges": ["108.162.198.0/22"],
        "top_nodes": 20,
        "output": "ip/JP.txt",
        "label": "jp 【日本】 JP",
    },
    "nl": {
        "ip_ranges": ["104.20.0.0/24", "188.114.96.0/24"],
        "top_nodes": 10,
        "output": "ip/NL.txt",
        "label": "nl 【荷兰】 NL",
    },
    "sg": {
        "ip_ranges": ["108.162.192.0/24", "162.159.0.0/24", "172.64.32.0/24"],
        "top_nodes": 10,
        "output": "ip/SG.txt",
        "label": "sg 【新加坡】 SG",
    },
    "us": {
        "ip_ranges": [
            "104.16.0.0/22", "104.18.0.0/22", "104.19.0.0/22",
            "104.17.0.0/22", "103.31.4.0/22", "103.21.244.0/22",
        ],
        "top_nodes": 10,
        "output": "ip/US.txt",
        "label": "us 【美国】 US",
    },
    "de": {
        "ip_ranges": [
            "104.21.0.0/24", "104.24.0.0/24", "104.25.0.0/24",
            "104.27.0.0/24", "104.26.0.0/24",
        ],
        "top_nodes": 10,
        "output": "ip/DE.txt",
        "label": "de 【德国】 DE",
    },
    "all": {
        "ip_ranges": [
            "172.64.229.0/24", "104.16.0.0/24", "104.17.0.0/24",
            "104.18.0.0/24", "104.19.0.0/24", "104.20.0.0/24",
            "104.21.0.0/24", "104.24.0.0/24", "104.25.0.0/24",
            "104.26.0.0/24", "104.27.0.0/24", "162.159.0.0/24",
            "188.114.96.0/24", "103.21.244.0/24", "108.162.192.0/24",
            "173.245.48.0/24", "103.22.200.0/24", "103.31.4.0/24",
            "141.101.64.0/24", "190.93.240.0/24", "197.234.240.0/24",
            "198.41.128.0/24", "162.158.0.0/24", "172.64.0.0/24",
            "172.64.128.0/24", "172.64.192.0/24", "172.64.224.0/24",
            "172.64.229.0/24", "172.64.230.0/24", "172.64.232.0/24",
            "172.64.240.0/24", "172.64.248.0/24", "172.65.0.0/24",
            "172.66.0.0/24", "172.67.0.0/24", "131.0.72.0/24",
        ],
        "top_nodes": 300,
        "output": "ip/IP.txt",
        "label": "CF 优选IP",
        "show_latency": True,
    },
}

TEST_TIMEOUT = 3
TEST_PORT = 443
MAX_THREADS = 30


class CloudflareTester:
    def __init__(self, config):
        self.config = config
        self.nodes = set()
        self.results = []
        self.lock = threading.Lock()

    def fetch_nodes(self):
        for ip_range in self.config["ip_ranges"]:
            base_ip, _ = ip_range.split("/")
            octets = base_ip.split(".")
            count = 20 if self.config.get("top_nodes", 20) >= 20 else 10
            for i in range(1, count):
                ip = f"{octets[0]}.{octets[1]}.{octets[2]}.{i + int(octets[3])}"
                self.nodes.add(ip)

    def test_node(self, ip):
        try:
            start = time.time()
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(TEST_TIMEOUT)
                if s.connect_ex((ip, TEST_PORT)) == 0:
                    return {
                        "ip": ip,
                        "reachable": True,
                        "latency_ms": int((time.time() - start) * 1000),
                    }
        except Exception:
            pass
        return {"ip": ip, "reachable": False, "latency_ms": None}

    def worker(self, queue):
        while not queue.empty():
            ip = queue.get()
            try:
                result = self.test_node(ip)
                with self.lock:
                    self.results.append(result)
            finally:
                queue.task_done()

    def run(self):
        self.fetch_nodes()
        q = Queue()
        for ip in self.nodes:
            q.put(ip)

        threads = []
        for _ in range(min(MAX_THREADS, len(self.nodes))):
            t = threading.Thread(target=self.worker, args=(q,))
            t.start()
            threads.append(t)
        for t in threads:
            t.join()

        reachable = [r for r in self.results if r["reachable"]]
        reachable.sort(key=lambda x: x["latency_ms"])

        top = reachable[: self.config["top_nodes"]]
        label = self.config["label"]
        show_latency = self.config.get("show_latency", False)

        with open(self.config["output"], "w", encoding="utf-8") as f:
            for node in top:
                if show_latency:
                    line = f"{node['ip']}#{label} {node['latency_ms']}ms\n"
                else:
                    line = f"{node['ip']}#{label}\n"
                f.write(line)
                print(line.strip())

        print(f"Saved {len(top)} nodes to {self.config['output']}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python cf_tester.py <region>")
        print("Regions: jp, nl, sg, us, de, all")
        sys.exit(1)

    region = sys.argv[1].lower()
    if region not in CONFIG:
        print(f"Unknown region: {region}")
        sys.exit(1)

    tester = CloudflareTester(CONFIG[region])
    tester.run()
