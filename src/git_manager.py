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

    def validate_push(self) -> bool:
        ans = subprocess.run(["git", "push", "--dry-run"], capture_output=True)
        if ans.returncode == Status.OK:
            print("Push validation successful")
            return True
        else:
            print(f"Push failed: {ans.stderr.decode()}")
            return False

    def push(self, tag: str):
        ans = subprocess.run(
            ["git", "push", "origin", f"{tag}", "--dry-run"],
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

    def create_tag(self, tag: str):
        ans = subprocess.run(["git", "tag", f"{tag}"])
        if ans.returncode == Status.OK:
            print(f"tag {tag} created...")

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

    def get_commits(self, reference: str = 'HEAD'):
        """
        Args:
            reference (str): point from where the commits will be taken.

        Returns:
            str: %H commit hash, %s commit message, %b commit body, <!end.> end of commit <|!|> will be used later to split the output.
        """
        ans = subprocess.run(
            ["git", "log", f"{reference}",
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
        ans = subprocess.run(["git", "tag", "-d", f"{tag}"])
        if ans.returncode == Status.OK:
            print(f"tag {tag} deleted...")
