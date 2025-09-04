import subprocess
from semvpy import git_manager as git
from semvpy import formater
from semvpy.git_auth import authenticate_url, AuthenticationError
from semvpy.file_manager import File
from semvpy.logger import logger


def current_directory():
    subprocess.run(["pwd"])


if __name__ == "__main__":
    logger.info('Running semvpy')
    current_directory()
    reference: str = 'HEAD'

    remote: str = git.get_remote()
    branch: str = git.get_default_branch()
    try:
        auth_remote = authenticate_url(remote)
    except AuthenticationError as e:
        logger.error(str(e))
        exit(1)

    if git.check_if_branch_up_to_date(auth_remote, branch):
        logger.debug('Local branch is up to date with remote')
    else:
        git.fetch(auth_remote, branch)
        logger.debug('Local branch is NOT up to date with remote')

    last_version: str = git.get_tags()
    if last_version:
        reference = f'{last_version}..HEAD'
    commits: list = git.get_commits(reference)

    changes: dict = formater.group_changes_by_type(commits)
    new_version: str = formater.update_version(changes, last_version)
    formated_changes: str = formater.format_changes(changes, new_version)
    logger.info(formated_changes)

    changelog: File = File("CHANGELOG.md")
    if not changelog.exists():
        changelog.create_file()
    # changelog.write_changelog(formated_changes)

    package_json: File = File("package.json")
    if package_json.exists():
        package_json.update_package_version(new_version)

    tag_was_created: bool = git.create_tag(new_version)
    if git.is_allowed_to_push(auth_remote, branch) and tag_was_created:
        git.push(new_version, auth_remote, branch)

        # TODO: delete, this for testing purposes only
        git.delete_tag(new_version)

    logger.info('Stop semvpy')
