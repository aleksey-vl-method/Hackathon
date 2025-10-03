#!/usr/bin/env python3
"""
Simple JIRA Data Fetcher
Pulls data from JIRA using the REST API v3 and displays it to the user.
"""

import os
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
from typing import List, Dict, Any
import json


def load_config() -> Dict[str, str]:
    """Load configuration from environment variables."""
    load_dotenv()

    config = {
        'jira_url': os.getenv('JIRA_URL'),
        'jira_email': os.getenv('JIRA_EMAIL'),
        'jira_api_token': os.getenv('JIRA_API_TOKEN'),
    }

    # Validate required config
    missing = [key for key, value in config.items() if not value]
    if missing:
        raise ValueError(f"Missing required configuration: {', '.join(missing)}")

    # Ensure URL doesn't have trailing slash
    config['jira_url'] = config['jira_url'].rstrip('/')

    return config


def test_connection(config: Dict[str, str]) -> None:
    """Test connection to JIRA API."""
    url = f"{config['jira_url']}/rest/api/3/myself"
    auth = HTTPBasicAuth(config['jira_email'], config['jira_api_token'])

    try:
        response = requests.get(url, auth=auth, timeout=10)
        response.raise_for_status()
        user_info = response.json()
        print(f"✓ Connected to JIRA: {config['jira_url']}")
        print(f"✓ Authenticated as: {user_info.get('displayName', 'Unknown')}\n")
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Failed to connect to JIRA: {str(e)}")


def fetch_issues(config: Dict[str, str], jql: str = "assignee = currentUser() AND resolution = Unresolved", max_results: int = 50) -> List[Dict[str, Any]]:
    """Fetch issues from JIRA using REST API v3 with JQL query."""
    url = f"{config['jira_url']}/rest/api/3/search"
    auth = HTTPBasicAuth(config['jira_email'], config['jira_api_token'])

    headers = {
        "Accept": "application/json"
    }

    params = {
        "jql": jql,
        "maxResults": max_results,
        "fields": "summary,status,priority,assignee,created,issuetype"
    }

    try:
        response = requests.get(url, auth=auth, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get('issues', [])
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Failed to fetch issues: {str(e)}")


def display_issues(issues: List[Dict[str, Any]], jira_url: str) -> None:
    """Display fetched issues in a readable format."""
    if not issues:
        print("No issues found.")
        return

    print(f"Found {len(issues)} issue(s):\n")
    print("-" * 100)

    for issue in issues:
        key = issue.get('key', 'N/A')
        fields = issue.get('fields', {})

        summary = fields.get('summary', 'N/A')
        status = fields.get('status', {}).get('name', 'N/A')
        priority = fields.get('priority', {})
        priority_name = priority.get('name', 'None') if priority else 'None'
        assignee = fields.get('assignee', {})
        assignee_name = assignee.get('displayName', 'Unassigned') if assignee else 'Unassigned'
        created = fields.get('created', 'N/A')
        issue_type = fields.get('issuetype', {}).get('name', 'N/A')

        print(f"Key:        {key}")
        print(f"Type:       {issue_type}")
        print(f"Summary:    {summary}")
        print(f"Status:     {status}")
        print(f"Priority:   {priority_name}")
        print(f"Assignee:   {assignee_name}")
        print(f"Created:    {created}")
        print(f"Link:       {jira_url}/browse/{key}")
        print("-" * 100)


def main():
    """Main execution function."""
    try:
        # Load configuration
        config = load_config()

        # Test connection to JIRA
        test_connection(config)

        # Fetch issues (customize the JQL query as needed)
        # jql_query = "assignee = currentUser() AND resolution = Unresolved ORDER BY created DESC"
        # jql_query = f"assignee = {config['jira_email']} AND resolution = Unresolved ORDER BY created DESC"
        # jql_query = f"assignee=0 AND resolution = Unresolved ORDER BY created DESC"
        jql_query = "assignee = currentUser()"

        issues = fetch_issues(config, jql_query, max_results=50)

        # Display results
        display_issues(issues, config['jira_url'])

    except ValueError as e:
        print(f"Configuration Error: {e}")
        print("\nPlease ensure you have created a .env file with the required variables.")
        print("See .env.example for reference.")
        return 1
    except ConnectionError as e:
        print(f"Connection Error: {e}")
        return 1
    except RuntimeError as e:
        print(f"Runtime Error: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
