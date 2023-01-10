#!/usr/bin/env python

"""Gets the DMARC policy of domains hosting Mastodon instances"""

import logging
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from io import StringIO
import csv

import simplejson
from requests_toolbelt import user_agent, sessions
import checkdmarc

__version__ = "1.1.0"

instance_csv_fields = ["name", "description", "email", "admin",
                       "logins_per_week", "users", "posts",
                       "connections", "dnssec", "spf_valid", "dmarc_policy",
                       "errors", "warnings"]


class MastodonInstancesClient:
    def __init__(self, api_key):
        headers = {"User-Agent": user_agent("mastodon-dmarc-survey", __version__),
                   "Authorization": "Bearer {}".format(api_key)}
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
        return self._session.get("instances/show", params=dict(name=name)).json()

    def list_versions(self, **kwargs):
        return self._session.get("versions/list", params=kwargs).json()["versions"]

    def get_version(self, name):
        return self._session.get("version/show", params=dict(name=name)).json()


def _main():
    with open("key.txt") as key_file:
        api_key = key_file.readline().strip()
        args = ArgumentParser(description=__doc__,
                              formatter_class=ArgumentDefaultsHelpFormatter)
        args.add_argument("--version", "-V",
                          action="version",
                          version=__version__)
        count_help = "The number of instances to check, based on the " \
                     "descending number of active users (0 for all)"
        args.add_argument("--count", "-c", type=int, default=1000,
                          help=count_help)
        args.add_argument("--instance", "-i", help="Get information about a single specific instance")
        args.add_argument("--json", "-j", action="store_true", help="Output in verbose JSON format")
        args.add_argument("--output", "-o", help="Redirect output to a file")
        args.add_argument("--debug", "-d", action="store_true", help="Enable debug output")
        args = args.parse_args()
        log_level = logging.INFO
        if args.debug:
            log_level = logging.DEBUG
            logging.basicConfig(format='%(levelname)s: %(message)s',
                                level=log_level)
            logging.debug("Debug logging enabled...")
        client = MastodonInstancesClient(api_key)
        if args.instance is None:
            logging.debug("Getting the list of instances...")
            instances = client.list_instances(count=args.count, include_down="false",
                                              sort_by="active_users",
                                              sort_order="desc")
        else:
            instances = [client.get_instance(args.instance)]
        for i in range(len(instances)):
            errors = []
            warnings = []
            instance = instances[i]
            logging.debug("Checking {}...".format(instance["name"]))
            # Convert fields names to something more accurate
            instance["posts"] = instance["statuses"]
            del instance["statuses"]
            instance["logins_per_week"] = instance["active_users"]
            del instance["active_users"]
            try:
                dnssec = checkdmarc.test_dnssec(instance["name"])
            except checkdmarc.DNSException:
                dnssec = False
            instance["dnssec"] = dnssec
            try:
                dmarc_record = checkdmarc.get_dmarc_record(
                    instance["name"], timeout=1.0)
                for warning in dmarc_record["parsed"]["warnings"]:
                    warnings.append("DMARC: {}".format(warning))
                dmarc_policy = dmarc_record["parsed"]["tags"]["p"]["value"]
                if dmarc_policy == "none":
                    dmarc_policy = "Monitoring only (p=none)"
                elif dmarc_policy == "quarantine":
                    dmarc_policy = "Enforced (p=quarantine)"
                elif dmarc_policy == "reject":
                    dmarc_policy = "Enforced (p=reject)"
            except checkdmarc.DMARCRecordNotFound as e:
                dmarc_policy = "Missing"
                errors.append("DMARC: {}".format(str(e)))
            except checkdmarc.DMARCError as e:
                dmarc_policy = "Invalid"
                errors.append("DMARC: {}".format(str(e)))
            except checkdmarc.DNSException as e:
                dmarc_policy = "Invalid"
                errors.append("DMARC: {}".format(str(e)))
            instance["spf_valid"] = True
            try:
                spf_record = checkdmarc.get_spf_record(
                    instance["name"], timeout=.5)
                for warning in spf_record["warnings"]:
                    warnings.append("SPF: {}".format(warning))
            except checkdmarc.SPFError as e:
                instance["spf_valid"] = False
                errors.append("SPF: {}".format(e))
            instance["dmarc_policy"] = dmarc_policy
            instance["errors"] = errors
            instance["warnings"] = warnings

            instances[i] = instance

    output = simplejson.dumps(instances, indent=2)
    if not args.json:
        csv_file = StringIO(newline="\n")
        csv_writer = csv.DictWriter(csv_file, fieldnames=instance_csv_fields)
        csv_writer.writeheader()
        for instance in instances:
            instance["description"] = ""
            instance["errors"] = "|".join(instance["errors"])
            instance["warnings"] = "|".join(instance["warnings"])
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
        with open(args.output, "w", newline="\n", encoding="utf-8", errors="replace") as output_file:
            output_file.write(output)
    else:
        print(output)


if __name__ == "__main__":
    _main()
