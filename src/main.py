import subprocess
from git_manager import GitManager
from file_manager import File


def current_directory():
    subprocess.run(["pwd"])


if __name__ == "__main__":
    current_directory()
    reference: str = 'HEAD'
    git = GitManager()
    remote = git.get_remote()
    print(remote)
    allowed_to_push: bool = git.validate_push()
    previous_tag: str = git.get_tags()
    if previous_tag:
        reference = f'{previous_tag}..HEAD'
    commits = git.get_commits(reference)

    changelog: File = File("CHANGELOG.md")
    changes: dict = changelog.group_changes_by_type(commits)
    tag: str = changelog.update_version(changes, previous_tag)
    git.create_tag(tag)
    formated_changes: str = changelog.format_changes(changes, tag)
    # changelog.write_changelog(result)
    print(formated_changes)
    if allowed_to_push:
        git.push(tag)

        # TODO: delete, this for testing purposes only
        git.delete_tag(tag)
