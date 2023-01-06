#!/usr/bin/env python

"""Gets the DMARC policy of domains hosting Mastodon instances"""

from argparse import ArgumentParser
from io import StringIO
import csv

import simplejson
from requests_toolbelt import user_agent, sessions
import checkdmarc

__version__ = "1.0.0"

instance_csv_fields = ["name", "description", "email", "admin",
                       "active_users", "users", "posts",
                       "connections", "dmarc_policy"]


class MastodonInstancesClient:
    def __init__(self, api_key):
        headers = {"User-Agent": user_agent("checkdmarc-mastodon", __version__),
                   "Authorization": f"Bearer {api_key}"}
        base_url = "https://instances.social/api/1.0/"
        self._session = sessions.BaseUrlSession(base_url=base_url)
        self._session.headers = headers

    def get_random_instances(self, **kwargs):
        return self._session.get("instances/sample", params=kwargs).json()["instances"]

    def list_instances(self, **kwargs):
        return self._session.get("instances/list", params=kwargs).json()["instances"]

    def search_instances(self, **kwargs):
        return self._session.get("instances/search", params=kwargs).json()["instances"]

    def get_instance(self, name):
        return self._session.get("instances/show", params=dict(name=name)).json()["instances"]

    def list_versions(self, **kwargs):
        return self._session.get("versions/list", params=kwargs).json()["versions"]

    def get_version(self, name):
        return self._session.get("version/show", params=dict(name=name)).json()["versions"]


def _main():
    with open("key.txt") as key_file:
        api_key = key_file.readline().strip()
        args = ArgumentParser(description=__doc__)
        args.add_argument("--version", "-V",
                          action="version",
                          version=__version__)
        count_help = "The number of instances to check, based on the " \
                     "descending number of active users (0 for all)"
        args.add_argument("--count", "-c", type=int, default=1000,
                          help=count_help)
        args.add_argument("--json", "-j", action="store_true", help="Output in verbose JSON format")
        args.add_argument("--output", "-o", help="Redirect output to a file")
        args = args.parse_args()
        client = MastodonInstancesClient(api_key)
        instances = client.list_instances(count=args.count, include_down="false",
                                          sort_by="active_users",
                                          sort_order="desc")
        for i in range(len(instances)):
            instance = instances[i]
            try:
                dmarc_record = checkdmarc.get_dmarc_record(
                    instance["name"], timeout=.5)
                dmarc_policy = dmarc_record["parsed"]["tags"]["p"]["value"]
                if dmarc_policy == "none":
                    dmarc_policy = "Monitoring only (p=none)"
                elif dmarc_policy == "quarantine":
                    dmarc_policy = "Enforced (p=quarantine)"
                elif dmarc_policy == "reject":
                    dmarc_policy = "Enforced (p=reject)"
            except checkdmarc.DMARCRecordNotFound:
                dmarc_policy = "Missing"
            except checkdmarc.DMARCError:
                dmarc_policy = "Invalid"
            except checkdmarc.DNSException:
                dmarc_policy = "Invalid"
            instance["dmarc_policy"] = dmarc_policy
            instances[i] = instance

    output = simplejson.dumps(instance)
    if not args.json:
        csv_file = StringIO(newline="\n")
        csv_writer = csv.DictWriter(csv_file, fieldnames=instance_csv_fields)
        csv_writer.writeheader()
        for instance in instances:
            instance["posts"] = instance["statuses"]
            instance["description"] = ""
            if instance["info"] is not None:
                try:
                    description = instance["info"]["short_description"]
                    instance["description"] = description
                except KeyError:
                    pass
            row = {}
            for field in instance_csv_fields:
                row[field] = instance[field]
            csv_writer.writerow(row)
        csv_file.seek(0)
        output = csv_file.read()
    if args.output:
        with open(args.output, "w", newline="\n", encoding="utf-32", errors="ignore") as output_file:
            output_file.write(output)
    else:
        print(output)


if __name__ == "__main__":
    _main()
