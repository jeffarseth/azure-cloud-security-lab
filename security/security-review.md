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

## 2026-07-21 - Management plane vs data plane

### Finding: Owner role cannot read or write blob data

**Observed.** I have Owner. I tried to run `az storage blob upload --auth-mode login`, but got "You do not have the required permissions."

**Mechanism.** Azure splits access into two planes. The management plane covers operations on the account itself: create, configure, delete, rotate keys. The data plane covers the bytes inside: read, write, list blobs. Owner grants the management plane only. Reading or writing blob data requires a separate Storage Blob Data role. I assigned myself as Storage Blob Data Contributor in order to have the ability to upload files to blobs.

**Implication.** Azure separated the management plane and the data plane in order to apply least-privilege for who can control accounts and who can control data.

### Finding: Logging is itself an attack surface (log flooding)

**Context.** Setup blob diagnostics such as read, write, delete to log analytics.

**Concern.** Logs are an attack surface to which an attacker can flood.

**Mechanism.** I am on pay-as-you-go past 5 GB/month. An attacker can generate millions of operations that can either cost me more money or a daily cap set to control cost becomes a blind spot, since collection stops once it's hit. An attacker can also bury the real event by these millions of junk reads.

**Mitigations.** Rate-based alerting can detect abnormal threshold, alert when the cap is hit. Make the log storage immutable for a set retention period so that forensics can still be achievable, only slower. Separate the logging plane from the workload plane via Log Analytics so that access control becomes tighter; tampering with logs requires a separate compromise of the workspace, with its own RBAC.