import os
import logging
from flask import Flask, request, jsonify
import requests
import base64

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
GITHUB_API_BASE_URL = "https://api.github.com"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

def create_readme(owner, repo):
    """
    Create a README.md file in the repository if it doesn't exist.
    """
    url = f"{GITHUB_API_BASE_URL}/repos/{owner}/{repo}/contents/README.md"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Check if README.md already exists
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        logger.info(f"README.md already exists in {owner}/{repo}")
        return None
    
    content = "# Welcome to this repository\n\nThis is an automatically generated README.md file."
    data = {
        "message": "Create README.md",
        "content": base64.b64encode(content.encode()).decode('ascii')
    }
    
    response = requests.put(url, headers=headers, json=data)
    return response

def enable_branch_protection(owner, repo, branch):
    """
    Enable branch protection for a given repository.
    """
    url = f"{GITHUB_API_BASE_URL}/repos/{owner}/{repo}/branches/{branch}/protection"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    protection_rules = {
        "required_status_checks": {"strict": True, "contexts": []},
        "enforce_admins": True,
        "required_pull_request_reviews": {
            "dismissal_restrictions": {},
            "dismiss_stale_reviews": True,
            "require_code_owner_reviews": True,
            "required_approving_review_count": 1
        },
        "restrictions": None
    }
    response = requests.put(url, headers=headers, json=protection_rules)
    return response


def notify_via_issue(owner, repo):
    """
    Create an issue in the repository to notify the user about the successful creation.
    """
    url = f"{GITHUB_API_BASE_URL}/repos/{owner}/{repo}/issues"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    issue_data = {
    "title": "Repository automated actions completed successfully",
    "body": f"""
    @{owner} Your repository has been created successfully and automated setup has been completed. Here's a summary of the actions taken:

    1. README.md Creation: A basic README.md file has been added to your repository. (If one was not present already)
    2. Branch Protection: Protection rules have been enabled for your default branch. This ensures that pull requests and code reviews are properly enforced.

    
    These measures help in maintaining code quality and security. Here are some next steps you might want to consider:

    - Review and customize the README.md file to better describe your project.
    - Set up your development environment and start coding!

    If you have any questions or need assistance, please don't hesitate to reach out to the repository administrators.

    Happy coding!
    """
    }
    response = requests.post(url, headers=headers, json=issue_data)
    return response

@app.route('/github-webhook', methods=['POST'])
def handle_github_webhook():
    """
    Handle the incoming Github webhook for repository creation events.
    Create README.md and enable branch protection for newly created public repositories.
    """
    if request.headers.get('X-GitHub-Event') != 'repository':
        return 'OK', 200

    payload = request.json
    if payload['action'] != 'created':
        return 'OK', 200

    repo = payload['repository']
    owner = repo['owner']['login']
    repo_name = repo['name']
    repo_url = repo['url']
    is_private = repo['private']

    logger.info(f"New repo {repo_name} created by {owner}. URL: {repo_url}")

    if is_private:
        logger.info(f"Repository {repo_name} is private. Skipping README creation and branch protection.")
        return 'OK', 200

    # Create README.md
    readme_response = create_readme(owner, repo_name)
    readme_created = False
    if readme_response:
        if readme_response.status_code in [201, 200]:
            logger.info(f"README.md created for {owner}/{repo_name}")
            readme_created = True
        else:
            logger.error(f"Failed to create README.md for {owner}/{repo_name}")

    # Get default branch name
    repo_info_url = f"{GITHUB_API_BASE_URL}/repos/{owner}/{repo_name}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    repo_info_response = requests.get(repo_info_url, headers=headers)
    if repo_info_response.status_code != 200:
        logger.error(f"Failed to get repository info for {owner}/{repo_name}")
        return jsonify({
            "message": f"Processed repository {owner}/{repo_name}",
            "readme_created": readme_created,
            "branch_protection": False
        }), 200

    default_branch = repo_info_response.json()['default_branch']

    # Enable branch protection
    protection_response = enable_branch_protection(owner, repo_name, default_branch)
    if protection_response.status_code == 200:
        logger.info(f"Branch protection enabled for {owner}/{repo_name}/{default_branch}")
    else:
        logger.error(f"Failed to enable branch protection for {owner}/{repo_name}/{default_branch}")

    notify_response = notify_via_issue(owner, repo_name)
    if notify_response.status_code in [201, 200]:
        logger.info(f"Notification issue created for {owner}/{repo_name}")
    
    return jsonify({
        "message": f"Processed repository {owner}/{repo_name}",
        "readme_created": readme_created,
        "branch_protection": protection_response.status_code == 200
    }), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)