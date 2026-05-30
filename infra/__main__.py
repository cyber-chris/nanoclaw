import pulumi
import pulumi_hcloud as hcloud

# Fetch stack configuration
config = pulumi.Config()
ssh_pub_key = config.require("sshPublicKey")

# TODO
