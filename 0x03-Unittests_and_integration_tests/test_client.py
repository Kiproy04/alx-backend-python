#!/usr/bin/env python3

"""Unit tests for client.GithubOrgClient"""

import unittest
from unittest.mock import patch, PropertyMock
from parameterized import parameterized

from client import GithubOrgClient


class TestGithubOrgClient(unittest.TestCase):
    """Tests for GithubOrgClient.org property."""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch("client.get_json")
    def test_org(self, org_name, mock_get_json):
        """Test that .org calls get_json with the correct URL and returns result."""
        # Arrange: fake payload
        expected_payload = {"org": org_name}
        mock_get_json.return_value = expected_payload

        # Act: create client and call .org
        client = GithubOrgClient(org_name)
        result = client.org

        # Assert: get_json called once with correct URL
        mock_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{org_name}"
        )
        # And result matches mock payload
        self.assertEqual(result, expected_payload)

    def test_public_repos_url(self):
        """Test that _public_repos_url returns repos_url from org payload."""
        expected_url = "http://example.com/repos"

        with patch.object(
            GithubOrgClient, "org", new_callable=PropertyMock
        ) as mock_org:
            mock_org.return_value = {"repos_url": expected_url}
            client = GithubOrgClient("test-org")
            result = client._public_repos_url

        self.assertEqual(result, expected_url)

    @patch("client.get_json")
    def test_public_repos(self, mock_get_json):
        """Test that public_repos returns the list of repo names."""
        # Fake payload returned by get_json
        fake_repos = [
            {"name": "repo1"},
            {"name": "repo2"},
            {"name": "repo3"},
        ]
        mock_get_json.return_value = fake_repos

        # Expected URL to be mocked
        fake_url = "http://example.com/orgs/test-org/repos"

        with patch.object(GithubOrgClient, "_public_repos_url", new_callable=PropertyMock) as mock_url:
            mock_url.return_value = fake_url
            client = GithubOrgClient("test-org")
            result = client.public_repos()

        # Check returned repo names
        self.assertEqual(result, ["repo1", "repo2", "repo3"])

        # Check mocks were called once
        mock_url.assert_called_once()
        mock_get_json.assert_called_once_with(fake_url)


    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected):
        """Test that has_license returns the correct boolean."""
        self.assertEqual(GithubOrgClient.has_license(repo, license_key), expected)
