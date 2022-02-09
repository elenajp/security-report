from pydoc import text
from data import repos
from decimal import Decimal
from github.GithubException import UnknownObjectException
from tabulate import tabulate


# The expected output
result = """\
# Security checks

- There are currently 37 update PRs on repos with an active dependabot.
- Of which 1 do not have branch protection enabled.

 Repository          |  # / max | Team            | Age of the oldest  | Branch protection
---------------------+----------+-----------------+--------------------+-------------------
   rooster             10 /10     infra             1 day                ✅
   dawn-vault           8 /10     infra             3 weeks              ✅
   picsou               5 /5      pre-pricing                            ❌
   dawn-base            2 /10     portfolio                              ✅
---------------------+----------+-----------------+--------------------+-------------------

# Branch protection trespassers

Steve 10 times, on picsou, rooster, and dawn-vault.
Cyril 2 times, on stacks, and dawn-boostrap.
Vincent 1 time, on stacks.
"""


def update_prs_number(repos):
    """Get the total number of update prs from the fake data"""
    update_prs_list = []
    for repo in repos:
        for pr in repo['prs']['update_prs']:
            update_prs_list.append(pr)

    total_update_prs = (sum(Decimal(update) for update in update_prs_list))
    return total_update_prs


def list_branches():
    branches = []
    for repo in repos:
        for branch in repo['branches']:
            branches.append(branch)
    return len(branches)


def repo_names(repos):
    """Gets the repo names"""
    repo_names = []
    for repo in repos:
        repo_names.append(repo['name'])

    return repo_names


def visibility(repos):
    """Checks if the repo is private or public"""
    repo_visibility = []
    for repo in repos:
        if repo['private'] == True:
            repo_visibility.append('Private')
        else:
            repo_visibility.append('Public')

    return repo_visibility


def active_dependabot(repos):
    """Checks if a dependabot is active in a repo and returns lists of repos that have a dependabot
    active and inactive."""
    dependabot = []

    for repo in repos:
        # when using the API I will need to use repo.get_contents(".github/dependabot.yml")
        if repo['contents'] == ".gitignore/dependabot.yml":
            dependabot.append('Y')
        else:
            dependabot.append('X')

    return dependabot


def branch_protection(repos):
    """Checks if the default (base) branch has branch protection enabled"""
    protection = []
    for repo in repos:
        if repo['default_branch']['protected'] == True:
            protection.append('Y')
        else:
            protection.append('X')
    return protection


def table(names, vis, bot, protection):
    headers = ['Repo name', 'visibility',
               'dependabot', 'branch protection']
    table_list = []
    my_vars = names, vis, bot, protection
    table_list += my_vars

    zip_table_data = tuple(zip(*table_list))
    return tabulate(zip_table_data, headers, tablefmt="fancy_grid")


def trespassers():
    pass


def main():
    """Prints the expected output with the fake data"""
    names = repo_names(repos)
    vis = visibility(repos)
    bot = active_dependabot(repos)
    protection = branch_protection(repos)

    update_prs = update_prs_number(repos)
    all_branches = list_branches()

    print(
        f"""
        - There are currently {update_prs} update PRs on repos with an active dependabot.
        - Of which {all_branches} do not have branch protection enabled.
        """)

    output = table(names, vis, bot, protection)
    print(output)


if __name__ == "__main__":
    main()
