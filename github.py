from typing import List
from http import HTTPStatus
import requests
import os
from pprint import pprint
from tabulate import tabulate

API_URL = "https://api.github.com"


def table(repos: List[dict]):
    table = repos
    tabulate_table = tabulate(table, headers='keys', tablefmt="fancy_grid")
    return tabulate_table


def count_dependabot_prs(session: requests.Session, repo_name: str) -> int:
    """ Returns the number of pull request created by Dependabot
    """
    update_pr_count = 0
    with session.get(f"{API_URL}/repos/edgelaboratories/{repo_name}/pulls") as resp:
        resp.raise_for_status()
        pulls: List[dict] = resp.json()

    for pull in pulls:
        if pull['user']['login'] == 'dependabot[bot]':
            update_pr_count += 1

    return update_pr_count


def get_repo_info(session: requests.Session, content: dict) -> dict:
    repo = {"name": content["name"]}

    with session.get(f"{API_URL}/repos/edgelaboratories/{repo['name']}/contents/.github/dependabot.yml") as resp:
        if resp.status_code == HTTPStatus.OK:
            repo["active_debendabot"] = True
            repo["dependabot_prs"] = count_dependabot_prs(
                session, content["name"]
            )
        elif resp.status_code == HTTPStatus.NOT_FOUND:
            repo["active_debendabot"] = False
        else:
            resp.raise_for_status()

    if content["visibility"] == "private":
        repo["visibility"] = "private"
    else:
        repo["visibility"] = "public"

    repo["default_branch"] = content["default_branch"]
    with session.get(f"{API_URL}/repos/edgelaboratories/{repo['name']}/branches/{repo['default_branch']}/protection") as resp:
        if resp.status_code == HTTPStatus.OK:
            repo["protected"] = True
        elif resp.status_code == HTTPStatus.NOT_FOUND:
            repo["protected"] = False
        else:
            resp.raise_for_status()

    return repo


def main():
    """Calls the GitHub API to output the number of update PRs, the table data"""
    token = os.environ['GITHUB_TOKEN']

    session = requests.Session()
    session.headers["Authorization"] = f"Token {token}"

    resp = session.get(f"{API_URL}/orgs/edgelaboratories/repos")
    resp.raise_for_status()

    repos = []
    for content in resp.json():
        # TODO: remove me when script is complete, it's just to test
        if content["name"] not in ["marketdata", "ops-tests", "ops-docs", "goliath", "fusion"]:
            continue

        if content["archived"] == False:
            repos.append(get_repo_info(session, content))
    # pprint(content)

    update_prs = count_dependabot_prs(session, content["name"])
    print(
        f'There are currently {update_prs} update PRs in repos with an active dependabot')

    get_repo_info(session, content)

    first_table = table(repos)
    print(first_table)

    # pprint(active_bot_repos[0])


if __name__ == "__main__":
    main()
