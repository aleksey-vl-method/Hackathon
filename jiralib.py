from dotenv import load_dotenv
import os
from jira import JIRA

load_dotenv()
api_key = os.getenv("JIRA_API_TOKEN")
print(f"API Key: {api_key}")

jira = JIRA(server = 'https://method.atlassian.net/', basic_auth=('c.zhao@method.me', api_key))

server_info = jira.server_info()
print(f"Connected to JIRA: {server_info}")

myself = jira.myself()

# First, let's get all available fields to understand the custom field mapping
print("\n--- AVAILABLE JIRA FIELDS ---")
fields = jira.fields()
custom_fields = [f for f in fields if f['custom']]
print(f"Found {len(custom_fields)} custom fields:")
for field in custom_fields[:10]:  # Show first 10 custom fields
    print(f"- {field['id']}: {field['name']}")

my_issues = jira.search_issues('assignee = "d.mau@method.me"')
print(f"\nFound {len(my_issues)} issues assigned to me:")


my_issues = [jira.issue('PL-57560')]
for issue in my_issues:
    print(f"\n{'='*50}")
    print(f"TICKET: {issue.key}")
    print(f"{'='*50}")
    
    # Basic details
    print(f"Summary: {issue.fields.summary}")
    print(f"Status: {issue.fields.status.name}")
    print(f"Priority: {issue.fields.priority.name if issue.fields.priority else 'None'}")
    print(f"Issue Type: {issue.fields.issuetype.name}")
    
    # People
    print(f"Reporter: {issue.fields.reporter.displayName if issue.fields.reporter else 'None'}")
    print(f"Assignee: {issue.fields.assignee.displayName if issue.fields.assignee else 'Unassigned'}")
    
    # Dates
    print(f"Created: {issue.fields.created}")
    print(f"Updated: {issue.fields.updated}")
    if issue.fields.duedate:
        print(f"Due Date: {issue.fields.duedate}")
    
    # Project info
    print(f"Project: {issue.fields.project.name} ({issue.fields.project.key})")
    
    # Description (first 200 characters)
    if issue.fields.description:
        desc = issue.fields.description[:200] + "..." if len(issue.fields.description) > 200 else issue.fields.description
        print(f"Description: {desc}")
    
    # Comments count
    if hasattr(issue.fields, 'comment') and issue.fields.comment:
        print(f"Comments: {issue.fields.comment.total}")
    
    # Labels
    if issue.fields.labels:
        print(f"Labels: {', '.join(issue.fields.labels)}")
    
    # Components
    if issue.fields.components:
        components = [comp.name for comp in issue.fields.components]
        print(f"Components: {', '.join(components)}")
    
    # Resolution details
    if issue.fields.resolution:
        print(f"Resolution: {issue.fields.resolution.name}")
        print(f"Resolution Description: {issue.fields.resolution.description}")
    
    # Custom fields - let's find acceptance criteria and other custom fields
    print(f"\n--- CUSTOM FIELDS ---")
    
    # Common custom field names for acceptance criteria
    custom_fields_to_check = [
        'customfield_10000', 'customfield_10001', 'customfield_10002', 'customfield_10003',
        'customfield_10004', 'customfield_10005', 'customfield_10006', 'customfield_10007',
        'customfield_10008', 'customfield_10009', 'customfield_10010', 'customfield_10011'
    ]
    
    # Check all fields to find acceptance criteria
    all_fields = dir(issue.fields)
    for field_name in all_fields:
        if field_name.startswith('customfield_'):
            field_value = getattr(issue.fields, field_name, None)
            if field_value:
                print(f"{field_name}: {field_value}")
    
    # Also check for common field names
    common_fields = ['acceptancecriteria', 'acceptance_criteria', 'analysisresult', 'analysis_result']
    for field in common_fields:
        if hasattr(issue.fields, field):
            value = getattr(issue.fields, field)
            if value:
                print(f"{field}: {value}")
    
    # Show ALL available fields (uncomment to debug)
    print(f"\n--- ALL AVAILABLE FIELDS ---")
    print([field for field in dir(issue.fields) if not field.startswith('_')])