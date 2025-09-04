from pathlib import Path
from semvpy.logger import logger
import json


class File:

    def __init__(self, file_name: str):
        self.file_name = file_name
        self.path = Path(file_name)

    # TODO: add @staticmethod, remove self
    def exists(self) -> bool:
        try:
            path = Path(self.file_name)
            if not path.is_file():
                logger.info(f"File: {path} does not exist")
                return False
            # Optionally, try reading a small chunk to check readability
            with path.open("r", encoding="utf-8") as f:
                f.read(1)
            logger.info(f'File: {path} exists and is readable')
            return True
        except FileNotFoundError:
            logger.error(f"ERROR: File {self.file_name} not found")
            return False
        except PermissionError:
            logger.error(f"ERROR: Permission denied for file {self.file_name}")
            return False
        except Exception as e:
            logger.error(f'Unexpected error in exists: {e}')
            return False

    # TODO: add @staticmethod, remove self
    # and improve Error handling
    def create_file(self):
        try:
            file = self.path
            file.touch()
            logger.info(f'File {self.file_name} created.')
        except Exception as e:
            logger.error(f'ERROR: {e}')
            raise

    # TODO: add @staticmethod, remove self
    def write_changelog(self, changes: str):
        try:
            with self.path.open("r+") as file:
                content = file.read()
                file.seek(0, 0)
                file.write(changes + content)
        except FileNotFoundError:
            logger.error(f"ERROR: file {self.file_name} not found")
        except PermissionError:
            logger.error(f"ERROR: Permission denied for file {self.file_name}")
        except OSError as e:
            logger.error(f"ERROR: OS error while writing changelog: {e}")
        except Exception as e:
            logger.error(f"ERROR: Unexpected error in write_changelog: {e}")

    # TODO: add @staticmethod, remove self
    def update_package_version(self, new_version: str):
        try:
            with self.path.open(mode="r") as file:
                data = json.load(file)

            data['version'] = new_version

            with self.path.open(mode="w") as file:
                json.dump(data, file, indent=2)
                logger.info(f"Version updated in {file}")

        except FileNotFoundError:
            logger.error(f"ERROR: file {file} not found")
        except json.JSONDecodeError:
            logger.error(f"ERROR: failed to decode JSON from {file}.")
        except Exception as e:
            logger.error(f"ERROR: unexpected error: {e}.")
