from __future__ import (absolute_import, division, print_function)

import json
import re
from datetime import datetime

import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def parsedate(datestr):
    """Parse json date string to datetime"""
    return datetime.strptime(datestr, "%Y-%m-%d %X")


def string2date(datestr):
    """Parse json date string to matplotlib.date"""
    return mdates.date2num(parsedate(datestr))


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


def analyze_dates(commits, filename, minyear=2004, maxyear=2019):
    years = mdates.YearLocator()  # every year
    months = mdates.MonthLocator()  # every month
    yearsFmt = mdates.DateFormatter('%Y')
    # Grab the date of each commit. Filter out bad data
    print("Extracting dates...")
    pltdates = [
        string2date(commit["date"]) for commit in commits
        if int(commit["date"][0:4]) >= minyear
        and int(commit["date"][0:4]) <= maxyear
    ]
    # Plot it out. Source: https://matplotlib.org/examples/api/date_demo.html
    print("Plotting dates...")
    fig, ax = plt.subplots()
    # Have a histogram bar for each quarter of data.
    ax.hist(pltdates, color="green", bins=((maxyear - minyear + 1) * 4))
    # Format the ticks
    ax.xaxis.set_major_locator(years)
    ax.xaxis.set_major_formatter(yearsFmt)
    ax.xaxis.set_minor_locator(months)
    ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
    fig.autofmt_xdate()
    plt.savefig("./reports/{}".format(filename))
    print("Finished.")


def find_contributor_ranges(commits, filename):
    contrib_sets = {}
    # Track which years each contributor contributed in.
    print("Tracking contribution years...")
    for commit in commits:
        commit_year = int(commit["date"][0:4])
        for person in commit["signedOffBy"]:
            if person not in contrib_sets:
                contrib_sets[person] = set([])
            contrib_sets[person].add(commit_year)
    print("Aggregating contribution years...")
    contrib_cnts = [len(s) for s in contrib_sets.values()]
    print("Plotting...")
    fig, ax = plt.subplots()
    max_cnt = max(contrib_cnts)
    ax.hist(contrib_cnts, bins=max_cnt, density=True, stacked=True)
    plt.xticks(range(1, max_cnt + 1))
    plt.xlabel("Number of years contributed in")
    plt.ylabel("Portion of the whole")
    # Format the ticks
    plt.savefig("./reports/{}".format(filename))
    print("Finished.")


def main(filename, topn):
    commits = None
    print("Now loading '{}'...".format(filename))
    with open(filename, "r") as fp:
        commits = json.load(fp)
    print("Finished loading file.")
    # contrib_list = find_top_contributors(commits, topn, .8)
    # find_top_email_domians(contrib_list, topn)
    # analyze_dates(commits, "commit-hist.png")
    find_contributor_ranges(commits, "longevity-hist.png")


if __name__ == '__main__':
    main("mainline-parsed.json", 71)