#!/usr/bin/env python3
import click
import requests
from github import Github
from pprint import pprint

# use CLICK to make a CLI tool to report security issues
# use GITHUB API to see if there are such logs and report them into this tool.
# use PYGITHUB library to access the GITHUB API

# Check for bot to see if it is enabled
# dependabot is active on repos, repos have reponame/.github/dependabot.yml file so
# we should report the number.
# check if the dependabot.yml file is present in the repos or not (reference) using
# GET to api.github.com/repos/name/repo/contents/fileNameOrPath.

# GRAPHYQL you write simple queries, get the data

# find edgelab paht to make api calls with pygithub

username = "edgelaboratories"
github_url = "https://github.com/edgelaboratories"
github_data = requests.url(github_url).json()
pprint(github_data)


# @click.option():
