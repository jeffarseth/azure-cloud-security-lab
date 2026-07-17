# Security review

## 2026-07-17 - Management plane access to VMs

### Finding: RBAC grants root on a VM with no network path

**Observed.** Ran this against a VM with no public IP, in a private subnet, with default-deny inbound NSGs:

```
az vm run-command invoke \
  --resource-group rg-azseclab-ncus \
  --name vm-azseclab-ncus \
  --command-id RunShellScript \
  --scripts "hostname && whoami && ip a"
```

Output:

```
vm-azseclab-ncus
root
```

**Mechanism.** I have Owner on the subscription. Owner includes `runCommand`. The VM runs a guest agent that polls Azure's control plane and executes whatever it's told, as root.

**Who can do this.** Me, then anyone with Contributor or above, then RRC's GAs after elevating.

**Implication.** The NSGs that I have created do not protect a VM from someone with RBAC. Two separate planes, and hardening one does nothing for the other.