#!/usr/bin/env python3
"""
Test script to fetch active JIRA tickets.
"""

from jiralib import get_active_jira_issues_by_email, get_active_jira_issues_by_status, print_issue_details


def main():
    """Test active JIRA issues functionality."""
    
    # Get email input
    email = input("Enter email for active ticket fetching (or press Enter for c.zhao@method.me): ")
    if email == "":
        email = "c.zhao@method.me"
    
    print(f"\n{'='*60}")
    print(f"FETCHING ACTIVE JIRA TICKETS FOR: {email}")
    print(f"{'='*60}")
    
    # Method 1: Get active issues (resolution = Unresolved)
    print("\n--- METHOD 1: Active Issues (Unresolved) ---")
    active_issues = get_active_jira_issues_by_email(email, max_results=10)
    
    if active_issues:
        print(f"Found {len(active_issues)} active issue(s):")
        
        # Print summary
        for i, issue in enumerate(active_issues, 1):
            print(f"\n{i}. [{issue['key']}] {issue['summary']}")
            print(f"   Status: {issue['status']} | Priority: {issue['priority']}")
            print(f"   Project: {issue['project_name']} | Type: {issue['issue_type']}")
        
        # Print detailed view of first issue
        if active_issues:
            print(f"\n{'='*50}")
            print("DETAILED VIEW OF FIRST ACTIVE ISSUE:")
            print_issue_details(active_issues[0])
    else:
        print("No active issues found.")
    
    # Method 2: Get issues by specific active statuses
    print(f"\n\n--- METHOD 2: Issues by Active Status ---")
    active_statuses = ['To Do', 'In Progress', 'In Review', 'Code Review', 'Testing']
    status_issues = get_active_jira_issues_by_status(email, active_statuses, max_results=10)
    
    if status_issues:
        print(f"Found {len(status_issues)} issue(s) in active statuses {active_statuses}:")
        
        # Group by status
        status_groups = {}
        for issue in status_issues:
            status = issue['status']
            if status not in status_groups:
                status_groups[status] = []
            status_groups[status].append(issue)
        
        for status, issues in status_groups.items():
            print(f"\n--- {status.upper()} ({len(issues)} issues) ---")
            for issue in issues:
                print(f"  • [{issue['key']}] {issue['summary']}")
    else:
        print(f"No issues found in active statuses: {active_statuses}")


if __name__ == "__main__":
    main()
