import os
import requests
import json
import base64
from datetime import datetime
import ssl

class GitHubTool:
    def __init__(self, config):
        self.config = config
        # 从环境变量读取GitHub token
        import os
        token = config['github']['token']
        if token == "${GITHUB_TOKEN}":
            token = os.environ.get('GITHUB_TOKEN')
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": config['github']['user_agent']
        }
        self.base_url = "https://api.github.com"
        # 配置requests会话
        self.session = requests.Session()
        # 禁用SSL验证（仅用于测试环境）
        self.session.verify = False
        # 增加超时设置
        self.session.timeout = 30

    def get_issues(self, repo, labels=None, state="open", sort="updated", direction="desc"):
        """获取仓库的issues"""
        labels_str = ",".join(labels) if labels else None
        params = {
            "state": state,
            "sort": sort,
            "direction": direction
        }
        if labels_str:
            params["labels"] = labels_str

        url = f"{self.base_url}/repos/{repo}/issues"
        response = self.session.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()

    def get_issue_details(self, repo, issue_number):
        """获取issue的详细信息"""
        url = f"{self.base_url}/repos/{repo}/issues/{issue_number}"
        response = self.session.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_file_content(self, repo, file_path, ref="main"):
        """获取文件内容"""
        url = f"{self.base_url}/repos/{repo}/contents/{file_path}?ref={ref}"
        response = self.session.get(url, headers=self.headers)
        if response.status_code == 404:
            return None
        response.raise_for_status()
        content = response.json()
        return base64.b64decode(content['content']).decode('utf-8')

    def get_repo_tree(self, repo, ref="main"):
        """获取仓库的文件树结构"""
        url = f"{self.base_url}/repos/{repo}/git/trees/{ref}?recursive=1"
        response = self.session.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()['tree']

    def create_fork(self, repo):
        """创建仓库的fork"""
        url = f"{self.base_url}/repos/{repo}/forks"
        response = self.session.post(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def create_branch(self, repo, base_branch, new_branch):
        """创建新分支"""
        import time
        # 等待fork完成
        print(f"Waiting for fork {repo} to be ready...")
        for i in range(10):
            try:
                # 获取base分支的sha
                url = f"{self.base_url}/repos/{repo}/git/ref/heads/{base_branch}"
                response = self.session.get(url, headers=self.headers)
                if response.status_code == 200:
                    base_sha = response.json()['object']['sha']
                    break
                print(f"Attempt {i+1}: Base branch {base_branch} not ready yet")
                time.sleep(2)
            except Exception as e:
                print(f"Attempt {i+1}: Error checking base branch: {str(e)}")
                time.sleep(2)
        else:
            raise Exception(f"Base branch {base_branch} not found in repo {repo}")

        # 创建新分支
        url = f"{self.base_url}/repos/{repo}/git/refs"
        data = {
            "ref": f"refs/heads/{new_branch}",
            "sha": base_sha
        }
        response = self.session.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()

    def update_file(self, repo, file_path, content, branch, message, base_branch="main"):
        """更新文件"""
        # 获取现有文件信息（从base分支获取）
        url = f"{self.base_url}/repos/{repo}/contents/{file_path}?ref={base_branch}"
        response = self.session.get(url, headers=self.headers)
        response.raise_for_status()
        file_info = response.json()

        # 更新文件
        url = f"{self.base_url}/repos/{repo}/contents/{file_path}"
        data = {
            "message": message,
            "content": base64.b64encode(content.encode('utf-8')).decode('utf-8'),
            "sha": file_info['sha'],
            "branch": branch
        }
        response = self.session.put(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()

    def create_pull_request(self, repo, title, body, head, base):
        """创建PR"""
        url = f"{self.base_url}/repos/{repo}/pulls"
        data = {
            "title": title,
            "body": body,
            "head": head,
            "base": base
        }
        response = self.session.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()

    def get_contributing_guide(self, repo, file_path):
        """获取贡献指南"""
        return self.get_file_content(repo, file_path)

    def check_if_issue_exists(self, repo, issue_number):
        """检查issue是否存在"""
        url = f"{self.base_url}/repos/{repo}/issues/{issue_number}"
        response = self.session.get(url, headers=self.headers)
        return response.status_code == 200

    def create_repository(self, repo_name, description="", private=False):
        """创建新仓库"""
        url = f"{self.base_url}/user/repos"
        data = {
            "name": repo_name,
            "description": description,
            "private": private
        }
        response = self.session.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()