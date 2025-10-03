from dotenv import load_dotenv
import os
from jira import JIRA
from typing import List, Dict, Any, Optional


def get_jira_connection() -> JIRA:
    """Establish connection to JIRA using environment variables."""
    load_dotenv()
    api_key = os.getenv("JIRA_API_TOKEN")
    jira_email = os.getenv("JIRA_EMAIL")
    
    if not api_key or not jira_email:
        raise ValueError("JIRA_API_TOKEN and JIRA_EMAIL must be set in environment variables")
    
    jira = JIRA(server='https://method.atlassian.net/', basic_auth=(jira_email, api_key))
    return jira


def get_jira_issues_by_email(assignee_email: str, max_results: int = 50) -> List[Dict[str, Any]]:
    """
    Get JIRA issues assigned to a specific email address.
    
    Args:
        assignee_email: Email address of the assignee
        max_results: Maximum number of issues to return (default: 50)
    
    Returns:
        List of dictionaries containing issue details
    """
    try:
        jira = get_jira_connection()
        
        # Search for issues assigned to the specified email
        jql_query = f'assignee = "{assignee_email}"'
        issues = jira.search_issues(jql_query, maxResults=max_results)
        
        issue_list = []
        
        for issue in issues:
            issue_data = extract_issue_details(issue)
            issue_list.append(issue_data)
        
        return issue_list
        
    except Exception as e:
        print(f"Error fetching issues: {str(e)}")
        return []


def extract_issue_details(issue) -> Dict[str, Any]:
    """Extract detailed information from a JIRA issue object."""
    issue_data = {
        'key': issue.key,
        'summary': issue.fields.summary,
        'status': issue.fields.status.name,
        'priority': issue.fields.priority.name if issue.fields.priority else 'None',
        'issue_type': issue.fields.issuetype.name,
        'reporter': issue.fields.reporter.displayName if issue.fields.reporter else 'None',
        'assignee': issue.fields.assignee.displayName if issue.fields.assignee else 'Unassigned',
        'created': issue.fields.created,
        'updated': issue.fields.updated,
        'due_date': issue.fields.duedate if issue.fields.duedate else None,
        'project_name': issue.fields.project.name,
        'project_key': issue.fields.project.key,
        'description': issue.fields.description[:200] + "..." if issue.fields.description and len(issue.fields.description) > 200 else issue.fields.description,
        'comments_count': issue.fields.comment.total if hasattr(issue.fields, 'comment') and issue.fields.comment else 0,
        'labels': issue.fields.labels if issue.fields.labels else [],
        'components': [comp.name for comp in issue.fields.components] if issue.fields.components else [],
        'resolution': issue.fields.resolution.name if issue.fields.resolution else None,
        'resolution_description': issue.fields.resolution.description if issue.fields.resolution else None,
        'custom_fields': {}
    }
    
    # Extract custom fields
    all_fields = dir(issue.fields)
    for field_name in all_fields:
        if field_name.startswith('customfield_'):
            field_value = getattr(issue.fields, field_name, None)
            if field_value:
                issue_data['custom_fields'][field_name] = field_value
    
    return issue_data


def print_issue_details(issue_data: Dict[str, Any]) -> None:
    """Print issue details in a formatted way."""
    print(f"\n{'='*50}")
    print(f"TICKET: {issue_data['key']}")
    print(f"{'='*50}")
    
    # Basic details
    print(f"Summary: {issue_data['summary']}")
    print(f"Status: {issue_data['status']}")
    print(f"Priority: {issue_data['priority']}")
    print(f"Issue Type: {issue_data['issue_type']}")
    
    # People
    print(f"Reporter: {issue_data['reporter']}")
    print(f"Assignee: {issue_data['assignee']}")
    
    # Dates
    print(f"Created: {issue_data['created']}")
    print(f"Updated: {issue_data['updated']}")
    if issue_data['due_date']:
        print(f"Due Date: {issue_data['due_date']}")
    
    # Project info
    print(f"Project: {issue_data['project_name']} ({issue_data['project_key']})")
    
    # Description
    if issue_data['description']:
        print(f"Description: {issue_data['description']}")
    
    # Comments count
    if issue_data['comments_count'] > 0:
        print(f"Comments: {issue_data['comments_count']}")
    
    # Labels
    if issue_data['labels']:
        print(f"Labels: {', '.join(issue_data['labels'])}")
    
    # Components
    if issue_data['components']:
        print(f"Components: {', '.join(issue_data['components'])}")
    
    # Resolution details
    if issue_data['resolution']:
        print(f"Resolution: {issue_data['resolution']}")
        if issue_data['resolution_description']:
            print(f"Resolution Description: {issue_data['resolution_description']}")
    
    # Custom fields
    if issue_data['custom_fields']:
        print(f"\n--- CUSTOM FIELDS ---")
        for field_name, field_value in issue_data['custom_fields'].items():
            print(f"{field_name}: {field_value}")


def get_active_jira_issues_by_email(assignee_email: str, max_results: int = 50) -> List[Dict[str, Any]]:
    """
    Get only active JIRA issues assigned to a specific email address.
    Active issues are those that are not resolved (resolution = Unresolved).
    
    Args:
        assignee_email: Email address of the assignee
        max_results: Maximum number of issues to return (default: 50)
    
    Returns:
        List of dictionaries containing active issue details
    """
    try:
        jira = get_jira_connection()
        
        # Search for active issues assigned to the specified email
        # resolution = Unresolved filters out completed/resolved tickets
        jql_query = f'assignee = "{assignee_email}" AND resolution = Unresolved'
        issues = jira.search_issues(jql_query, maxResults=max_results)
        
        issue_list = []
        
        for issue in issues:
            issue_data = extract_issue_details(issue)
            issue_list.append(issue_data)
        
        return issue_list
        
    except Exception as e:
        print(f"Error fetching active issues: {str(e)}")
        return []


def get_active_jira_issues_by_status(assignee_email: str, active_statuses: List[str] = None, max_results: int = 50) -> List[Dict[str, Any]]:
    """
    Get JIRA issues by specific active statuses for an assignee.
    
    Args:
        assignee_email: Email address of the assignee
        active_statuses: List of status names to filter by (e.g., ['To Do', 'In Progress', 'In Review'])
        max_results: Maximum number of issues to return (default: 50)
    
    Returns:
        List of dictionaries containing issue details
    """
    if active_statuses is None:
        # Default active statuses - customize based on your JIRA workflow
        active_statuses = ['To Do', 'In Progress', 'In Review', 'Code Review', 'Testing', 'Blocked']
    
    try:
        jira = get_jira_connection()
        
        # Build JQL query with multiple statuses
        status_query = ' OR '.join([f'status = "{status}"' for status in active_statuses])
        jql_query = f'assignee = "{assignee_email}" AND ({status_query})'
        
        issues = jira.search_issues(jql_query, maxResults=max_results)
        
        issue_list = []
        
        for issue in issues:
            issue_data = extract_issue_details(issue)
            issue_list.append(issue_data)
        
        return issue_list
        
    except Exception as e:
        print(f"Error fetching issues by status: {str(e)}")
        return []


