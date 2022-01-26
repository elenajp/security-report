#!/usr/bin/env python3
import click
import requests
import os
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


# # using an access token
# g = Github("access_token")

# # Github Enterprise with custom hostname
# g = Github(base_url="https://{hostname}/api/v3", login_or_token="access_token")

token = os.getenv('GITHUB_TOKEN', '...')
g = Github(token)
repo = g.get_repo("MartinHeinz/python-project-blueprint")
issues = repo.get_issues(state="open")
pprint(issues.get_page(0))


# @click.option():
