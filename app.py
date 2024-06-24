import os
import logging
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
GITHUB_API_BASE_URL = "https://api.github.com"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

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

@app.route('/github-webhook', methods=['POST'])
def handle_github_webhook():
    """
    Handle the incoming Github webhook for repository creation events.
    Enable branch protection for newly created public repositories.
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
    default_branch = repo['default_branch']

    logger.info(f"New repo {repo_name} created by {owner}. URL: {repo_url}")

    if is_private:
        logger.info(f"Repository {repo_name} is private. Skipping branch protection.")
        return 'OK', 200

    response = enable_branch_protection(owner, repo_name, default_branch)

    if response.status_code == 200:
        logger.info(f"Branch protection enabled for {owner}/{repo_name}/{default_branch}")
        return jsonify({"message": f"Branch protection enabled for {owner}/{repo_name}/{default_branch}"}), 200
    else:
        logger.error(f"Failed to enable branch protection for {owner}/{repo_name}/{default_branch}")
        return jsonify({
            "error": "Failed to enable branch protection",
            "status_code": response.status_code,
            "response": response.text
        }), response.status_code

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)