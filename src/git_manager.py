import subprocess
import re
from enum import IntEnum
from logger import logger


class Status(IntEnum):
    OK = 0
    ERROR = 1


def _run_git_command(args, check=False, decode_output=True):
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True,
            check=check
        )
        stdout = (result.stdout.decode()
                  if decode_output and result.stdout else result.stdout)
        stderr = (result.stderr.decode()
                  if decode_output and result.stderr else result.stderr)
        return result.returncode, stdout, stderr
    except subprocess.CalledProcessError as e:
        logger.warning(f"Git command failed: {
            e.stderr.decode() if e.stderr else str(e)}")
        return 1, None, e.stderr
    except Exception as e:
        logger.error(f"Unexpected error running git command: {e}")
        return 1, None, str(e)


def status():
    code, out, err = _run_git_command(["status"])
    if code == Status.OK:
        logger.info(f"Status: {out}")
    else:
        logger.info(err)


def help():
    code, out, err = _run_git_command(["--help"])
    if code == Status.OK:
        logger.info(f"Status: {out}")
    else:
        logger.info(err)


def is_allowed_to_push(remote: str, branch: str) -> bool:
    code, out, err = _run_git_command(
        ["push", "--dry-run", remote, f"HEAD:{branch}"]
    )
    if code == Status.OK:
        logger.info(f"Push validation successful: {out}")
        return True
    else:
        logger.info(err)
    return False


def push(tag: str, remote: str, branch):
    code, out, err = _run_git_command(
        ["push", "--tags", remote, f"HEAD:{branch}", "--dry-run"], check=True
    )
    if code == Status.OK:
        logger.info("Changes were pushed successfully")
    else:
        logger.info(f"Push failed: {err}")


def get_tags() -> str:
    code, out, err = _run_git_command(
        ["tag", "--list", "'v*'", "--sort=-v:refname", "|", "head", "-n", "1"],
        decode_output=False
    )
    if not out:
        logger.info("There's no tags in this repository, get_tags")
        return None

    return out


def describe_tags() -> str:
    code, out, err = _run_git_command(
        ["describe", "--tags", "--abbrev=0"],
    )
    if not out:
        logger.info("There's no tags in this repository, describe_tags")
        return None

    return out.decode()


def create_tag(tag: str) -> bool:
    code, out, err = _run_git_command(["tag", tag])
    if code == Status.OK:
        logger.info(f"tag {tag} created...")
        return True
    else:
        logger.info(f"Push failed: {err}")

    return False


def get_remote():
    try:
        ans = subprocess.run(
            ["git", "config", "--get", "remote.origin.url"],
            capture_output=True,
            check=True
        )
        url = ans.stdout.decode().strip() if isinstance(
            ans.stdout, bytes) else str(ans.stdout).strip()
        return url
    except subprocess.CalledProcessError as e:
        logger.info(f"ERROR: directory is not a repository. Details: {e}")
        return None
    except Exception as e:
        logger.info(f"Unexpected error in get_remote: {e}")
        return None


def get_commits(reference: str = 'HEAD') -> list:
    """
    Args:
        reference (str): point from where the commits will be taken.

    Returns:
        list (str): %H commit hash, %s commit message, %b commit body, <!end.> end of commit <|!|> will be used later to split the output.
    """
    code, out, err = _run_git_command(
        ["log", reference, "--no-decorate", "--pretty=%H|!| %s|!| %b!end."],
        decode_output=False
    )
    if code == Status.OK:
        logger.info(f"Status: {out}, Commits retrieved successfully")
        if out:
            commits = out.decode().replace("\n", "").split("!end.")

            # remove las item of list, it's allways
            # empty because of the slplit !end.
            commits.pop(-1)
        return commits
    else:
        logger.info(f"Error retrieving commits: {err.decode()}")

    return None


def delete_tag(tag: str):
    """ Delete this function """
    code, out, err = _run_git_command(["tag", "-d", tag])
    if code == Status.OK:
        logger.info(f"Status: {out}, tag {tag} deleted...")
    else:
        logger.info(err)


def add():
    code, out, err = _run_git_command(
        ["add", "./CHANGELOG.md"]
    )
    if code == Status.OK:
        logger.info(
            f"Status: {out}, CHANGELOG.md added to git changes to send")
    else:
        logger.info(err)


def commit(message: str = "skip: CHANGELOG.md udpated"):
    code, out, err = _run_git_command(
        ["commit", "-m", message]
    )
    if code == Status.OK:
        logger.info(
            f"Status: {out}, changes to CHANGELOG.md have been commited")
    else:
        logger.info(err)


def reset():
    code, out, err = _run_git_command(
        ["reset", "--hard", "origin"]
    )
    if code == Status.OK:
        logger.info(f"Status: {out}")
    else:
        logger.info(err)


def validate_version():
    return


def ref_exists():
    return


def is_repo():
    """ check if current directory is a repository """
    code, out, err = _run_git_command(
        ["rev-parse", "--git-dir"]
    )
    if code == Status.OK:
        logger.info(f"Status: {out}")
    else:
        logger.info(err)


def get_head():
    code, out, err = _run_git_command(
        ["rev-parse", "HEAD"]
    )
    if code == Status.OK:
        logger.info(f"Status: {out}")
        return out.strip()
    else:
        logger.info(err)

    return None


def check_if_branch_up_to_date(remote: str, branch: str):
    code, out, err = _run_git_command(
        ["ls-remote", remote, branch]
    )
    if code == Status.OK:
        pattern: str = r"^(?P<ref>\w+)?"
        hash_remote_head: str = re.search(pattern, out)
        if get_head() == hash_remote_head.group(0):
            return True
    else:
        logger.info(err)

    return False


def is_detached():
    # TODO: improve Error handling???
    return subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True
    ).stdout.decode().strip() == "HEAD"


def fetch(remote: str, branch: str):
    if is_detached():
        code, out, err = _run_git_command(
            [
                "fetch",
                "--unshallow",
                "--tags",
                "--update-head-ok",
                remote,
                f"+refs/heads/{branch}:refs/heads/{branch}"
            ]
        )
        if code == Status.ERROR:
            code, out, err = _run_git_command(
                ["fetch", "--tags", "--update-head-ok",
                    remote, f"+refs/heads/{branch}:refs/heads/{branch}"]
            )
    else:
        code, out, err = _run_git_command(
            ["fetch", "--unshallow", "--tags", remote]
        )
        if code == Status.ERROR:
            code, out, err = _run_git_command(
                ["fetch", "--tags", remote]
            )


def get_default_branch() -> str:
    # pattern looks for any text after HEAD branch:
    pattern: str = r"(?<=HEAD branch: )\w+"
    code, out, err = _run_git_command(
        ["remote", "show", "origin"]
    )
    return re.search(pattern, out.strip()).group(0)
