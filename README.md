# AI Auto Fix Agent

An AI-powered agent that automatically fixes issues in open source repositories.

## Features

- **Automated Issue Analysis**: Uses AI to understand and analyze GitHub issues
- **Smart Code Fixing**: Generates high-quality code fixes that follow project conventions
- **Multi-Community Support**: Works with pytorch, vllm, sglang, and triton repositories
- **Quality Assurance**: Runs tests and builds to ensure fixes are valid
- **Compliance**: Follows project-specific contributing guidelines
- **PR Generation**: Creates properly formatted pull requests

## Configuration

The agent is configured via a `config.yaml` file:

```yaml
# AI Agent Configuration

# GitHub Configuration
github:
  token: "your-github-token"
  agent_repo: "your-username/auto-fix-agent"
  user_agent: "AutoFixAgent/1.0"

# Target Open Source Communities
target_communities:
  - name: "pytorch"
    repo: "pytorch/pytorch"
    default_branch: "main"
    contributing_guide: ".github/CONTRIBUTING.md"
    test_command: "python -m pytest"
    build_command: "python setup.py build"
    labels: ["bug", "good first issue"]
  # More communities...

# AI Configuration
ai:
  retry_attempts: 3

# Agent Behavior
agent:
  max_prs_per_day: 10
  working_dir: "./workspace"
  pr_title_template: "[{type}] {short_description}"
  commit_message_template: "{type}: {description}\n\nFixes #{issue_number}"
  pr_body_template: "## Issue Fix\n\nFixes #{issue_number}\n\n### Changes Made\n{changes}\n\n### Testing\n{testing}\n\n### Checklist\n- [x] Tests pass\n- [x] Builds successfully\n- [x] Follows contributing guidelines"
```

## Installation

1. Clone the repository:

```bash
git clone https://github.com/robellliu-dev/auto-fix-agent.git
cd auto-fix-agent
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up environment variables:

```bash
export GITHUB_TOKEN="your-github-token"
```

## Usage

Run the agent:

```bash
python main.py --config config.yaml
```

To specify a maximum number of PRs:

```bash
python main.py --config config.yaml --max-prs 5
```

## How It Works

1. **Issue Discovery**: The agent searches for open issues in the target repositories
2. **Issue Analysis**: AI analyzes each issue to understand the problem
3. **File Identification**: Relevant files are identified for modification
4. **Fix Generation**: AI generates code fixes following project conventions
5. **Quality Checks**: Tests and builds are run to verify fixes
6. **PR Creation**: Properly formatted pull requests are created

## Requirements

- Python 3.8+
- GitHub token with repo permissions
- trae CLI

## License

MIT
