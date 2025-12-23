import pathlib
import os

class FSService:
    def __init__(self,
                 data_directory: str) -> None:
        self._data_directory = pathlib.Path(data_directory)

        self._create_data_directory()
    
    def file_exists(self, filepath: pathlib.Path) -> bool:
        pass

    def save_file(self, filepath: pathlib.Path, data: bytes, replace: bool = True) -> None:
        pass

    def delete_file(self, filepath: pathlib.Path) -> None:
        pass

    def read_file(self, filepath: pathlib.Path) -> None:
        pass

    def _create_data_directory(self) -> None:
        if self._data_directory.exists():
            return
        
        os.makedirs(str(self._data_directory))