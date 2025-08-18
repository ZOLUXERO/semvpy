from pathlib import Path


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
        formated_commits: list = []
        result: str = ""

        for change in changes:
            commits.append(change.split("|!|"))

        for item in commits:
            item[0] = f'[hash]({item[0]})'
            item[1] = f'{item[1]}'
            if item[2].strip() != "":
                item[2] = f', {item[2]}'
            formated_commits.append(' '.join(item))

        result = '\n'.join(formated_commits)
        return result
