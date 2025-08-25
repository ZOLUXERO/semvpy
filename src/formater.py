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

    # TODO: all this function needs to be revised and refactored
    def group_changes_by_type(self, changes: list) -> dict:
        # TODO: se estan creando dos copias de la lista en memoria
        # puede causar problemas de rendimiento, posible solucion
        # un diccionario?
        commits: list = []
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

        # TODO: we may need to refactor this to use the
        # MAJOR_TYPES, MINOR_TYPES, PATCH_TYPES and ALL_TYPES
        # class variables
        grouped_changes: dict = {
            'feat': {'breaking_change': False, 'contents': []},
            'fix': {'breaking_change': False, 'contents': []},
            'chore': {'breaking_change': False, 'contents': []},
            'test': {'breaking_change': False, 'contents': []},
            'build': {'breaking_change': False, 'contents': []},
            'ci': {'breaking_change': False, 'contents': []},
            'docs': {'breaking_change': False, 'contents': []},
            'style': {'breaking_change': False, 'contents': []},
            'refactor': {'breaking_change': False, 'contents': []},
            'perf': {'breaking_change': False, 'contents': []},
            'revert': {'breaking_change': False, 'contents': []},
        }
        for change in changes:
            commits.append(change.split("|!|"))

        for index, commit in enumerate(commits):
            match = re.search(pattern, commit[Commit.MESSAGE])
            scope: str = ''
            message: str = ''
            body: str = ''
            breaking_change: bool = False

            if match.group(Change.SCOPE):
                scope = f' **{match.group(Change.SCOPE).strip('()')}**'
            if (match.group(Change.ATTENTION)):
                breaking_change = True
            if match.group(Change.MESSAGE):
                message = match.group(Change.MESSAGE)

            # Breaking changes must be allways in the body and
            # be uppercase text, contain a ':' and have a description
            if commit[Commit.BODY].strip() != '':
                body = f', {commit[Commit.BODY]}'
                if ('BREAKING_CHANGE:' in commit[Commit.BODY] or
                        'BREAKING-CHANGE:' in commit[Commit.BODY] or
                        'BREAKING CHANGE:' in commit[Commit.BODY]):
                    breaking_change = True

            if (grouped_changes[match.group(Change.TYPE)]['breaking_change'] is False
                    and breaking_change is True):
                grouped_changes[match.group(
                    Change.TYPE)]['breaking_change'] = True

            grouped_changes[match.group(Change.TYPE)]['contents'].append({
                'hash': commit[Commit.HASH],
                'scope': scope,
                'message': message,
                'body': body,
                'breaking_change': breaking_change,
                'text': f'- [[hash]({commit[Commit.HASH]
                                     })]{scope}:{message}{body}',
            })

        return grouped_changes

    def format_changes(self, changes: dict, version: str) -> str:
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

    def parse_version(self, version: str) -> list[int]:
        """ Parse version from vX.X.X to [X, X, X] """
        return [int(v) for v in version.replace('v', '').split('.')]

    def format_version(self, version: list[int]) -> str:
        """ Parse version from [X, X, X]  to vX.X.X """
        return f'v{'.'.join(map(str, version))}'

    def has_changes(
            self,
            changes: dict,
            categories: set,
            key: str = 'contents'
    ) -> bool:
        """ Check if a category of commits has changes """
        return any(changes.get(cat, {}).get(key) for cat in categories)

    def print_format(self, grouped_changes: dict):
        for value in grouped_changes:
            print(f'{value}:\n{grouped_changes[value]}')
