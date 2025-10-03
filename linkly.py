# Generate a 1-shot link with the Linkly API

import os
import requests

def create_linkly_oneshot_link(email, api_key, workspace_id, url, name, utm_source):
	api_endpoint = "https://api.linklyhq.com/v1/link/create"  # Replace with actual endpoint if different
	payload = {
		"email": email,
		"api_key": api_key,
		"workspace_id": workspace_id,
		"url": url,
		"name": name,
		"utm_source": utm_source
	}
	headers = {
		"Content-Type": "application/json"
	}
	response = requests.post(api_endpoint, json=payload, headers=headers)
	if response.status_code == 200:
		print("Link created successfully:")
		print(response.json())
		return response.json()
	else:
		print(f"Failed to create link: {response.status_code}")
		print(response.text)
		return None

# Example usage: reads sensitive info from environment variables
if __name__ == "__main__":
	email = os.environ.get("LINKLY_EMAIL")
	api_key = os.environ.get("LINKLY_API_KEY")
	workspace_id = os.environ.get("LINKLY_WORKSPACE_ID")
	if not (email and api_key and workspace_id):
		print("Please set LINKLY_EMAIL, LINKLY_API_KEY, and LINKLY_WORKSPACE_ID environment variables.")
	else:
		# workspace_id should be int
		try:
			workspace_id = int(workspace_id)
		except ValueError:
			print("LINKLY_WORKSPACE_ID must be an integer.")
			exit(1)
		create_linkly_oneshot_link(
			email=email,
			api_key=api_key,
			workspace_id=workspace_id,
			url="https://www.method.me",
			name="My New Tracking Link",
			utm_source="newsletter"
		)
