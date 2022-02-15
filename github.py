import requests
import os
from pprint import pprint
from tabulate import tabulate

API_URL = "https://api.github.com"


def table(repos):
    table = repos
    tabulate_table = tabulate(table, headers='keys', tablefmt="fancy_grid")
    return tabulate_table
    # change this to return and print in main function, add docstring


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
    update_prs = []
    for gh_repo in gh_repos:
        repo = {"name": gh_repo["name"]}
        repos.append(repo)
        # pprint(gh_repos[0])

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

        resp = session.get(
            f"{API_URL}/repos/edgelaboratories/{repo['name']}/branches")
        resp.json()
        if resp.status_code == 200:
            repo["protected"] = True
        else:
            repo["protected"] = False

    for active_bot in active_bot_repos:
        resp = session.get(
            f"{API_URL}/repos/edgelaboratories/{active_bot['name']}/pulls")
        if resp.status_code == 200:
            update_prs.append(active_bot['updated_at'])
    print(
        f'There are currently {len(update_prs)} update PRs in repos with an active dependabot')

    first_table = table(repos)
    print(first_table)


if __name__ == "__main__":
    main()
