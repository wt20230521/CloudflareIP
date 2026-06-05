#!/usr/bin/env python3
"""
域名延迟测试工具 - 统一脚本
用法: python domain_tester.py <mode>
mode: domain, vless
"""

import asyncio
import time
import re
import sys
from typing import List, Optional, Tuple

RAW_ITEMS = [
    "jp.byun.eu.org", "un.goasa.top", "emby2.misakaf.org",
    "cfip.xxxxxxxx.tk", "bestcf.onecf.eu.org", "cf.zhetengsha.eu.org",
    "acjp2.cloudflarest.link", "achk.cloudflarest.link", "xn--b6gac.eu.org",
    "yx.887141.xyz", "8.889288.xyz", "cfip.1323123.xyz", "cf.515188.xyz",
    "cf-st.annoy.eu.org", "cf.0sm.com", "cf.877771.xyz", "cf.345673.xyz",
    "shopify.com", "time.is", "icook.hk", "icook.tw", "ip.sb",
    "japan.com", "malaysia.com", "russia.com", "singapore.com", "skk.moe",
    "www.visa.com", "www.visa.com.sg", "www.visa.com.hk", "www.visa.com.tw",
    "www.visa.co.jp", "www.visakorea.com", "www.gco.gov.qa", "www.gov.se",
    "www.gov.ua", "www.digitalocean.com", "www.csgo.com", "www.shopify.com",
    "www.whoer.net", "www.whatismyip.com", "www.ipget.net",
    "www.hugedomains.com", "www.udacity.com", "www.4chan.org",
    "www.okcupid.com", "www.glassdoor.com", "www.udemy.com",
    "www.baipiao.eu.org", "alejandracaiccedo.com", "log.bpminecraft.com",
    "www.boba88slot.com", "gur.gov.ua", "www.zsu.gov.ua", "www.iakeys.com",
    "edtunnel-dgp.pages.dev", "www.d-555.com", "fbi.gov", "www.sean-now.com",
    "download.yunzhongzhuan.com", "whatismyipaddress.com", "www.ipaddress.my",
    "www.pcmag.com", "www.ipchicken.com", "www.iplocation.net", "iplocation.io",
    "www.who.int", "www.wto.org", "www.visa.cn", "cf.877774.xyz", "palera.in",
    "ct.877774.xyz", "cmcc.877774.xyz", "cu.877774.xyz", "asia.877774.xyz",
    "eur.877774.xyz", "na.877774.xyz", "time.cloudflare.com", "bestcf.030101.xyz",
    "tw2s.youxuan.wiki", "youxuan.cf.090227.xyz", "cdns.doon.eu.org",
    "mfa.gov.ua", "store.ubi.com", "staticdelivery.nexusmods.com",
    "ktff.tencentapp.cn", "yd.iori3.pp.ua", "saas.sin.fan",
    "cloudflare-dl.byoip.top", "ProxyIP.Vultr.CMLiussss.net", "tbt1.593920.xyz",
    "优选.cf.090227.xyz", "123.cf.090227.xyz", "cf.tencentapp.cn",
    "cf.cloudflare.182682.xyz", "cdn.2020111.xyz", "cf.900501.xyz",
    "cfip.cfcdn.vip", "cloudflare.182682.xyz", "cloudflare-ip.mofashi.ltd",
    "fn.130519.xyz", "freeyx.cloudflare88.eu.org", "nrt.xxxxxxxx.nyc.mn",
    "nrtcfdns.zone.id", "tencentapp.cn", "777.ai7777777.xyz",
]

DOMAIN_REGEX = re.compile(r"^(?=.{1,253}$)(?!-)([A-Za-z0-9-]{1,63}\.)+[A-Za-z]{2,63}\.?$")

CONFIG = {
    "domain": {
        "output": "ip/Domain.txt",
        "format": lambda domain, status: f"{domain}#CF|优选域名|{status}",
        "top": 20,
    },
    "vless": {
        "output": "ip/Vless.txt",
        "format": lambda domain, status: f"vless://04c808e2-0b59-47b0-a54b-32fc7ef1c902@{domain}:443?encryption=none&security=tls&sni=misaka.cndyw.ggff.net&fp=random&type=ws&host=misaka.cndyw.ggff.net&path=%2F%3Fed%3D2560#优选|域名|{status}",
        "top": 20,
    },
}


def normalize_domains(items: List[str]) -> List[str]:
    seen = set()
    domains = []
    for raw in items:
        s = str(raw).strip().strip(",").strip("'" ").rstrip("',;:)")
        if not s or "://" in s:
            continue
        if DOMAIN_REGEX.match(s) is None:
            continue
        if s.endswith("."):
            s = s[:-1]
        if s.lower() in seen:
            continue
        seen.add(s.lower())
        domains.append(s)
    return domains


async def measure_latency(domain: str, port: int = 443, timeout: float = 1.0, attempts: int = 2) -> Optional[float]:
    best = None
    for _ in range(max(1, attempts)):
        start = time.perf_counter()
        try:
            _, writer = await asyncio.wait_for(
                asyncio.open_connection(domain, port, ssl=False), timeout=timeout
            )
            writer.close()
            try:
                await writer.wait_closed()
            except Exception:
                pass
            ms = (time.perf_counter() - start) * 1000.0
            best = ms if best is None else min(best, ms)
        except Exception:
            pass
    return best


async def gather(domains: List[str], concurrency: int = 200) -> List[Tuple[str, Optional[float]]]:
    sem = asyncio.Semaphore(concurrency)

    async def probe(d: str) -> Tuple[str, Optional[float]]:
        async with sem:
            return d, await measure_latency(d)

    tasks = [asyncio.create_task(probe(d)) for d in domains]
    return [await t for t in asyncio.as_completed(tasks)]


def run(mode: str):
    cfg = CONFIG[mode]
    domains = normalize_domains(RAW_ITEMS)
    results = asyncio.run(gather(domains))

    # Sort: success first by latency asc
    results.sort(key=lambda x: (1, float("inf")) if x[1] is None else (0, x[1]))
    top = results[: cfg["top"]]

    with open(cfg["output"], "w", encoding="utf-8") as f:
        for domain, ms in top:
            status = "timeout" if ms is None else f"{int(round(ms))}ms"
            line = cfg["format"](domain, status)
            f.write(line + "\n")
            print(line)

    print(f"Saved {len(top)} to {cfg['output']}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python domain_tester.py <mode>")
        print("Modes: domain, vless")
        sys.exit(1)
    run(sys.argv[1].lower())
