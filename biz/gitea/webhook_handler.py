import os
from typing import List, Dict, Any

import requests
from biz.utils.log import logger

class PullRequestHandler:
    def __init__(self, webhook_data: dict, gitea_token: str, gitea_url: str):
        self.webhook_data = webhook_data
        self.gitea_token = gitea_token
        self.gitea_url = gitea_url.rstrip('/')
        self.action = webhook_data.get('action', '')
        self.repository = webhook_data.get('repository', {})
        self.pull_request = webhook_data.get('pull_request', {})

    def get_pull_request_changes(self) -> List[Dict[str, Any]]:
        """获取 Pull Request 的变更"""
        try:
            owner = self.repository.get('owner', {}).get('username')
            repo = self.repository.get('name')
            number = self.pull_request.get('number')
            
            if not all([owner, repo, number]):
                logger.error('Missing required fields for getting PR changes')
                return []

            url = f"{self.gitea_url}/api/v1/repos/{owner}/{repo}/pulls/{number}/files"
            headers = {
                'Authorization': f'token {self.gitea_token}',
                'Accept': 'application/json'
            }
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            logger.error(f'Failed to get PR changes: {str(e)}')
            return []

    def get_pull_request_commits(self) -> List[Dict[str, Any]]:
        """获取 Pull Request 的提交记录"""
        try:
            owner = self.repository.get('owner', {}).get('username')
            repo = self.repository.get('name')
            number = self.pull_request.get('number')
            
            if not all([owner, repo, number]):
                logger.error('Missing required fields for getting PR commits')
                return []

            url = f"{self.gitea_url}/api/v1/repos/{owner}/{repo}/pulls/{number}/commits"
            headers = {
                'Authorization': f'token {self.gitea_token}',
                'Accept': 'application/json'
            }
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            logger.error(f'Failed to get PR commits: {str(e)}')
            return []

    def add_pull_request_notes(self, body: str) -> bool:
        """添加 Pull Request 评论"""
        try:
            owner = self.repository.get('owner', {}).get('username')
            repo = self.repository.get('name')
            number = self.pull_request.get('number')
            
            if not all([owner, repo, number]):
                logger.error('Missing required fields for adding PR comment')
                return False

            url = f"{self.gitea_url}/api/v1/repos/{owner}/{repo}/issues/{number}/comments"
            headers = {
                'Authorization': f'token {self.gitea_token}',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            data = {'body': body}
            
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            return True
        except Exception as e:
            logger.error(f'Failed to add PR comment: {str(e)}')
            return False

class PushHandler:
    def __init__(self, webhook_data: dict, gitea_token: str, gitea_url: str):
        self.webhook_data = webhook_data
        self.gitea_token = gitea_token
        self.gitea_url = gitea_url.rstrip('/')
        self.repository = webhook_data.get('repository', {})
        self.commits = webhook_data.get('commits', [])

    def get_push_commits(self) -> List[Dict[str, Any]]:
        """获取 Push 事件的提交记录"""
        return self.commits

    def get_push_changes(self) -> List[Dict[str, Any]]:
        """获取 Push 事件的变更"""
        changes = []
        for commit in self.commits:
            for file in commit.get('modified', []):
                changes.append({
                    'old_path': file,
                    'new_path': file,
                    'status': 'modified'
                })
            for file in commit.get('added', []):
                changes.append({
                    'old_path': file,
                    'new_path': file,
                    'status': 'added'
                })
            for file in commit.get('removed', []):
                changes.append({
                    'old_path': file,
                    'new_path': file,
                    'status': 'deleted'
                })
        return changes

    def add_push_notes(self, body: str) -> bool:
        """添加 Push 事件的评论"""
        try:
            owner = self.repository.get('owner', {}).get('username')
            repo = self.repository.get('name')
            ref = self.webhook_data.get('ref', '').replace('refs/heads/', '')
            
            if not all([owner, repo, ref]):
                logger.error('Missing required fields for adding push comment')
                return False

            # 获取最新的提交
            latest_commit = self.commits[0] if self.commits else None
            if not latest_commit:
                logger.error('No commits found in push event')
                return False

            url = f"{self.gitea_url}/api/v1/repos/{owner}/{repo}/commits/{latest_commit['id']}/comments"
            headers = {
                'Authorization': f'token {self.gitea_token}',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            data = {'body': body}
            
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            return True
        except Exception as e:
            logger.error(f'Failed to add push comment: {str(e)}')
            return False

def filter_changes(changes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """过滤变更文件"""
    supported_extensions = os.environ.get('SUPPORTED_EXTENSIONS', '').split(',')
    if not supported_extensions:
        return changes

    return [
        change for change in changes
        if any(change['new_path'].endswith(ext) for ext in supported_extensions)
    ] 