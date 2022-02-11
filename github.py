import requests
import os

API_URL = "https://api.github.com"


def main():
    token = os.environ['GITHUB_TOKEN']

    session = requests.Session()
    session.headers["Authorization"] = f"Token {token}"

    resp = session.get(f"{API_URL}/orgs/edgelaboratories/repos")
    resp.raise_for_status()
    gh_repos = [r for r in resp.json() if r["name"] in [
        "marketdata", "ops-tests", "fustion", "ops-docs", "goliath"]]
    # gh_repos = resp.json()

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

        if gh_repo['private'] == True:
            repo['visibility'] = 'private'
        else:
            repo['visibility'] = 'public'

    print(repos)
    print()
    print()
    # return active_bot_repos
    print(active_bot_repos)

    # repos will be something like
    # [
    #    {"name": "ops-tests", "active_dependabot": False, },
    #    {"name": "arcanist", "active_dependabot": True, }
    # ]
    #
    # Fancy display


if __name__ == "__main__":
    main()
