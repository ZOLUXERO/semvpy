import subprocess
import re
from enum import IntEnum


class Status(IntEnum):
    OK = 0
    ERROR = 1


class GitManager:
    def status():
        ans = subprocess.run(["git", "status"], capture_output=True)
        if ans.returncode == Status.OK:
            print(f"Status: {ans.stdout}")
        else:
            print(ans.stderr)

    def help():
        ans = subprocess.run(["git", "--help"], capture_output=True)
        if ans.returncode == Status.OK:
            print(ans.stdout)
        else:
            print(ans.stderr)

    def authenticate():
        ans = subprocess.run()
        return ans

    def validate_push():
        ans = subprocess.run(["git", "push", "--dry-run"], capture_output=True)
        if ans.returncode == Status.OK:
            print("Push validation successful")
        else:
            print(f"Push failed: {ans.stderr.decode()}")

    def get_tags():
        ans = subprocess.run(
            ["git", "tag", "--list", "'v*'", "--sort=-v:refname"],
            capture_output=True
        )
        if not ans.stdout:
            print("There's no tags in this repository")

    def get_remote():
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

    def get_commits():
        # INFO: %H commit hash, %s commit message, %b commit body,
        # !end. end of commit
        # |!| will be used later to split the output
        ans = subprocess.run(
            ["git", "log", "--no-decorate", "--pretty=%H|!| %s|!| %b!end."],
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
