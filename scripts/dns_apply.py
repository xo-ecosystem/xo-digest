#!/usr/bin/env python3
import os, sys, json, time
import requests, yaml

CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")
CLOUDFLARE_API_KEY   = os.getenv("CLOUDFLARE_API_KEY")
CLOUDFLARE_API_EMAIL = os.getenv("CLOUDFLARE_API_EMAIL")
NC_API_URL = os.getenv("NAMECHEAP_API_URL", "https://api.namecheap.com/xml.response")
NC_API_USER = os.getenv("NAMECHEAP_API_USER")
NC_USERNAME = os.getenv("NAMECHEAP_USERNAME")
NC_API_KEY = os.getenv("NAMECHEAP_API_KEY")
NC_CLIENT_IP = os.getenv("NAMECHEAP_CLIENT_IP")


def cf(url, method="GET", **kwargs):
    if not CF_TOKEN:
        sys.exit("Missing CLOUDFLARE_API_TOKEN")
    headers = kwargs.pop("headers", {})
    headers["Authorization"] = f"Bearer {CF_TOKEN}"
    headers["Content-Type"] = "application/json"
    r = requests.request(method, url, headers=headers, **kwargs)
    r.raise_for_status()
    return r.json()


def cf_zone_id(domain):
    data = cf(f"https://api.cloudflare.com/client/v4/zones?name={domain}&status=active")
    return (data.get("result") or [{}])[0].get("id", "")


def cf_ns(zone_id):
    data = cf(f"https://api.cloudflare.com/client/v4/zones/{zone_id}")
    return data["result"].get("name_servers", [])


def cf_upsert(zone_id, name, typ, content, proxied=False):
    q = cf(
        f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records?type={typ}&name={name}"
    )
    rid = (q.get("result") or [{}])[0].get("id")
    body = {"type": typ, "name": name, "content": content, "proxied": bool(proxied)}
    if rid:
        res = cf(
            f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{rid}",
            "PUT",
            json=body,
        )
        action = "updated"
    else:
        res = cf(
            f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records",
            "POST",
            json=body,
        )
        action = "created"
    ok = res.get("success", False)
    print(
        json.dumps(
            {"zone": zone_id, "name": name, "type": typ, "proxied": proxied, action: ok}
        )
    )
    return ok


def nc_set_ns(domain, ns1, ns2):
    if not (NC_API_USER and NC_USERNAME and NC_API_KEY and NC_CLIENT_IP):
        print("⚠️  Skipping Namecheap NS update (missing env vars).", file=sys.stderr)
        return
    sld, tld = domain.split(".", 1)
    params = {
        "ApiUser": NC_API_USER,
        "ApiKey": NC_API_KEY,
        "UserName": NC_USERNAME,
        "ClientIp": NC_CLIENT_IP,
        "Command": "namecheap.domains.dns.setCustom",
        "SLD": sld,
        "TLD": tld,
        "Nameservers": f"{ns1},{ns2}",
    }
    r = requests.get(NC_API_URL, params=params, timeout=30)
    r.raise_for_status()
    print(f"Namecheap NS set for {domain}: {ns1}, {ns2}")


def render(val, meta):
    # simple templating: "{{ pages_host }}"
    if isinstance(val, str) and "{{" in val:
        out = val
        for k, v in (meta or {}).items():
            out = out.replace(f"{{{{ {k} }}}}", str(v))
        return out
    return val


def main():
    cfg_path = None
    # prefer ~/.xo-config/dns_config.yml, fallback to scripts/dns_config.yml
    home_cfg = os.path.expanduser("~/.xo-config/dns_config.yml")
    repo_cfg = os.path.join(os.path.dirname(__file__), "dns_config.yml")
    if len(sys.argv) > 2 and sys.argv[1] == "--config":
        cfg_path = sys.argv[2]
    elif os.path.exists(home_cfg):
        cfg_path = home_cfg
    elif os.path.exists(repo_cfg):
        cfg_path = repo_cfg
    else:
        sys.exit(
            "No dns_config.yml found. Use --config PATH or create ~/.xo-config/dns_config.yml"
        )

    with open(cfg_path, "r") as f:
        cfg = yaml.safe_load(f)

    meta = cfg.get("meta", {})
    domains = cfg.get("domains", cfg)  # support old flat format

    for d in domains:
        domain = d["name"]
        print(f"\n=== {domain} ===")
        zid = cf_zone_id(domain)
        if not zid:
            sys.exit(
                f"❌ Cloudflare zone not found for {domain}. Create/activate in CF first."
            )
        print(f"CF Zone: {zid}")

        if d.get("nameservers", {}).get("auto_cf"):
            ns = cf_ns(zid)
            if len(ns) >= 2:
                print(f"CF NS: {ns}")
                try:
                    nc_set_ns(domain, ns[0], ns[1])
                except Exception as e:
                    print(f"⚠️  Namecheap NS update failed: {e}", file=sys.stderr)

        for rec in d.get("records", []):
            typ = rec["type"]
            name = rec["name"]
            content = render(rec["content"], meta)
            proxied = bool(rec.get("proxied", False))
            cf_upsert(
                zid,
                f"{name}.{domain}" if name not in ("@",) else domain,
                typ,
                content,
                proxied,
            )

    print("\n✅ DNS apply complete.")


if __name__ == "__main__":
    main()
