# Identity

## 2026-07-14 - Tenant ownership

### Create a separate Entra tenant for the lab

**Context.** Azure for Students placed my subscription in Red River College's
tenant (rrcca.onmicrosoft.com), where my @rrc.ca account is homed.

**Finding.** Two authorization systems, and I had opposite positions in each:
- Entra roles (identity plane): none in RRC's tenant. Cannot create users,
  groups, or policies.
- Azure RBAC (resource plane): Owner on my subscription. Full control of
  resources and spend.

The lab requires creating identities, so the identity plane was blocking.

**Decision.** Created a workforce tenant (rrcazlab2026.onmicrosoft.com,
region Canada) where I hold Global Administrator.

**Rationale.** Tenant creators are automatically assigned Global Administrator, so this required no approval from RRC. Region and initial domain are permanent; chose Canada for data residency and a domain with no PII, since screenshots of it go in a public repo.

**Tradeoff.** Two tenants to manage instead of one. Accepted: identity control is a prerequisite for the rest of the lab.

**Follow-on risk found.** The new tenant's only admin was my #EXT# account -
an object in my tenant whose authentication home is RRC's directory. RRC
controls its lifecycle, so my lab's sole GA was revocable by my college.
Mitigated by creating labadmin@rrcazlab2026.onmicrosoft.com, cloud-only,
with its own password and MFA, verified by signing in before relying on it.

### Failed subscription transfer

**Context.** My Azure for Students subscription is associated with RRC's tenant (rrcca.onmicrosoft.com), because my @rrc.ca identity is homed there. I attempted to change its directory association to my own tenant (rrcazlab2026.onmicrosoft.com) so that identities I control could hold RBAC on it.

**Finding.** The portal returned: `Your current settings do not allow you to transfer this subscription. Contact your Global Administrator for access`. I initially read this as a control RRC had deliberately configured. It isn't: as of May 1, 2026, Microsoft changed the platform default so subscriptions cannot move in or out of a directory unless a Global Administrator explicitly permits it. RRC almost certainly never touched this setting. Only a Global Admin with elevated access can change the policy or add an exemption, so I have no path to it.

**Decision.** The subscription stays in RRC's tenant while my lab runs split across two directories

**Rationale.** I am keeping `rrcazlab2026.onmicrosoft.com` so i can have a directory that i can work on: user, groups, security defaults, MFA. RRC directory is for RBAC, it doesn't let me have entra roles unlike `rrcazlab`.

**Tradeoff.** Users and groups created in `rrcazlab2026.onmicrosoft.com` can never hold RBAC on the subscription, because it trusts `rrcca.onmicrosoft.com` and guest invitation from my domain is blocked. Least-privilege assignments in `rbac-review.md` are therefore limited to managed identities and custom role definitions - I cannot demonstrate group-based RBAC against real resources.