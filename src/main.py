import subprocess
from git_manager import GitManager
from file_manager import File


def current_directory():
    subprocess.run(["pwd"])


if __name__ == "__main__":
    current_directory()
    remote = GitManager.get_remote()
    print(remote)
    GitManager.validate_push()
    changes = GitManager.get_commits()
    changelog = File("CHANGELOG.md")
    result: str = changelog.format(changes)
    print(result)
    # changelog.write_changelog(result)
