from github import count_dependabot_prs
import requests
from unittest.mock import MagicMock


def test_count_dependabot_prs():
    mock_session = MagicMock(spec=requests.Session)

    mock_session.get().__enter__().json.return_value = []
    assert count_dependabot_prs(mock_session, "fake_repo") == 0

    mock_session.get().__enter__().json.return_value = [
        {'number': 448,
         'state': 'open',
         'title': 'maven(deps): bump swagger-request-validator-core from 2.15.1 to 2.25.0 in /copernic',
         'user': {'login': 'dependabot[bot]'}},
        {'number': 439,
            'state': 'open',
            'title': 'Reword dependabot commit message prefix',
            'user': {'login': 'A-Ibm'}},
        {'number': 198,
            'state': 'open',
            'title': 'Bump spring-boot-starter-parent from 2.1.5.RELEASE to 2.2.5.RELEASE',
            'login': {'login': 'dependabot-preview[bot]'}}
    ]

    assert count_dependabot_prs(mock_session, "fake_repo") == 1
