import requests
from datetime import datetime, timedelta, timezone
import config

class GitHubService:
    def __init__(self, token=None):
        self.token = token
        self.url = "https://api.github.com/graphql"
        self.headers = {"Authorization": f"Bearer {token}"} if token else {}

    def get_repo_details(self, repo_name):
        """Fetch repository details using REST (legacy/simple)."""
        # We can keep some REST methods if they are simple, or migrate them too.
        # For now, let's focus on the activity report which is the main limit-eater.
        from github import Github
        client = Github(self.token)
        repo = client.get_repo(repo_name)
        return {
            "name": repo.name,
            "description": repo.description,
            "stars": repo.stargazers_count,
            "language": repo.language,
            "readme": self.get_readme(repo)
        }

    def get_readme(self, repo):
        try:
            readme = repo.get_readme()
            return readme.decoded_content.decode('utf-8')
        except Exception:
            return "No README found."

    def get_user_activity(self, username, days=7):
        """Fetch commits by user across all repos in the last X days using GraphQL."""
        if not self.token:
            raise ValueError("GitHub GraphQL API requires a Personal Access Token (PAT). Please provide one.")

        to_date = datetime.now(timezone.utc)
        from_date = to_date - timedelta(days=days)
        
        query = """
        query($username: String!, $from: GitTimestamp!) {
          user(login: $username) {
            repositories(first: 50, orderBy: {field: PUSHED_AT, direction: DESC}) {
              nodes {
                nameWithOwner
                defaultBranchRef {
                  target {
                    ... on Commit {
                      history(first: 50, since: $from) {
                        nodes {
                          oid
                          message
                          committedDate
                          url
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
        """
        variables = {
            "username": username,
            "from": from_date.isoformat()
        }
        
        response = requests.post(self.url, json={'query': query, 'variables': variables}, headers=self.headers)
        
        if response.status_code != 200:
            raise Exception(f"GraphQL Query failed: {response.status_code} - {response.text}")
            
        data = response.json()
        if "errors" in data:
            raise Exception(f"GraphQL Errors: {data['errors']}")
            
        all_commits = []
        repos = data["data"]["user"]["repositories"]["nodes"]
        
        for repo in repos:
            repo_name = repo["nameWithOwner"]
            if not repo["defaultBranchRef"]:
                continue
                
            history = repo["defaultBranchRef"]["target"]["history"]["nodes"]
            for commit in history:
                all_commits.append({
                    "repo": repo_name,
                    "sha": commit["oid"],
                    "message": commit["message"],
                    "date": datetime.fromisoformat(commit["committedDate"].replace('Z', '+00:00')),
                    "url": commit["url"]
                })
        all_commits.sort(key=lambda x: x['date'], reverse=True)
        return all_commits

    def calculate_stats(self, commits):
        """Calculate average time between pushes."""
        if len(commits) < 2:
            return {"avg_time_between_pushes": "N/A (too few commits)"}
        
        sorted_commits = sorted(commits, key=lambda x: x['date'])
        intervals = []
        for i in range(1, len(sorted_commits)):
            diff = sorted_commits[i]['date'] - sorted_commits[i-1]['date']
            intervals.append(diff.total_seconds())
        
        avg_seconds = sum(intervals) / len(intervals)
        hours = int(avg_seconds // 3600)
        minutes = int((avg_seconds % 3600) // 60)
        
        return {
            "avg_time_between_pushes": f"{hours}h {minutes}m",
            "total_commits": len(commits)
        }
