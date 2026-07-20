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

## 2026-07-20 - Storage account security

### Finding: Shared key access bypasses RBAC scoping and attribution

**Observed.** Enabled shared access key, which means the account access keys grant full data access without Entra authentication.

**Mechanism.** Using the shared key instead of RBAC has a different authentication system. Key grants the entire account, can't be limited to one container or to read-only. Logs can't say who used the key. There isn't a "lesser version" of a key.

**Implication.** Any user who obtains either account key has full, non-attributable access to all data, and revoking it means rotating the key, which breaks everything using it.

**Intent.** Enabled deliberately so `storage-audit.py` has something to detect in Week 4.

### Finding: Versioning on for ransomware/overwrite recovery

**Observed.** Blob versioning is enabled on the account.

**Mechanism.** Each overwrite or delete keeps prior version rather than destroying it.

**Mitigates.** Accidental deletion, and ransomware that encrypts blobs in place (can roll back to a clean version).