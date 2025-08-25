import subprocess
import re
from enum import IntEnum


class Status(IntEnum):
    OK = 0
    ERROR = 1


class GitManager:
    def status(self):
        ans = subprocess.run(["git", "status"], capture_output=True)
        if ans.returncode == Status.OK:
            print(f"Status: {ans.stdout}")
        else:
            print(ans.stderr)

    def help(self):
        ans = subprocess.run(["git", "--help"], capture_output=True)
        if ans.returncode == Status.OK:
            print(ans.stdout)
        else:
            print(ans.stderr)

    def authenticate(self):
        ans = subprocess.run()
        return ans

    def is_allowed_to_push(self) -> bool:
        ans = subprocess.run(["git", "push", "--dry-run"], capture_output=True)
        if ans.returncode == Status.OK:
            print("Push validation successful")
            return True
        else:
            print(f"Push failed: {ans.stderr.decode()}")
            return False

    def push_tag(self, tag: str, remote: str):
        ans = subprocess.run(
            ["git", "push", "--tags", remote, "--dry-run"],
            capture_output=True
        )
        if ans.returncode == Status.OK:
            print("Changes where pushed successfully")
        else:
            print(f"Push failed: {ans.stderr.decode()}")

    def get_tags(self) -> str:
        ans = subprocess.run(
            ["git", "tag", "--list", "'v*'",
                "--sort=-v:refname", "|", "head", "-n", "1"],
            capture_output=True
        )
        if not ans.stdout:
            print("There's no tags in this repository, get_tags")
            return None

        return ans.stdout

    def describe_tags(self) -> str:
        ans = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            capture_output=True
        )
        print(ans.stdout)
        if not ans.stdout:
            print("There's no tags in this repository, describe_tags")
            return None

        return ans.stdout.decode()

    def create_tag(self, tag: str) -> bool:
        ans = subprocess.run(["git", "tag", tag])
        if ans.returncode == Status.OK:
            print(f"tag {tag} created...")
            return True

        return False

    def get_remote(self):
        ans = subprocess.run(
            ["git", "config", "--get", "remote.origin.url"],
            capture_output=True
        )
        if ans.returncode == Status.ERROR:
            print("ERROR 1: directory is not a repository")
            return None
        url = ans.stdout.decode().strip() if isinstance(
            ans.stdout, bytes) else str(ans.stdout).strip()
        return url

    def get_commits(self, reference: str = 'HEAD') -> list:
        """
        Args:
            reference (str): point from where the commits will be taken.

        Returns:
            list (str): %H commit hash, %s commit message, %b commit body, <!end.> end of commit <|!|> will be used later to split the output.
        """
        ans = subprocess.run(
            ["git", "log", reference,
                "--no-decorate", "--pretty=%H|!| %s|!| %b!end."],
            capture_output=True
        )

        if ans.returncode == Status.OK:
            print("Commits retrieved successfully")
            if ans.stdout:
                res = ans.stdout.decode().replace("\n", "").split("!end.")
                res.pop(-1)
            return res
        else:
            print(f"Error retrieving commits: {ans.stderr.decode()}")
            return None

    def delete_tag(self, tag: str):
        """ Delete this function """
        ans = subprocess.run(["git", "tag", "-d", tag])
        if ans.returncode == Status.OK:
            print(f"tag {tag} deleted...")

    def add(self):
        ans = subprocess.run(
            ["git", "add", "./CHANGELOG.md"],
            capture_output=True
        )
        if ans.returncode == Status.OK:
            print("CHANGELOG.md added to git changes to send")

    def commit(self, message: str = "skip: CHANGELOG.md udpated"):
        ans = subprocess.run(
            ["git", "commit", "-m", message],
            capture_output=True
        )
        if ans.returncode == Status.OK:
            print("changes to CHANGELOG.md have been commited")

    def reset():
        ans = subprocess.run(
            ["git", "reset", "--hard", "origin"],
            capture_output=True
        )
        if ans.returncode == Status.OK:
            print("changes to CHANGELOG.md have been commited")

    def validate_version():
        return

    def ref_exists():
        return

    def is_repo():
        """ check if current directory is a repository """
        ans = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            capture_output=True
        )

    def get_head(self):
        ans = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True
        )
        if ans.returncode == Status.OK:
            return ans.stdout.decode().strip()
        return None

    def check_if_branch_up_to_date(self, remote: str, branch: str):
        ans = subprocess.run(
            ["git", "ls-remote", remote, branch],
            capture_output=True
        )
        pattern: str = r"^(?P<ref>\w+)?"
        hash_remote_head: str = re.search(pattern, ans.stdout.decode())
        if self.get_head() == hash_remote_head.group(0):
            return True

        return False

    def is_detached(self):
        return subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True
        ).stdout.decode().strip() == "HEAD"

    def fetch(self, remote: str, branch: str):
        detached: bool = self.is_detached()
        try:
            if detached:
                subprocess.run(
                    [
                        "git",
                        "fetch",
                        "--unshallow",
                        "--tags",
                        "--update-head-ok",
                        remote,
                        f"+refs/heads/{branch}:refs/heads/{branch}"
                    ],
                    capture_output=True
                )
            else:
                subprocess.run(
                    ["git", "fetch", "--unshallow", "--tags", remote],
                    capture_output=True
                )
        except Exception as e:
            if detached:
                subprocess.run(
                    ["git", "fetch", "--tags", "--update-head-ok",
                        remote, f"+refs/heads/{branch}:refs/heads/{branch}"],
                    capture_output=True
                )
            else:
                subprocess.run(
                    ["git", "fetch", "--tags", remote],
                    capture_output=True
                )

    def get_default_branch(self) -> str:
        # pattern looks for any text after HEAD branch:
        pattern: str = r"(?<=HEAD branch: )\w+"
        ans = subprocess.run(
            ["git", "remote", "show", "origin"],
            capture_output=True
        )
        return re.search(pattern, ans.stdout.decode().strip()).group(0)
