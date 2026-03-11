#!/usr/bin/env python3
import yaml
import subprocess
import os
from github_tool import GitHubTool

def main():
    """设置GitHub仓库并推送代码"""
    # 读取配置文件
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # 初始化GitHub工具
    github_tool = GitHubTool(config)
    
    # 获取仓库名称
    repo_name = config['github']['agent_repo'].split('/')[1]
    
    try:
        # 创建GitHub仓库
        print(f"Creating repository: {config['github']['agent_repo']}")
        repo = github_tool.create_repository(
            repo_name=repo_name,
            description="AI Auto Fix Agent - Automatically fixes issues in open source repositories",
            private=False
        )
        print(f"Repository created successfully: {repo['html_url']}")
        
    except Exception as e:
        print(f"Error creating repository: {str(e)}")
        print("Repository might already exist")
    
    # 推送代码到GitHub
    print("Pushing code to GitHub...")
    try:
        # 确保远程仓库已添加
        subprocess.run([
            'git', 'remote', 'add', 'origin', 
            f"https://github.com/{config['github']['agent_repo']}.git"
        ], capture_output=True, text=True)
        
        # 推送代码
        result = subprocess.run(
            ['git', 'push', '-u', 'origin', 'master', '--verbose'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("Code pushed successfully!")
            print(f"Repository URL: https://github.com/{config['github']['agent_repo']}")
        else:
            print(f"Error pushing code: {result.stderr}")
            print(f"Exit code: {result.returncode}")
            
    except Exception as e:
        print(f"Error during push: {str(e)}")

if __name__ == "__main__":
    main()
