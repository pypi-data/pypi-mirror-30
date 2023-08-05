import os

class FileSystemOps(object):
    @staticmethod
    def get_file_list(dir_path, ext):
        file_list = []
        print(os.listdir(dir_path))
        for file in os.listdir(dir_path):
            if file.endswith(ext):
                file_list.append(os.path.join(dir_path, file))
        return file_list