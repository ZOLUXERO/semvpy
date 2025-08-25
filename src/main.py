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
    branch: str = git.get_default_branch()
    if git.check_if_branch_up_to_date(remote, branch):
        print("Local branch is up to date with remote")
    else:
        git.fetch(remote, branch)
        print("Local branch is NOT up to date with remote")

    last_version: str = git.get_tags()
    if last_version:
        reference = f'{last_version}..HEAD'
    commits: list = git.get_commits(reference)

    formater: Formater = Formater()
    changes: dict = formater.group_changes_by_type(commits)
    new_version: str = formater.update_version(changes, last_version)
    formated_changes: str = formater.format_changes(changes, new_version)

    changelog: File = File("CHANGELOG.md")
    # changelog.write_changelog(formated_changes)

    print(formated_changes)
    if git.is_allowed_to_push() and git.create_tag(new_version):
        git.push_tag(new_version, remote)

        # TODO: delete, this for testing purposes only
        git.delete_tag(new_version)
