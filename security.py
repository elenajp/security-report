"""This module creates a CLI tool that reports security compliance issues..."""  # more to add

# import click
import os
from github import Github
from github.GithubException import UnknownObjectException


def active_dependabot(repos):
    """Checks if a dependabot is active in a repo and returns lists of repos that have a dependabot 
    active and inactive """
    active_bot_repos = []
    inactive_bot_repos = []

    for repo in repos:
        try:
            repo.get_contents(".github/dependabot.yml")
        except UnknownObjectException:
            inactive_bot_repos.append(repo)
        else:
            active_bot_repos.append(repo)

    # print(f"These repos have active bots: {active_bot_repos}")
    return active_bot_repos, inactive_bot_repos


def open_prs(active_bots):
    """Returns the number of open PRs and returns a list of the open PRs that have an
    active dependabot"""
    open_prs_list = []
    open_prs_no = 0

    for rep in active_bots:
        pulls = rep.get_pulls(state='open', sort='created',
                              base='rep.default_branch')

        for pr in pulls:
            if pr["user"]["login"] == "dependabot[bot]":
                open_prs_list.append(pr.title)
                open_prs_no += 1

    return open_prs_no, open_prs_list

    # g.get_repo("edgelaboratories/fusion").get_pull(3).raw_data
    # {'user': {'login': 'vthiery'} }
    # x = g.get_repo("edgelaboratories/fusion").get_pull(3).raw_data
    # print(x["user"]["login"])
    # In [103]: if x["user"]["login"] == "vthiery":
    #  print("yes")
    return


def main():
    token = os.environ.get("GITHUB_TOKEN")
    g = Github(token)
    # hardcoding repos for now, unil I have token
    repos = [
        g.get_repo("edgelaboratories/fusion"),
        g.get_repo("edgelaboratories/ops-tests"),
        g.get_repo("edgelaboratories/nomad-job-exec"),
        g.get_repo("edgelaboratories/beat-exporter")
    ]

    active_bots, inactive = active_dependabot(repos)
    print(f"Repos with an active bot: {active_bots}")
    print(f"Repos with an inactive bot: {inactive}")

    # branch_name(repo_names)
    # repo.edit(private=False)
    # g.get_repo("edgelaboratories/fusion").archived
    # g.get_repo("edgelaboratories/fusion").fork returns boolean or .get_forks()

    # open_prs, open_prs_list = open_prs(active_bots)
    # print(f"Open prs: {open_prs}, Open prs list: {open_prs_list}")

    open_prs_no, open_prs_list = open_prs(active_bots)
    print(f"There are {open_prs_no} open PRs")
    print(f"Open PRs: {open_prs_list}")


if __name__ == "__main__":
    main()
