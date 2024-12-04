from File_handler import FileHandler
 
## Handles individual PDF downloads
class Controller:
    def __init__(self, file_path_gri, destination_folder, output_folder):
        self.file_path_gri = file_path_gri
        self.destination_folder = destination_folder
        self.output_folder = output_folder
        self.file_handler = FileHandler(file_path_gri, destination_folder, output_folder)

    def start(self):
        self.file_handler.start_download()
