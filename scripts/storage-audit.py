# Jeffar - Azure Storage Auditor
# Description - This script lists Azure storage accounts in a subscription, checks their public access settings,
#               and tests blob containers for anonymous accessibility using Azure SDKs and HTTP requests.
# Created - 2026-07-22
# Last updated - 2026-07-22

# Modules
from azure.identity import DefaultAzureCredential       # for authenticating with azure using default credentials
from azure.mgmt.storage import StorageManagementClient  # for managing azure storage accounts
from azure.mgmt.storage.models import PublicAccess      # for proper import of the PublicAccess enum
from azure.storage.blob import BlobServiceClient        # for interacting with blob services and listing blobs
from datetime import datetime, timezone                 # for recording scan_time
import requests                                         # for making http requests to check blob container accessibility
import json                                             # for exporting to json
import os                                               # for path

# Constants
SUBSCRIPTION_ID = "61525bb8-ad35-470e-8a23-c4b34ed21135"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)) # absolute path to the folder this script lives in
REPO_ROOT = os.path.dirname(SCRIPT_DIR)                 # repo root is one level up from scripts/
INCIDENTS_DIR = os.path.join(REPO_ROOT, "incidents")    # incidents/

# Main Function
def main():
    try:
        credential = DefaultAzureCredential()                           # initialize the credential object
        client = StorageManagementClient(credential, SUBSCRIPTION_ID)   # initialize the storage management client

        findings = scan_accounts(client, credential)
        report = build_report(findings)

        print_summary(findings)
        export_json(report)

    except Exception as err:                                            # incase of network or auth failures
        print(f"An error occurred: {err}")

# Functions
def scan_accounts(client, credential):
    """
    scan_accounts - lists every storage account and tests each container for anonymous exposure

    client - authenticated StorageManagementClient

    credential - DefaultAzureCredential, reused for data-plane blob listing
    """

    findings = []                                                       # holds each exposed-blob finding as a dict

    # list all storage accounts in the subscription
    accounts = client.storage_accounts.list()
    for account in accounts:
        rg = account.id.split("/")[4]                                   # get the resource group by splitting account.id

        # list all containers in the account, testing each for exposure
        containers = client.blob_containers.list(rg, account.name)
        for container in containers:
            scan_container(account, container, credential, findings)    # append any findings from this container

    return findings

def scan_container(account, container, credential, findings):
    """
    scan_container - tests one container's blobs for anonymous readability, appending exposures to findings

    account - the storage account object the container belongs to

    container - the container object to test

    credential - DefaultAzureCredential, for authorized blob listing

    findings - the shared list to append exposed-blob findings to
    """

    # skip locked containers; only test ones config marks as public
    if container.public_access == PublicAccess.NONE:
        return

    # authenticated: build a data-plane client to discover blob names
    account_url = f"https://{account.name}.blob.core.windows.net"           # construct the account url
    blob_service = BlobServiceClient(account_url, credential=credential)    # create a BlobServiceClient with DefaultAzureCredential()
    container_client = blob_service.get_container_client(container.name)    # get the container client

    # list the blobs while authorized
    for blob in container_client.list_blobs():

        # unauthenticated: test if this specific blob is publicly reachable
        blob_url = f"{account_url}/{container.name}/{blob.name}"

        # make an http get request
        response = requests.get(blob_url)                                   # no auth headers since this is an anonymous test

        if response.status_code == 200:
            findings.append({
                "account": account.name,
                "container": container.name,
                "config_public_access": str(container.public_access),
                "exposed": True,
                "blob": blob.name,
                "url": blob_url,
                "status_code": response.status_code,
            })

def build_report(findings):
    """
    build_report - wraps the findings list with scan metadata into a single report dict

    findings - list of finding dicts
    """

    # write report dict
    return {
        "scan_time": datetime.now(timezone.utc).isoformat(),            # utc timestamp so the record is timezone-unambiguous
        "findings": findings,
    }

def print_summary(findings):
    """
    print_summary - prints a count and one line per exposed blob to the terminal

    findings - list of finding dicts
    """

    print(f"\nAudit complete")
    print(f"{len(findings)} exposed blob(s) found\n")
    for finding in findings:
        print(f"[EXPOSED] {finding['account']}/{finding['container']}/{finding['blob']}")
    if len(findings) != 0: print()

def export_json(report, filename=None):
    """
    export_json - writes the audit report dict to a json file

    report   - dict containing scan_time and findings

    filename - output path including directory and extension: initialized to None
    """

    # put file in incidents/
    if filename is None:
        filename = os.path.join(INCIDENTS_DIR, "audit-report.json")

    os.makedirs(os.path.dirname(filename), exist_ok=True)           # ensure incidents/ exists

    with open(filename, "w", encoding="utf-8") as file:             # writes to savepath in utf-8 and create object file
        json.dump(report, file, indent=4)                           # write report to file with most used tab indentation

    abs_path = os.path.abspath(filename)                            # convert to absolute path to make it ctrl-clickable (sometimes...)

    print(f"Report written to {abs_path} with {len(report['findings'])} findings.\n")

# dunder name guard
if __name__ == "__main__":
    main()