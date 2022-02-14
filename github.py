import requests
import os
from pprint import pprint

API_URL = "https://api.github.com"


def table(repos):
    pass


def main():
    """Uses the GitHub API to get the repo name, if the repo has an active dependabot, whether the repo is public or private, if the base branch is protected and appends to the list repos"""
    token = os.environ['GITHUB_TOKEN']

    session = requests.Session()
    session.headers["Authorization"] = f"Token {token}"

    resp = session.get(f"{API_URL}/orgs/edgelaboratories/repos")
    resp.raise_for_status()
    gh_repos = [r for r in resp.json() if r["name"] in [
        "marketdata", "ops-tests", "ops-docs", "goliath", "fusion"]]

    repos = []
    active_bot_repos = []
    for gh_repo in gh_repos:
        repo = {"name": gh_repo["name"]}
        repos.append(repo)

        resp = session.get(
            f"{API_URL}/repos/edgelaboratories/{repo['name']}/contents/.github/dependabot.yml")
        if resp.status_code == 200:
            repo["active_debendabot"] = True
            active_bot_repos.append(gh_repo)
        elif resp.status_code == 404:
            repo["active_debendabot"] = False
        else:
            repo["active_debendabot"] = '403 Forbidden'

        if gh_repo["visibility"] == "private":
            repo["visibility"] = "private"
        else:
            repo["visibility"] = "public"

        res = session.get(
            f"{API_URL}/repos/edgelaboratories/{repo['name']}/branches")
        data = res.json()
        for rep in data:
            if rep['protected'] == True:
                repo["protected"] = True
            else:
                repo["protected"] = False

    print(repos)


if __name__ == "__main__":
    main()
