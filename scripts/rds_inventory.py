#!/usr/bin/env python3
"""
Template script: RDS & Aurora inventory across multiple AWS accounts.

- Adjust the ACCOUNTS list with your own AWS profiles.
- Adjust the REGIONS list with the regions you want to scan.
"""

import boto3
import csv
from datetime import datetime

# TODO: replace these with your real AWS profiles and friendly aliases
ACCOUNTS = [
    {"profile": "account-dev", "alias": "dev"},
    {"profile": "account-staging", "alias": "staging"},
    {"profile": "account-prod", "alias": "prod"},
]

# TODO: adjust the regions you want to scan
REGIONS = ["us-east-1", "sa-east-1"]

OUTPUT_FILE = f"rds_inventory_{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}.csv"


def get_account_metadata(session):
    """Return account_id and alias (if exists)."""
    sts = session.client("sts")
    identity = sts.get_caller_identity()
    account_id = identity["Account"]

    iam = session.client("iam")
    try:
        aliases = iam.list_account_aliases().get("AccountAliases", [])
        account_alias = aliases[0] if aliases else ""
    except Exception:
        account_alias = ""

    return account_id, account_alias


def list_rds_resources(session, region):
    """List RDS instances and Aurora clusters for a given region."""
    rds = session.client("rds", region_name=region)
    resources = []

    # RDS Instances
    paginator = rds.get_paginator("describe_db_instances")
    for page in paginator.paginate():
        for db in page["DBInstances"]:
            endpoint = db.get("Endpoint", {})
            resources.append(
                {
                    "resource_type": "instance",
                    "identifier": db["DBInstanceIdentifier"],
                    "engine": db["Engine"],
                    "engine_version": db.get("EngineVersion", ""),
                    "endpoint": endpoint.get("Address", ""),
                    "port": endpoint.get("Port", ""),
                    "region": region,
                }
            )

    # Aurora Clusters
    paginator = rds.get_paginator("describe_db_clusters")
    for page in paginator.paginate():
        for cluster in page["DBClusters"]:
            # Writer endpoint
            resources.append(
                {
                    "resource_type": "cluster-writer",
                    "identifier": cluster["DBClusterIdentifier"],
                    "engine": cluster["Engine"],
                    "engine_version": cluster.get("EngineVersion", ""),
                    "endpoint": cluster.get("Endpoint", ""),
                    "port": cluster.get("Port", ""),
                    "region": region,
                }
            )
            # Reader endpoint (if exists)
            if cluster.get("ReaderEndpoint"):
                resources.append(
                    {
                        "resource_type": "cluster-reader",
                        "identifier": cluster["DBClusterIdentifier"],
                        "engine": cluster["Engine"],
                        "engine_version": cluster.get("EngineVersion", ""),
                        "endpoint": cluster.get("ReaderEndpoint"),
                        "port": cluster.get("Port", ""),
                        "region": region,
                    }
                )

    return resources


def main():
    rows = []

    for account in ACCOUNTS:
        profile = account["profile"]
        alias_hint = account["alias"]

        print(f"[INFO] Collecting RDS data from profile: {profile}")

        session = boto3.Session(profile_name=profile)
        account_id, account_alias = get_account_metadata(session)
        effective_alias = account_alias or alias_hint

        for region in REGIONS:
            print(f"  - Region: {region}")
            resources = list_rds_resources(session, region)
            for r in resources:
                rows.append(
                    {
                        "account_profile": profile,
                        "account_alias": effective_alias,
                        "account_id": account_id,
                        "region": r["region"],
                        "resource_type": r["resource_type"],
                        "identifier": r["identifier"],
                        "engine": r["engine"],
                        "engine_version": r["engine_version"],
                        "endpoint": r["endpoint"],
                        "port": r["port"],
                    }
                )

    fieldnames = [
        "account_profile",
        "account_alias",
        "account_id",
        "region",
        "resource_type",
        "identifier",
        "engine",
        "engine_version",
        "endpoint",
        "port",
    ]

    with open(OUTPUT_FILE, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"[INFO] Inventory written to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
