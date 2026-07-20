# Networking

## 2026-07-16 - Region selection

### Decision: Move everything to North Central US

**Context.** I needed a VM. Network was at Canada Central.

**Finding.** Canada Central was blocked by Azure's policy limiting me to five regions. Central US didn't have the size that i was looking for. East US 2 had quota limitations. North Central US was my only option. Portal region dropdown menu listed North Central US, then stopped listing it after a reload, with no change to the subscription. `az vm list-skus` was authoritative and did the job better than GUI.

**Decision.** Everything moved to North Central US. It was my third rebuild.

**Rationale.** North Central US was my only option because it's the only allowed region where B2ats_v2 has quota and no restrictions.

**Tradeoff.** Data sits in the US, not Canada. I had no choice since Microsoft only allowed me five regions that was either US or Mexico. Canada Central, Central US, and East US 2 resource groups are deleted. Bicep would have made this one variable instead of three rebuilds but i have no idea what bicep is at the moment since that's a task for the future.

**Next.** I am going to use the cloud shell as much as possible and run `az vm list-skus` before choosing a region. The most constrained resource picks the region, everything else follows.

## 2026-07-17 - Traffic controls

### Decision: Keep default-deny inbound, leave outbound open

**Context.** VM is in snet-private with no public IP. Both subnets have NSGs attached with only Azure's default rules.

**Finding.** Nothing needs inbound access. `run-command` covers administration, and `snet-public` is empty.

**Decision.** No inbound rules on either subnet. Outbound left unrestricted.

**Rationale.** A jump box is a small VM with a public IP whose only job is to give me entry to the main VM, but that another VM costs me another ~$7/month plus a public IP, so it would eat unnecessary credit for something `run-command` already does for free. The VM also needs to reach the internet outbound so that `apt update && apt upgrade` can reach Ubuntu's repos. Filtering egress would need Azure Firewall that is priced around $900/month, though this would help to allow the repos and deny the rest. I have accepted the risk of leaving outbound open. I considered using the built-in UFW, but it is host-based instead of being network-based, it will filter packets inside of the machine instead of it filtering before traffic reaches the machine. The UFW can be disabled, flushed, or rewritten by root. NSGs are enforced by Azure, outside the VM, so root on the machine doesn't reach them.

**Tradeoff.** Accepting an open egress from the VM increases the risk that, if the VM is compromised, malware could communicate with external infrastructure.

**Next.** This decision needs to be revisited when the lab holds real data. The storage account planned for the next session is the trigger.

## 2026-07-20 - Storage redundancy

### Decision: LRS chosen for redundancy matched to data value

**Context.** Storage account needs a redundancy tier which is either LRS (Locally Redundant Storage) or GRS (Geo-Redundant Storage).

**Decision.** LRS.

**Rationale.** Data is regenerable mock data. GRS costs more to survive a regional outage, which buys nothing for data that can be recreated with a script.

**Tradeoff.** No protection against a full region loss. Risk is accepted because the data is worthless if lost.

**Next.** Revisit if the account ever holds something not trivially regenerable.