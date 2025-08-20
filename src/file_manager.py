from pathlib import Path
from enum import IntEnum
import re


class Commit(IntEnum):
    HASH = 0
    MESSAGE = 1
    BODY = 2


class Change(IntEnum):
    TYPE = 1
    SCOPE = 2
    BREAKING_CHANGE = 3
    MESSAGE = 4


class File:
    def __init__(self, file_name: str):
        self.file_name = file_name
        self.path = Path(file_name)
        self.exists()

    def exists(self):
        try:
            path = Path(self.file_name)
            contents = path.read_text(encoding="utf-8")
            print(f'File: {path} exists, {contents}')
        except Exception as e:
            print(f'ERROR: {e}')
            self.create_file()

    def create_file(self):
        try:
            file = self.path
            file.touch()
            print(f'File {self.file_name} created.')
        except Exception as e:
            print(f'ERROR: {e}')
            raise

    def write_changelog(self, changes: str):
        try:
            with self.path.open("r+") as file:
                # INFO: Carga el archivo en memoria,
                # no es eficiente con archivos grandes!!!
                content = file.read()
                file.seek(0, 0)
                file.write(changes + content)
                file.close()
        except Exception as e:
            print(f'ERROR: {e}')
            raise

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
        grouped_changes: dict = {
            'feat': [],
            'fix': [],
            'chore': [],
            'test': [],
            'build': [],
            'ci': [],
            'docs': [],
            'style': [],
            'refactor': [],
            'perf': [],
            'revert': [],
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
            if match.group(Change.BREAKING_CHANGE):
                breaking_change = True
            if match.group(Change.MESSAGE):
                message = match.group(Change.MESSAGE)

            if commit[Commit.BODY].strip() != '':
                body = f', {commit[Commit.BODY]}'

            grouped_changes[match.group(Change.TYPE)].append({
                'hash': commit[Commit.HASH],
                'scope': scope,
                'message': message,
                'body': body,
                'breaking_change': breaking_change,
                'text': f'- [hash]({commit[Commit.HASH]
                                    }){scope}:{message}{body}',
            })

        return grouped_changes

    def format_changes(self, grouped_changes: dict) -> str:
        markdown_changes: str = ''
        for commit_type in grouped_changes:
            if grouped_changes[commit_type]:
                changelog_body = [d['text']
                                  for d in grouped_changes[commit_type]]
                changelog_body = '\n'.join(changelog_body)
                markdown_changes += f'\n## {commit_type.title()}\n'
                markdown_changes += changelog_body

        markdown_changes += '\n'
        return markdown_changes

    def update_version(self, changes: dict,
                       old_version: str = 'v1.4.0') -> str:
        MAJOR, MINOR, PATCH = 0, 1, 2
        version = old_version.replace('v', '').split('.')
        major_categories: set = {"perf"}
        minor_categories: set = {"feat", "chore",
                                 "docs", "style", "refactor", "ci"}
        patch_categories: set = {"fix", "build", "test", "revert"}
        version_str: str = ''

        if any(changes.get(category) for category in major_categories):
            version[MAJOR] = str(int(version[MAJOR]) + 1)
        elif any(changes.get(category) for category in minor_categories):
            version[MINOR] = str(int(version[MINOR]) + 1)
        elif any(changes.get(category) for category in patch_categories):
            version[PATCH] = str(int(version[PATCH]) + 1)

        version_str = f'v{'.'.join(version)}'
        print(version_str)
        return version_str

    def print_format(self, grouped_changes: dict):
        for value in grouped_changes:
            print(f'{value}:\n{grouped_changes[value]}')
