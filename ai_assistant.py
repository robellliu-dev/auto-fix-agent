import os
from openai import OpenAI
import json
import re
import httpx
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AIAssistant:
    def __init__(self, config):
        self.config = config
        try:
            self.client = OpenAI(
                api_key=os.getenv("OPENAI_API_KEY"),
                timeout=httpx.Timeout(60.0, connect=20.0),
                http_client=httpx.Client(
                    timeout=httpx.Timeout(60.0, connect=20.0),
                    follow_redirects=True,
                    verify=False  # 禁用SSL验证（仅用于测试环境）
                )
            )
            logger.info("OpenAI client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {str(e)}")
            raise
        self.model = config['ai']['model']
        self.temperature = config['ai']['temperature']
        self.max_tokens = config['ai']['max_tokens']

    def analyze_issue(self, issue_title, issue_body, repo_context=""):
        """分析issue，确定问题类型和修复方向"""
        prompt = f"""
        You are an experienced software developer. Analyze the following GitHub issue and provide:
        1. A clear understanding of the problem
        2. The type of issue (bug, feature request, etc.)
        3. Potential files that might need to be modified
        4. A plan for fixing the issue

        Issue Title: {issue_title}
        Issue Body: {issue_body}
        
        {repo_context}
        """

        retry_attempts = self.config.get('ai', {}).get('retry_attempts', 3)
        for attempt in range(retry_attempts):
            try:
                print(f"Calling OpenAI API (attempt {attempt+1}/{retry_attempts}) with model: {self.model}")
                print(f"Prompt length: {len(prompt)} characters")
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )
                
                print(f"API response received successfully")
                
                return response.choices[0].message.content.strip()
            except Exception as e:
                print(f"Error in analyze_issue (attempt {attempt+1}/{retry_attempts}): {str(e)}")
                if attempt < retry_attempts - 1:
                    print("Retrying...")
                    import time
                    time.sleep(2 ** attempt)  # 指数退避
                else:
                    print("All retry attempts failed")
                    import traceback
                    traceback.print_exc()
                    raise

    def generate_fix(self, issue_analysis, file_path, file_content, contributing_guide=""):
        """生成代码修复方案"""
        prompt = f"""
        You are an expert software developer. Based on the issue analysis below, fix the problem in the provided code.
        
        Issue Analysis:
        {issue_analysis}
        
        File Path: {file_path}
        File Content:
        ```
        {file_content}
        ```
        
        {f"Contributing Guidelines: {contributing_guide}" if contributing_guide else ""}
        
        Please provide only the fixed code, without any additional explanations. Make sure the fix:
        1. Addresses the root cause of the issue
        2. Follows the project's coding style
        3. Maintains backward compatibility
        4. Does not introduce new bugs
        5. Is minimal and focused on the specific issue
        """

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )

        # 提取代码部分
        content = response.choices[0].message.content.strip()
        code_match = re.search(r'```(?:[a-z]+\n)?(.*?)```', content, re.DOTALL)
        if code_match:
            return code_match.group(1).strip()
        return content

    def generate_test(self, file_path, file_content, fix_content, issue_description):
        """生成测试用例"""
        prompt = f"""
        You are an expert software developer. Generate a test case for the fixed code below to verify the issue is resolved.
        
        Original File Path: {file_path}
        Original Code:
        ```
        {file_content}
        ```
        
        Fixed Code:
        ```
        {fix_content}
        ```
        
        Issue Description:
        {issue_description}
        
        Please provide only the test code, following the project's testing conventions.
        """

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )

        content = response.choices[0].message.content.strip()
        code_match = re.search(r'```(?:[a-z]+\n)?(.*?)```', content, re.DOTALL)
        if code_match:
            return code_match.group(1).strip()
        return content

    def review_fix(self, issue_analysis, file_path, original_content, fixed_content, contributing_guide=""):
        """审查修复方案"""
        prompt = f"""
        You are a senior software engineer reviewing a code fix. Evaluate the fix against the issue analysis and contributing guidelines.
        
        Issue Analysis:
        {issue_analysis}
        
        File Path: {file_path}
        Original Code:
        ```
        {original_content}
        ```
        
        Fixed Code:
        ```
        {fixed_content}
        ```
        
        {f"Contributing Guidelines: {contributing_guide}" if contributing_guide else ""}
        
        Please provide a detailed review including:
        1. Whether the fix addresses the root cause
        2. Code quality assessment
        3. Compliance with contributing guidelines
        4. Potential issues or improvements
        5. Overall recommendation (approve/reject with reason)
        """

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )

        return response.choices[0].message.content.strip()

    def generate_commit_message(self, issue_analysis, fix_description, issue_number, config):
        """生成符合规范的提交信息"""
        prompt = f"""
        Generate a concise and descriptive commit message for the following fix:
        
        Issue Analysis: {issue_analysis}
        Fix Description: {fix_description}
        Issue Number: #{issue_number}
        
        Follow this template: {config['agent']['commit_message_template']}
        Keep it professional and follow the project's commit message conventions.
        """

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
            max_tokens=100
        )

        return response.choices[0].message.content.strip()

    def generate_pr_title(self, issue_analysis, fix_description, config):
        """生成符合规范的PR标题"""
        prompt = f"""
        Generate a concise PR title for the following fix:
        
        Issue Analysis: {issue_analysis}
        Fix Description: {fix_description}
        
        Follow this template: {config['agent']['pr_title_template']}
        Keep it under 72 characters and follow the project's PR title conventions.
        """

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
            max_tokens=100
        )

        return response.choices[0].message.content.strip()

    def generate_pr_body(self, issue_number, changes, testing, config):
        """生成PR正文"""
        return config['agent']['pr_body_template'].format(
            issue_number=issue_number,
            changes=changes,
            testing=testing
        )