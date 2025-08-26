from enum import IntEnum
import re


class Commit(IntEnum):
    HASH = 0
    MESSAGE = 1
    BODY = 2


class Change(IntEnum):
    TYPE = 1
    SCOPE = 2
    ATTENTION = 3
    MESSAGE = 4


class Formater:
    MAJOR_TYPES: set = {"perf"}
    MINOR_TYPES: set = {"feat", "chore",
                        "docs", "style", "refactor", "ci"}
    PATCH_TYPES: set = {"fix", "build", "test", "revert"}
    ALL_TYPES: set = MAJOR_TYPES | MINOR_TYPES | PATCH_TYPES

    @staticmethod
    def parse_commit(commit: str, pattern: str) -> dict:
        parts = commit.split("|!|")
        match = re.search(pattern, parts[Commit.MESSAGE])
        if not match:
            return None

        return {
            "type": match.group(Change.TYPE),
            "scope": match.group(Change.SCOPE),
            "attention": match.group(Change.ATTENTION),
            "message": match.group(Change.MESSAGE),
            "body": parts[Commit.BODY],
            "hash": parts[Commit.HASH],
        }

    @staticmethod
    def is_breaking_change(commit):
        if commit["attention"]:
            return True

        body = commit["body"]
        return any(x in body for x in ["BREAKING_CHANGE:", "BREAKING-CHANGE:", "BREAKING CHANGE:"])

    @staticmethod
    def group_changes_by_type(changes: list) -> dict:
        # Examples:
        # feat: message
        # feat<!optional>: message
        # feat<(scope)optional>: message
        # feat<(scope)optional><!optional>: message
        #
        # r"(<type>group=1) (<scope, optional>group=2)
        # (! breagking change, optional>group=3) <:>,
        # (message between 1 and 100 character>group=4)"
        pattern: str = r"(feat|fix|chore|test|build|ci|docs|style|refactor|perf|revert)(\(.+\))?(!)?:(.{1,100})"
        grouped = {change_type: {"breaking_change": False, "contents": []}
                   for change_type in Formater.ALL_TYPES}

        # TODO: se estan creando dos copias de la lista en memoria
        # puede causar problemas de rendimiento, posible solucion
        # un diccionario?
        parsed_commits = list(
            filter(None, map(lambda c: Formater.parse_commit(c, pattern), changes)))

        for commit in parsed_commits:
            breaking = Formater.is_breaking_change(commit)
            scope = f' **{commit["scope"].strip("()")
                          }**' if commit["scope"] else ""
            body = f' ,{commit["body"]
                        }' if commit["body"].strip() != '' else ""
            entry = {
                'hash': commit["hash"],
                'scope': scope,
                'message': commit["message"],
                'body': body,
                'breaking_change': breaking,
                'text': f'- [[hash]({commit["hash"]
                                     })]{scope}:{commit["message"]}{body}',
            }
            grouped[commit["type"]]["contents"].append(entry)
            if breaking:
                grouped[commit["type"]]["breaking_change"] = True

        return grouped

    # TODO: add @staticmethod and remove self
    def format_changes(self, changes: dict, version: str) -> str:
        try:
            markdown_text: str = f'# {version}'
            for change_type in changes:
                if changes[change_type]['contents']:
                    body = [d['text']
                            for d in changes[change_type]['contents']]
                    body = '\n'.join(body)
                    markdown_text += f'\n### {change_type.title()}\n'
                    markdown_text += body
            markdown_text += '\n'
            return markdown_text
        except KeyError as e:
            print(f"ERROR: Missing expected key in changes dict: {e}")
            return f"# {version}\nERROR: Could not format changes due to missing key: {e}\n"
        except Exception as e:
            print(f"ERROR: Unexpected error in format_changes: {e}")
            return f"# {version}\nERROR: Could not format changes due to unexpected error: {e}\n"

    # TODO: add @staticmethod and remove self
    def update_version(
            self,
            changes: dict,
            last_version: str
    ) -> str:
        if last_version is None:
            return self.format_version([1, 0, 0])

        MAJOR, MINOR, PATCH = 0, 1, 2
        version = self.parse_version(last_version)

        if self.has_changes(changes, self.ALL_TYPES, 'breaking_change'):
            version[MAJOR] += 1
            version[MINOR] = 0
            version[PATCH] = 0
        elif self.has_changes(changes, self.MAJOR_TYPES):
            version[MAJOR] += 1
            version[MINOR] = 0
            version[PATCH] = 0
        elif self.has_changes(changes, self.MINOR_TYPES):
            version[MINOR] += 1
            version[PATCH] = 0
        elif self.has_changes(changes, self.PATCH_TYPES):
            version[PATCH] += 1

        return self.format_version(version)

    @staticmethod
    def parse_version(version: str) -> list[int]:
        """Parse version from vX.X.X to [X, X, X]"""
        return [int(v) for v in version.replace('v', '').split('.')]

    @staticmethod
    def format_version(version: list[int]) -> str:
        """Parse version from [X, X, X] to vX.X.X"""
        return f"v{'.'.join(map(str, version))}"

    # TODO: add @staticmethod and remove self
    def has_changes(
            self,
            changes: dict,
            categories: set,
            key: str = 'contents'
    ) -> bool:
        """ Check if a category of commits has changes """
        return any(changes.get(cat, {}).get(key) for cat in categories)

    # TODO: add @staticmethod and remove self
    def print_format(self, grouped_changes: dict):
        for value in grouped_changes:
            print(f'{value}:\n{grouped_changes[value]}')
