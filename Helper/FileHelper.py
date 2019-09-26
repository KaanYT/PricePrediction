import os


class FileHelper(object):

    @staticmethod
    def append_to_file(filename, text):
        hs = open(filename, "a")
        hs.write(str(text) + "\n")
        hs.close()

    @staticmethod
    def create_path_if_not_exists(path):
        if not os.path.exists(path):
            os.makedirs(path)
        return path
