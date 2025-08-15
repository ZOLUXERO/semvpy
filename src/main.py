# from git_manager import GitManager
import subprocess
from enum import IntEnum


class Status(IntEnum):
    OK = 0
    ERROR = 1


class GitManager:
    def printGit():
        print("nicee....")

    def status():
        ans = subprocess.run(["git", "status"], capture_output=True)
        if ans.returncode == Status.OK:
            print(ans.stdout)
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

    def get_remote():
        ans = subprocess.run(
            ["git", "config", "--get", "remote.origin.url"],
            capture_output=True
        )
        if ans.returncode == Status.ERROR:
            print("ERROR 1: directory is not a repository")

        return ans

    def format_url(remote: str):
        return


def current_directory():
    subprocess.run(["pwd"])


if __name__ == "__main__":
    current_directory()
    GitManager.printGit()
    GitManager.status()
    # GitManager.gitHelp()
    GitManager.get_remote()
