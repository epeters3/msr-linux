from __future__ import (absolute_import, division, print_function)

import argparse
import json
import sys
import re
from datetime import datetime


class Parser:
    def __init__(self, name, regex, dtype=str, preprocessor=None):
        self.name = name
        self.regex = regex
        self.dtype = dtype
        self.preprocessor = preprocessor

    def process(self, obj, text):
        """Add the first match in `text` to the `obj`'s attribute that
        matches this `Parser`'s `name` attribute."""
        matches = re.findall(self.regex, text, re.IGNORECASE)
        if len(matches) > 0:
            match = matches[0]
            if self.preprocessor:
                match = self.preprocessor(match)
            if self.dtype == list:
                getattr(obj, self.name).append(match)
            else:
                setattr(obj, self.name, match)


def safestrptime(datestr, format):
    try:
        return datetime.strptime(datestr, format)
    except ValueError:
        return None


def parsedate(datestr):
    formats = ["%a %b %d %X %Y", "%a, %d %b %Y %X"]
    result = None
    i = 0
    while result is None and i < len(formats):
        result = safestrptime(datestr, formats[i])
        i += 1
    return result


fieldsToExtract = {
    "SHA":
    Parser("SHA", r"commit ([a-zA-Z0-9]{40})"),
    "author":
    Parser("author", r"Author\:.+<(.+@.+)>"),
    "date":
    Parser("date", r"Date:\s+(.+)", str, parsedate),
    "signedOffBy":
    Parser("signedOffBy", r"Signed[-|\s]off[-|\s]by\:.+<(.+@.+)>", list),
    "reviewedBy":
    Parser("reviewedBy", r"Reviewed[-|\s]by\:.+<(.+@.+)>", list),
    "reportedBy":
    Parser("reportedBy", r"Reported[-|\s]by\:.+<(.+@.+)>"),
    "ackedBy":
    Parser("ackedBy", r"Acked[-|\s]by\:.+<(.+@.+)>", list),
    "testedBy":
    Parser("testedBy", r"Tested[-|\s]by\:.+<(.+@.+)>", list),
    "CCd":
    Parser("CCd", r"Cc\:.+<(.+@.+)>", list)
}


class NextCommit:
    """Represents a commit made to the linux-next repository."""

    def __init__(self):
        self.SHA = None
        self.author = None
        self.date = None
        self.signedOffBy = []
        self.reviewedBy = []
        self.reportedBy = []
        self.ackedBy = []
        self.testedBy = []
        self.CCd = []


def reportprogress(itemsprocessed):
    if len(itemsprocessed) % 100 == 0:
        if len(itemsprocessed) % 1000 == 0:
            print("{} complete".format(len(itemsprocessed)))
        else:
            print(".", end="")


def main():
    commits = []
    commit = None
    for line in sys.stdin.readlines():
        if len(re.findall(fieldsToExtract["SHA"].regex, line,
                          re.IGNORECASE)) > 0:
            # We've reached a new commit
            if commit is not None:
                commits.append(commit.__dict__)
                reportprogress(commits)
            commit = NextCommit()

        for parser in fieldsToExtract.values():
            parser.process(commit, line)

    # Add the last commit (it wasn't added in the loop)
    commits.append(commit.__dict__)
    with open("next-parsed.json", "w") as fp:
        json.dump(commits, fp, separators=(',', ':'), default=str)
    sys.stdout.flush()


if __name__ == '__main__':
    main()