from github import count_dependabot_prs, get_bypassers
import requests
import pytest
from unittest.mock import MagicMock


@pytest.mark.parametrize("fake_pulls,expected_count",  [
    # No pull requests
    ([], 0),

    # One PR not created by Dependabot
    (
        [
            {
                'number': 1,
                'state': 'open',
                'title': 'This is a very cool PR',
                'user': {'login': 'toto'}
            },
        ],

        0
    ),

    # 3 PRs and 2 created by dependabot
    (
        [
            {
                'number': 448,
                'state': 'open',
                'title': 'maven(deps): bump swagger-request-validator-core from 2.15.1 to 2.25.0 in /copernic',
                'user': {'login': 'dependabot[bot]'}
            },
            {
                'number': 439,
                'state': 'open',
                'title': 'Reword dependabot commit message prefix',
                'user': {'login': 'A-Ibm'}
            },
            {
                'number': 198,
                'state': 'open',
                'title': 'Bump spring-boot-starter-parent from 2.1.5.RELEASE to 2.2.5.RELEASE',
                'user': {'login': 'dependabot-preview[bot]'}
            }
        ],

        1
    ),
])
def test_count_dependabot_prs(fake_pulls, expected_count):
    mock_session = MagicMock(spec=requests.Session)
    mock_session.get().__enter__().json.return_value = fake_pulls

    assert count_dependabot_prs(mock_session, "fake_repo") == expected_count


@pytest.mark.parametrize('fake_audit_logs, expected_bypassers', [
    # If no git logs, no bypass
    ([], {}),

    (
        [
            {'repo': 'edgelaboratories/stacks',
             'action': 'protected_branch.policy_override', 'branch': 'refs/heads/master', 'actor': 'cyrilgdn', 'org': 'edgelaboratories'},

            {'repo': 'edgelaboratories/pigeon',
             'action': 'protected_branch.policy_override', 'branch': 'refs/heads/master', 'actor': 'vthiery', 'org': 'edgelaboratories'},

            {'repo': 'edgelaboratories/eve',
             'action': 'protected_branch.policy_override', 'branch': 'refs/heads/master', 'actor': 'cyrilgdn', 'org': 'edgelaboratories'},

            {'repo': 'edgelaboratories/stacks',
             'action': 'protected_branch.policy_override', 'branch': 'refs/heads/master', 'actor': 'cyrilgdn', 'org': 'edgelaboratories'},
        ],
        {
            'cyrilgdn': {'edgelaboratories/eve': 1, 'edgelaboratories/stacks': 2},
            'vthiery': {'edgelaboratories/pigeon': 1}
        }
    ),
])
def test_get_bypasses(fake_audit_logs, expected_bypassers):
    mock_session = MagicMock(spec=requests.Session)

    mock_session.get().__enter__().json.return_value = fake_audit_logs
    assert get_bypassers(mock_session) == expected_bypassers
