# Networking

## 2026-07-16 - Region selection

### Move everything to North Central US

**Context.** I needed a VM. Network was at Canada Central.

**Finding.** Canada Central was blocked by Azure's policy limiting me to five regions. Central US didn't have the size that i was looking for. East US 2 had quota limitations. North Central US was my only option. Portal region dropdown menu listed North Central US, then stopped listing it after a reload, with no change to the subscription. `az vm list-skus` was authoritative and did the job better than GUI.

**Decision.** Everything moved to North Central US. It was my third rebuild.

**Rationale.** North Central US was my only option because it's the only allowed region where B2ats_v2 has quota and no restrictions.

**Tradeoff.** Data sits in the US, not Canada. I had no choice since Microsoft only allowed me five regions that was either US or Mexico. Canada Central, Central US, and East US 2 resource groups are deleted. Bicep would have made this one variable instead of three rebuilds but i have no idea what bicep is at the moment since that's a task for the future.

**Next.** I am going to use the cloud shell as much as possible and run `az vm list-skus` before choosing a region. The most constrained resource picks the region, everything else follows.