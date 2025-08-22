import subprocess
from git_manager import GitManager
from file_manager import File
from formater import Formater


def current_directory():
    subprocess.run(["pwd"])


if __name__ == "__main__":
    current_directory()
    reference: str = 'HEAD'

    git: GitManager = GitManager()
    remote: str = git.get_remote()
    allowed_to_push: bool = git.validate_push()
    previous_tag: str = git.get_tags()
    if previous_tag:
        reference = f'{previous_tag}..HEAD'
    commits: list = git.get_commits(reference)

    formater: Formater = Formater()
    changes: dict = formater.group_changes_by_type(commits)
    tag: str = formater.update_version(changes, previous_tag)
    formated_changes: str = formater.format_changes(changes, tag)
    changelog: File = File("CHANGELOG.md")
    # changelog.write_changelog(formated_changes)
    branch_up_to_date: bool = git.check_if_brach_up_to_date(remote, "main")

    # TODO: validate if brach is up to date
    # if not fetch all changes from the remote
    # branch.
    if branch_up_to_date:
        print("Local branch is up to date with remote")

    tag_created: bool = git.create_tag(tag)

    print(formated_changes)
    if allowed_to_push and tag_created:
        git.push_tag(tag, remote)

        # TODO: delete, this for testing purposes only
        git.delete_tag(tag)
