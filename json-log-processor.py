from __future__ import (absolute_import, division, print_function)

import json
import re
from datetime import datetime


def parsedate(datestr):
    # Example of the .json format: 2019-02-14 16:02:18
    return datetime.strptime(datestr, "%Y-%m-%d %X")


def safe_add_to_key(dct, key, value, default=0):
    dct[key] = dct.get(key, default) + value


def find_top_email_domians(contrib_list, topn):
    domain_regex = r"@(.+?)\."
    email_cnts = {}
    for contrib in contrib_list[0:topn]:
        domain = re.findall(domain_regex, contrib[0])
        safe_add_to_key(email_cnts, domain[0], 1)
    domain_list = [(domain, count) for domain, count in email_cnts.iteritems()]
    domain_list.sort(key=lambda toop: toop[1], reverse=True)
    print("The top email domains of the top {} contributors are:".format(topn))
    for domain in domain_list:
        print("{} -> {} occurences".format(domain[0], domain[1]))


def find_top_contributors(commits, topn, topperct):
    contrib_cnts = {}
    # Count the number of contributions each person made, using
    # the "Signed-off-by" field to identify contribution.
    num_no_signedoff = 0
    for commit in commits:
        if len(commit["signedOffBy"]) == 0:
            num_no_signedoff += 1
        else:
            for person in commit["signedOffBy"]:
                safe_add_to_key(contrib_cnts, person, 1)
    contrib_list = [(person, count)
                    for person, count in contrib_cnts.iteritems()]

    # Sort the list by contribution count.
    contrib_list.sort(key=lambda toop: toop[1], reverse=True)

    print("{} / {} ({}%) of commits had no Signed-off-by tag".format(
        num_no_signedoff, len(commits),
        round((num_no_signedoff / len(commits) * 100), 2)))

    print("\nTotal number of contributors: {}".format(len(contrib_list)))

    print("\nTop {} contributors:".format(topn))
    for contrib in contrib_list[0:topn]:
        print("{} -> {} commits".format(contrib[0], contrib[1]))

    num_to_topperct = len(commits) * topperct
    num_contribs_to_topperct = 0
    accumulation = 0
    for contrib in contrib_list:
        accumulation += contrib[1]
        num_contribs_to_topperct += 1
        if accumulation > num_to_topperct:
            break
    print(
        "\nThe top {} / {} ({}%) contributors are at least in part responsible for {} / {} ({}%) of all contributions."
        .format(num_contribs_to_topperct, len(contrib_list),
                round(num_contribs_to_topperct / len(contrib_list) * 100, 2),
                accumulation, len(commits),
                round(accumulation / len(commits) * 100, 2)))

    return contrib_list


def analyze_dates(commits):
    pass


def main(filename, topn):
    commits = None
    print("Now loading '{}'...".format(filename))
    with open(filename, "r") as fp:
        commits = json.load(fp)
    print("Finished loading file.")
    contrib_list = find_top_contributors(commits, topn, .8)
    # find_top_email_domians(contrib_list, topn)


if __name__ == '__main__':
    main("mainline-parsed.json", 71)