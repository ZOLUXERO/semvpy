from pathlib import Path
from enum import IntEnum
import re


class Commit(IntEnum):
    HASH = 0
    MESSAGE = 1
    FOOTER = 2


class Change(IntEnum):
    TYPE = 1
    SCOPE = 2
    BREAKING_CHANGE = 3


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

    def format(self, changes: list) -> str:
        # TODO: se estan creando dos copias de la lista en memoria
        # puede causar problemas de rendimiento, posible solucion
        # un diccionario?
        commits: list = []
        formated_commits: dict = {
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

        result: str = ""

        for change in changes:
            commits.append(change.split("|!|"))

        # TODO: validar si el scope viene con el mensaje del commit
        # si no viene dejarlo vacio, si viene ponerlo con el formato
        # **scope:**.
        # En vez de hacer otro diccionario dentro de formated_commits
        # devolver de una vez un string formateado como:
        # f'hash, <scope: si existe>, mensaje, <footer si existe>'
        # probablemente haya que hacer un regex para validar si el mensaje
        # viene con scope.
        # retornar resultado
        #
        # feat: message
        # feat(scope): message
        # feat!: message
        # feat(scope)!: message

        # r"<type>group=1, <scope, optional>group=2,
        # <! breagking change, optional>group=3, <:>"
        pattern = r"(feat|fix|chore|test|build|ci|docs|style|refactor|perf|revert)(\(.+\))?(!)?:"

        for index, commit in enumerate(commits):
            match = re.search(pattern, commit[Commit.MESSAGE])
            print(match.group())
            if match.group(Change.SCOPE):
                print("tiene scope")
            else:
                print("no tiene scope")

            if match.group(Change.BREAKING_CHANGE):
                print("contiene Breaking change")
            else:
                print("No contiene Breaking change")

            message: str = commit[Commit.MESSAGE].strip().split(':', 1)
            footer: str = ''
            scope: str = ''
            if commit[Commit.FOOTER].strip() != '':
                footer = f', {commit[Commit.FOOTER]}'

            formated_commits[message[0]].append({
                'hash': f'[hash]({commit[Commit.HASH]})',
                'scope': scope,
                'message': message[1],
                'footer': footer,
            })

#        self.print_format(formated_commits)

        # result = '\n'.join(formated_commits)
        # return result
        #

    def print_format(self, formated_commits: dict):
        for value in formated_commits:
            print(f'{value}:\n{formated_commits[value]}')
