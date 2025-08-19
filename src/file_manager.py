from pathlib import Path
from enum import IntEnum


class Commit(IntEnum):
    HASH = 0
    MESSAGE = 1
    FOOTER = 2


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
            'reafactor': [],
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
        for index, item in enumerate(commits):
            message: str = item[Commit.MESSAGE].strip().split(':')
            footer: str = ''
            if item[Commit.FOOTER].strip() != '':
                footer = f', {item[Commit.FOOTER]}'

            formated_commits[message[0]].append({
                'hash': f'[hash]({item[Commit.HASH]})',
                'scope': '',
                'message': message[1],
                'footer': footer,
            })

        self.print_format(formated_commits)

        # result = '\n'.join(formated_commits)
        # return result
        #

    def print_format(self, formated_commits: dict):
        for value in formated_commits:
            print(f'{value}:\n{formated_commits[value]}')
