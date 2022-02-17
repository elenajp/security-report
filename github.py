from collections import defaultdict
from email.policy import default
import json
import jwt
import time
from typing import Dict, List
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


def get_bypassers(session: requests.Session) -> dict[str, dict[str, int]]:
    """Returns the name of the bypasser, the repo bypassed and how many times"""
    branch_bypasses = defaultdict(lambda: defaultdict(int))

    with session.get(f"{API_URL}/orgs/edgelaboratories/audit-log", params={"per_page": 100, "phrase": "action:protected_branch.policy_override"}) as resp:
        resp.raise_for_status()
        next_page = resp.links.get("next")
        if next_page is not None:
            print("TODO: There is other pages to process")
        logs = resp.json()

        for log in logs:
            if log['action'] == 'protected_branch.policy_override':
                # branch_bypass_actors[log['actor']] = branch_bypass_actors.get(
                #     log['actor'], 0) + 1
                branch_bypasses[log['actor']][log['repo']] += 1

    return branch_bypasses
    # TODO:
    # count how many override per actor
    # [
    #   {
    #     "repo": "edgelaboratories/stacks",
    #     "actor": "vthiery",
    #     "org": "edgelaboratories",
    #     "branch": "refs/heads/master",
    #     "action": "protected_branch.policy_override",
    #     "@timestamp": 1641796648783,
    #     "_document_id": "pCtl2n0J8njxnR8oUOEpuw",
    #     "created_at": 1641796648783,
    #     "actor_location": {
    #     "country_code": "CH"
    #     }
    #   }
    # ]
    # {"vthiery": {"edgelaboratories/stacks": 3, "another": 5}}
    print(f"There are {len(logs)} to process")
    print(f"Elena, do your job :p ")


def get_repo_info(session: requests.Session, content: dict) -> dict:
    """Returns """
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


def get_github_token() -> str:
    github_app_id = 172532
    github_org = "edgelaboratories"
    now = int(time.time())
    payload = {
        # issued at time, 60 seconds in the past to allow for clock drift
        "iat": now - 60,
        # JWT expiration time (10 minute maximum)
        "exp": now + 60,
        # GitHub App's identifier
        "iss": github_app_id,
    }

    with open("./github.pem", "r") as f:
        private_key = f.read()

    token = jwt.encode(payload, private_key, algorithm="RS256")

    with requests.get(
        f"{API_URL}/app/installations", headers={"Authorization": f"Bearer {token}"}
    ) as resp:
        resp.raise_for_status()
        installations = resp.json()

    for install in installations:
        if install['account']['login'] == github_org:
            install_id = install['id']
            break
    else:
        raise ValueError(
            f"could not find installation for the app {github_app_id} in {github_org} org"
        )

    with requests.post(
        f"{API_URL}/app/installations/{install_id}/access_tokens", headers={"Authorization": f"Bearer {token}"}
    ) as resp:
        resp.raise_for_status()
        content = resp.json()

    token = content["token"]
    return token


def check_repositories(session: requests.Session):
    resp = session.get(f"{API_URL}/orgs/edgelaboratories/repos")
    resp.raise_for_status()

    repos = []
    for content in resp.json():
        # TODO: remove me when script is complete, it's just to test
        if content["name"] not in ["marketdata", "ops-tests", "ops-docs", "goliath", "fusion"]:
            continue

        if content["archived"] == False:
            repos.append(get_repo_info(session, content))

    return repos, content


def main():
    """Calls the GitHub API to output the number of update PRs, the table data"""
    token = get_github_token()

    session = requests.Session()
    session.headers["Authorization"] = f"Token {token}"

    repos, content = check_repositories(session)
    get_repo_info(session, content)
    update_prs = count_dependabot_prs(session, content["name"])
    print(
        f'There are currently {update_prs} update PRs in repos with an active dependabot')

    first_table = table(repos)
    print(first_table)
    get_bypassers(session)


if __name__ == "__main__":
    main()
