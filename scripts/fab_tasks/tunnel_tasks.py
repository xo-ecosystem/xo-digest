import os

from invoke import Collection, task


@task
def tunnel_deploy(c, service="agent0", port=8000, subdomain="agent0"):
    """
    🚀 Deploys a Cloudflare tunnel using .cloudflared config
    and writes .access.yaml to restrict access (IP or JWT-based)
    """
    print("🔧 Starting Cloudflare Tunnel...")
    c.run("cloudflared tunnel run xo-dev-tunnel &", pty=True)

    access_yaml = f"""
    ingress:
      - hostname: {subdomain}.21xo.com
        service: http://localhost:{port}
        originRequest:
          noTLSVerify: true
    """
    with open(".access.yaml", "w") as f:
        f.write(access_yaml.strip())
    print("✅ Tunnel started & access.yaml written")


@task
def tunnel_secure(c):
    """
    🔐 Placeholder for applying JWT/IP restriction logic
    """
    print("🔒 Securing tunnel with IP/JWT restrictions...")
    # TODO: Inject allowed JWTs or IPs into `.access.yaml`


@task
def tunnel_add_dns(c):
    """
    ☁️ Placeholder for Cloudflare DNS automation
    """
    print("🌐 Adding DNS entry via Cloudflare API...")
    # Requires CF_API_KEY + Zone ID etc.
    # You can use requests.post() to hit the Cloudflare DNS endpoint


ns = Collection("tunnel")
ns.add_task(tunnel_deploy, name="deploy")
ns.add_task(tunnel_secure, name="secure")
ns.add_task(tunnel_add_dns, name="add_dns")
