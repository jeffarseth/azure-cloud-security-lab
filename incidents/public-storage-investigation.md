# Public Storage Investigation

## 2026-07-23 - Staged public blob exposure

### Simulation: Anonymous read of a misconfigured container

**Summary.** I staged an exposure with mock_pii.csv, fabricated data, in the lab-data container in the stazseclab2 storage account. It could be read using anonymous HTTP requests without credentials, and storage-audit.py successfully caught it.

**Reproduction.**

1. Expose:

```
PS > az storage account update --name stazseclab2 --resource-group rg-azseclab-ncus --allow-blob-public-access true
```

```
PS > az storage container set-permission --name lab-data --account-name stazseclab2 --public-access blob --auth-mode key
```

2. Detection:

```
PS > python .\scripts\storage-audit.py    # [EXPOSED] fired and wrote the JSON finding
```

3. Re-lock:

```
PS > az storage container set-permission --name lab-data --account-name stazseclab2 --public-access off --auth-mode key
```

```
PS > az storage account update --name stazseclab2 --resource-group rg-azseclab-ncus --allow-blob-public-access false
```

4. Confirm:

```
PS > python .\scripts\storage-audit.py    # 0 exposed blob(s) found
```

```
PS > curl https://stazseclab2.blob.core.windows.net/lab-data/mock_pii.csv    # returned `PublicAccessNotPermitted` or `ResourceNotFound` 
```

**Evidence.**

storage-audit.py report:

```
# exposed:

Audit complete
1 exposed blob(s) found

[EXPOSED] stazseclab2/lab-data/mock_pii.csv

Report written to C:\...\azure-cloud-security-lab\incidents\audit-report.json with 1 findings.

# locked:

Audit complete
0 exposed blob(s) found

Report written to C:\...\azure-cloud-security-lab\incidents\audit-report.json with 0 findings.
```

`curl` report:

```
# account switch blocking it:

curl : PublicAccessNotPermittedPublic access is not permitted on this storage account.

# container is locked but the account permits public access:

curl : ResourceNotFoundThe specified resource does not exist.
```

json report:

```
{
    "scan_time": "2026-07-23T18:01:51.700151+00:00",
    "findings": [
        {
            "account": "stazseclab2",
            "container": "lab-data",
            "config_public_access": "PublicAccess.BLOB",
            "exposed": true,
            "blob": "mock_pii.csv",
            "url": "https://stazseclab2.blob.core.windows.net/lab-data/mock_pii.csv",
            "status_code": 200
        } 
    ]
}
```

**Root Cause.** It took two independent controls to fail. Account-level switch, then container-level permission. An accidental leak here is unlikely but not impossible, and the container-level setting is the one more likely to get flipped carelessly.

**Remediation.** Reversed the exposure by disabling public access on both the account and the container. This was verified by running storage-audit.py to confirm that the configuration was off, and an unauthenticated curl to confirm that the data was unreachable.

**Lessons.**

1. Initially, storage-audit.py used a method of listing the container using `?restype=container&comp=list` which is different from reading the file directly by enumerating blobs with authenticated access. Listing the container returned a `404` while reading blobs returned a `200`. The tool reported safe while data was leaking, a dangerous false negative.

2. `curl -O` wrote the response body to mock_pii.csv and exited successfully, but the body was PublicAccessNotPermitted. This is because `curl` treats a `404` as a completed HTTP transaction, so it reports success. The command succeeded; the download didn't.