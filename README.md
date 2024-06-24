# github-repo-watchdog
GitHub Repository WatchDog: Automate branch protection for new repos in your org. This Flask app uses GitHub webhooks to apply custom protection rules instantly, ensuring code quality and security from day one. Streamline your GitHub management with ease.

# GitHub Repository WatchDog

GitHub Repository WatchDog is a Flask-based web application that automatically enables branch protection for newly created public repositories in your GitHub organization. It listens for GitHub webhooks and applies predefined protection rules to ensure code quality and maintain security standards across your organization's repositories.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Endpoint](#api-endpoint)
- [Branch Protection Rules](#branch-protection-rules)
- [Logging](#logging)
- [Contributing](#contributing)
- [License](#license)

## Features

- Listens for GitHub 'repository' event webhooks
- Automatically enables branch protection for newly created public repositories
- Configurable branch protection rules
- Detailed logging for monitoring and debugging

## Prerequisites

- Python 3.11+
- Flask
- Requests library
- A GitHub account with organization admin privileges
- A GitHub Personal Access Token with appropriate permissions

## Installation

1. Clone the repository:

git clone https://github.com/siddjos/github-repo-watchdog
cd github-repo-watchdog

2. Create a virtual environment and activate it:

python -m venv venv
source venv/bin/activate  # On Windows, use venv\Scripts\activate

3. Install the required dependencies:

pip install -r requirements.txt


## Configuration

1. Set up environment variables:
- `GITHUB_TOKEN`: Your GitHub Personal Access Token

You can set these in a `.env` file or export them in your shell:

export GITHUB_TOKEN=your_github_token_here

2. Configure your GitHub organization webhook:
- Go to your organization's settings
- Navigate to Webhooks
- Add a new webhook
- Set the Payload URL to your application's URL (e.g., `https://your-app-url.com/github-webhook`)
- Set the Content type to `application/json`
- Select "Let me select individual events" and choose "Repositories"
- Ensure the webhook is active

## Usage

To run the application locally:

python app.py

The application will start and listen on `http://0.0.0.0:5000`.

For production deployment, it's recommended to use a production WSGI server like Gunicorn:

gunicorn app:app

## API Endpoint

- `/github-webhook` (POST): Handles incoming GitHub webhooks for repository events

## Branch Protection Rules

The application applies the following branch protection rules to new public repositories:

- Require status checks to pass before merging
- Enforce all configured status checks for administrators
- Require pull request reviews before merging
- Dismiss stale pull request approvals when new commits are pushed
- Require review from Code Owners
- Require at least 1 approving review on a pull request
- No restrictions on who can push to the branch

These rules can be customized in the `enable_branch_protection` function.

## Logging

The application uses Python's built-in logging module. Logs are output to the console and include information about:

- New repository creations
- Branch protection enablement status
- Any errors encountered during the process

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.