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

    return active_bot_repos, inactive_bot_repos


def archived_repos(active_bots):
    """Filters out the archived repos from the repos with active bots as we are not concerned about them"""
    not_archived = []
    for repo in active_bots:
        if repo.archived:
            continue
        else:
            not_archived.append(repo)

    return not_archived


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


def availability(active_bots):
    """Returns if a repo that contains an active bot is private or public"""
    private_repos = []
    public_repos = []
    for repo in active_bots:
        if repo.private:
            private_repos.append(repo)
        else:
            public_repos.append(repo)

    return private_repos, public_repos


def forked_repo(active_bots):
    """Returns if a repo that contains an active bot is a fork"""
    forked_repos = []
    not_forked = []
    for repo in active_bots:
        if repo.fork:
            forked_repos.append(repo)
        else:
            not_forked.append(repo)

    print(f"Forked repos: {forked_repos}")
    print(f"Not Forked repos: {not_forked}")


def main():
    token = os.environ.get("GITHUB_TOKEN")
    g = Github(token)
    # hardcoding repos for now, unil I have token
    repos = [
        g.get_repo("edgelaboratories/fusion"),
        g.get_repo("edgelaboratories/ops-tests"),
        g.get_repo("edgelaboratories/nomad-job-exec"),
        g.get_repo("edgelaboratories/universes-monitor")
    ]

    active_bots, inactive = active_dependabot(repos)
    print(f"Repos with an active bot: {active_bots}")
    print(f"Repos with an inactive bot: {inactive}")
    print()

    not_archived = archived_repos(active_bots)
    print(f"Open PRs, with active bot, that are not archived: {not_archived}")
    print()

    open_prs_no, open_prs_list = open_prs(active_bots)
    print(f"There are {open_prs_no} open PRs")
    print(f"Open PRs: {open_prs_list}")
    print()

    private_repos, public_repos = availability(active_bots)
    print(f"Private repos with active bots: {private_repos}")
    print(f"Public repos with active bots: {public_repos}")

    forked_repo(active_bots)
    # forked_private_repos(private_repos)


if __name__ == "__main__":
    main()
