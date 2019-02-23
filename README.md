# Analyizing The Linux Repository

## Using `git-log-parser.py`

Pipe the logs of a linux repo e.g. `linux-next` or `mainline` to `git-log-parser.py` using this format:

```shell
git log --date=local | python git-log-parser.py
```

You can optionally add the `--no-merges` option to `git-log` to exclude all merge commits. Helpful if you just want to identify original work added to the kernel.

The output of this script will be saved as a `.json` file.
