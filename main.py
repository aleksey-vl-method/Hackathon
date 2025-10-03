from jiralib import get_jira_issues_by_email, print_issue_details, get_active_jira_issues_by_email
import requests
import json
from typing import List, Dict, Any      

"""Example usage of the function."""
# Example: Get issues for a specific email
email = input("Enter the personalized email for jira ticket fetching: (empty for default)")
if email == "":
    email = "a.vanleeuwarden@method.me"
print(f"Fetching JIRA issues for: {email}")

issues = get_active_jira_issues_by_email(email)

if issues:
    print(f"\nFound {len(issues)} issues:")
    
    for issue_data in issues:
        print(issue_data)
else:
    print("No issues found or error occurred.")



