#!/usr/bin/env python3
"""
网页抓取解析工具 - 统一脚本
用法: python web_scraper.py <source>
source: me, cdtools, cfxyz
"""

import re
import sys
from typing import List, Tuple, Optional
import requests
from bs4 import BeautifulSoup
from html.parser import HTMLParser

# ============ 配置 ============
CONFIG = {
    "me": {
        "urls": ["https://api.uouin.com/cloudflare.html"],
        "output": "ip/Me.txt",
        "parser": "table",
        "format": lambda ip, line, speed: f"{ip}#【{line or '未知'} Nodes】{speed or ''}",
    },
    "cdtools": {
        "urls": [
            "https://cf-ip.cdtools.click/beijing",
            "https://cf-ip.cdtools.click/shanghai",
            "https://cf-ip.cdtools.click/shenzhen",
            "https://cf-ip.cdtools.click/chengdu",
        ],
        "output": "ip/Cdtools.txt",
        "parser": "cdtools",
        "format": lambda ip, line, speed: f"{ip}#【优选 Nodes】{speed or ''}",
    },
    "cfxyz": {
        "urls": ["https://ip.164746.xyz/"],
        "output": "ip/Cfxyz.txt",
        "parser": "cfxyz",
        "format": lambda ip, line, speed: f"{ip}#【测速 Nodes】{speed or ''}",
    },
}

IP_REGEX = re.compile(r"\b((?:\d{1,3}\.){3}\d{1,3})(?::\d+)?\b")
SPEED_REGEX = re.compile(
    r"\b\d+(?:\.\d+)?\s*(?:[KMG]?i?B/s|[KMG]B/s|B/s|[KMG]?bps|Gbps|Mbps|Kbps|bps)\b",
    re.IGNORECASE,
)


def fetch_html(url: str, timeout: int = 20) -> str:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 Chrome/128.0.0.0 Safari/537.36"
        )
    }
    session = requests.Session()
    session.trust_env = False
    resp = session.get(url, headers=headers, timeout=timeout, proxies={"http": None, "https": None})
    resp.raise_for_status()
    return resp.text


def parse_speed_to_bps(speed_text: str) -> float:
    if not speed_text:
        return -1.0
    m = re.match(r"^(\d+(?:\.\d+)?)\s*([A-Za-z/]+)$", speed_text.strip())
    if not m:
        return -1.0
    value, unit = float(m.group(1)), m.group(2).lower().replace(" ", "")
    factor = 1.0
    if unit.startswith("g"):
        factor = 1e9
    elif unit.startswith("m"):
        factor = 1e6
    elif unit.startswith("k"):
        factor = 1e3
    if "bps" in unit or (unit.endswith("b/s") and not unit.endswith("ib/s")):
        return value * factor
    return value * factor * 8.0


def parse_me(html: str) -> List[Tuple[str, str, str]]:
    soup = BeautifulSoup(html, "lxml")
    rows = []
    for table in soup.find_all("table"):
        for tr in table.find_all("tr")[1:]:
            tds = tr.find_all("td")
            if len(tds) < 3:
                continue
            ip_m = IP_REGEX.search(tds[0].get_text())
            if not ip_m:
                continue
            ip = ip_m.group(1)
            line = tds[1].get_text(strip=True) or "未知"
            speed = tds[2].get_text(strip=True) if len(tds) > 2 else ""
            rows.append((ip, line, speed))
    return rows


def parse_cdtools(html: str) -> List[Tuple[str, str, str]]:
    soup = BeautifulSoup(html, "lxml")
    results = []
    for table in soup.find_all("table"):
        headers = [h.get_text(strip=True).lower() for h in table.find_all("th")]
        ip_idx = next((i for i, h in enumerate(headers) if "ip" in h or "地址" in h), None)
        speed_idx = next((i for i, h in enumerate(headers) if "下载速度" in h or "speed" in h), None)
        if ip_idx is None or speed_idx is None:
            continue
        for tr in table.find_all("tr"):
            tds = tr.find_all("td")
            if len(tds) <= max(ip_idx, speed_idx):
                continue
            ip_m = IP_REGEX.search(tds[ip_idx].get_text())
            if not ip_m:
                continue
            speed_text = tds[speed_idx].get_text(strip=True)
            speed_m = SPEED_REGEX.search(speed_text)
            speed = speed_m.group(0) if speed_m else ""
            results.append((ip_m.group(1), "优选", speed))
    return results


class CfxyzParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self._in_table = False
        self._in_row = False
        self._in_cell = False
        self._cell_parts = []
        self._row = []
        self.rows = []

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag == "table":
            self._in_table = True
        if not self._in_table:
            return
        if tag == "tr":
            self._in_row = True
            self._row = []
        elif tag in {"td", "th"} and self._in_row:
            self._in_cell = True
            self._cell_parts = []

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag == "table":
            self._in_table = False
        if not self._in_table:
            return
        if tag in {"td", "th"} and self._in_row:
            self._row.append("".join(self._cell_parts).strip())
            self._in_cell = False
        elif tag == "tr" and self._in_row:
            if self._row:
                self.rows.append(self._row)
            self._in_row = False

    def handle_data(self, data):
        if self._in_table and self._in_row and self._in_cell:
            self._cell_parts.append(data)


def parse_cfxyz(html: str) -> List[Tuple[str, str, str]]:
    parser = CfxyzParser()
    parser.feed(html)
    results = []
    seen = set()
    for row in parser.rows:
        row_text = " ".join(row)
        ips = IP_REGEX.findall(row_text)
        speed_m = SPEED_REGEX.search(row_text)
        speed = speed_m.group(0) if speed_m else ""
        for ip in ips:
            if ip not in seen:
                seen.add(ip)
                results.append((ip, "测速", speed))
    return results


def run(source: str):
    cfg = CONFIG[source]
    all_results = []

    for url in cfg["urls"]:
        try:
            html = fetch_html(url)
            if cfg["parser"] == "table":
                rows = parse_me(html)
            elif cfg["parser"] == "cdtools":
                rows = parse_cdtools(html)
            elif cfg["parser"] == "cfxyz":
                rows = parse_cfxyz(html)
            else:
                rows = []
            all_results.extend(rows)
            print(f"Fetched {len(rows)} from {url}")
        except Exception as e:
            print(f"Failed {url}: {e}", file=sys.stderr)

    if not all_results:
        print("No data fetched", file=sys.stderr)
        return

    # Deduplicate by IP, keep fastest
    best = {}
    for ip, line, speed in all_results:
        bps = parse_speed_to_bps(speed)
        if ip not in best or bps > best[ip][2]:
            best[ip] = (line, speed, bps)

    # Sort by speed desc
    sorted_ips = sorted(best.items(), key=lambda x: x[1][2], reverse=True)

    with open(cfg["output"], "w", encoding="utf-8") as f:
        for ip, (line, speed, _) in sorted_ips:
            line_text = cfg["format"](ip, line, speed)
            f.write(line_text + "\n")
            print(line_text)

    print(f"Saved {len(sorted_ips)} to {cfg['output']}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python web_scraper.py <source>")
        print("Sources: me, cdtools, cfxyz")
        sys.exit(1)
    run(sys.argv[1].lower())
