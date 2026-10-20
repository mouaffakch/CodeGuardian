import os
import re
from typing import Dict, Any, List, Optional
from pathlib import Path

try:
    import git
    GIT_AVAILABLE = True
except ImportError:
    GIT_AVAILABLE = False

BUG_MESSAGE_PATTERNS = [
    r'(?i)\bfix(es|ed)?\b',
    r'(?i)\bbug(s)?\b',
    r'(?i)\bhotfix\b',
    r'(?i)\bpatch\b',
    r'(?i)\bdefect(s)?\b',
    r'(?i)\bissue(s)?\s*#?\d+',
    r'(?i)\bresolve(s|d)?\b'
]

class GitAnalyzer:
    """Extracts commit history, churn metrics, and bug-fix correlation from Git repositories."""

    def __init__(self):
        self.is_available = GIT_AVAILABLE

    def get_repo_info(self, repo_path: str) -> Dict[str, Any]:
        """Returns Git repository metadata (branch, HEAD hash, remotes)."""
        if not self.is_available:
            return {"is_git": False, "branch": "unknown", "commit_hash": "HEAD"}

        try:
            repo = git.Repo(repo_path, search_parent_directories=True)
            active_branch = "HEAD"
            try:
                active_branch = repo.active_branch.name
            except Exception:
                pass

            commit_hash = repo.head.commit.hexsha[:8] if repo.head.is_valid() else "HEAD"
            remote_url = ""
            if repo.remotes:
                remote_url = repo.remotes[0].url

            return {
                "is_git": True,
                "branch": active_branch,
                "commit_hash": commit_hash,
                "remote_url": remote_url,
                "repo_root": repo.working_dir
            }
        except Exception:
            return {"is_git": False, "branch": "unknown", "commit_hash": "HEAD", "remote_url": None}

    def analyze_file_churn(self, repo_path: str, max_commits: int = 200) -> Dict[str, Dict[str, Any]]:
        """
        Analyzes Git history to compute per-file churn, commit counts, bug-fix commits, and author counts.
        """
        churn_data: Dict[str, Dict[str, Any]] = {}
        if not self.is_available:
            return churn_data

        try:
            repo = git.Repo(repo_path, search_parent_directories=True)
            repo_root = Path(repo.working_dir).resolve()

            if not repo.head.is_valid():
                return churn_data

            commits = list(repo.iter_commits(max_count=max_commits))
            
            for commit in commits:
                msg = commit.message
                is_bug_fix = any(re.search(pat, msg) for pat in BUG_MESSAGE_PATTERNS)
                author = commit.author.name or commit.author.email

                # Check stats for this commit
                try:
                    stats = commit.stats.files
                    for raw_file_path, file_stat in stats.items():
                        norm_path = raw_file_path.replace("\\", "/")
                        if norm_path not in churn_data:
                            churn_data[norm_path] = {
                                "commit_count": 0,
                                "churn_lines": 0,
                                "bug_fix_count": 0,
                                "authors": set(),
                                "recent_commits": []
                            }

                        entry = churn_data[norm_path]
                        entry["commit_count"] += 1
                        entry["churn_lines"] += (file_stat.get("insertions", 0) + file_stat.get("deletions", 0))
                        if is_bug_fix:
                            entry["bug_fix_count"] += 1
                        if author:
                            entry["authors"].add(author)

                        if len(entry["recent_commits"]) < 5:
                            entry["recent_commits"].append({
                                "hash": commit.hexsha[:8],
                                "message": commit.message.strip().split("\n")[0],
                                "author": author,
                                "date": commit.committed_datetime.isoformat(),
                                "is_bug_fix": is_bug_fix
                            })
                except Exception:
                    continue

            # Convert sets to counts for JSON serialization
            for path, data in churn_data.items():
                data["author_count"] = len(data["authors"])
                del data["authors"]

        except Exception as e:
            # Fallback gracefully
            pass

        return churn_data

git_analyzer = GitAnalyzer()
