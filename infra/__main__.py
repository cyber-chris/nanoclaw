import os

import pulumi
import pulumi_hcloud as hcloud

# Fetch stack configuration
config = pulumi.Config()
ssh_pub_key = config.require("sshPublicKey")

server_type = config.get("serverType") or "cpx22"
location = config.get("location") or "nbg1"
image = config.get("image") or "ubuntu-24.04"
repo_url = config.get("repoUrl") or "https://github.com/cyber-chris/nanoclaw.git"
NAME = "nanoclaw"

ssh_key = hcloud.get_ssh_key(
    # This is ct@Chriss-MacBook-Air.local
    fingerprint="9b:45:39:36:38:95:17:5b:62:df:20:97:23:26:14:f8"
)

firewall = hcloud.Firewall(
    "firewall",
    name=f"{NAME}-firewall",
    rules=[
        hcloud.FirewallRuleArgs(
            description="Allow SSH",
            direction="in",
            protocol="tcp",
            port="22",
            source_ips=["0.0.0.0/0", "::/0"],
        ),
        hcloud.FirewallRuleArgs(
            description="Allow ICMP (ping)",
            direction="in",
            protocol="icmp",
            source_ips=["0.0.0.0/0", "::/0"],
        ),
    ],
)

template_path = os.path.join(os.path.dirname(__file__), "cloud-init.yaml")
with open(template_path, "r", encoding="utf-8") as f:
    cloud_init = (
        f.read().replace("__SSH_PUB_KEY__", ssh_pub_key).replace("__REPO_URL", repo_url)
    )

if ssh_key.id is None:
    raise RuntimeError("ssh-key has no ID")
server = hcloud.Server(
    "server",
    name=NAME,
    server_type=server_type,
    image=image,
    location=location,
    ssh_keys=[str(ssh_key.id)],
    firewall_ids=[firewall.id.apply(lambda fid: int(fid))],
    user_data=cloud_init,
    labels={"app": "nanoclaw"},
)

pulumi.export("server_id", server.id)
pulumi.export("server_status", server.status)
pulumi.export("ipv4", server.ipv4_address)
pulumi.export("ipv6", server.ipv6_address)
pulumi.export("ssh", server.ipv4_address.apply(lambda ip: f"ssh {NAME}@{ip}"))
pulumi.export(
    "next_steps",
    server.ipv4_address.apply(
        lambda ip: (
            f"ssh {NAME}@{ip}  # then: cd nanoclaw && bash nanoclaw.sh "
            "(cloud-init may take ~2-3 min on first boot)"
        )
    ),
)
