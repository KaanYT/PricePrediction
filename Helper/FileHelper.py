
class FileHelper(object):

    @staticmethod
    def append_to_file(filename, text):
        hs = open(filename, "a")
        hs.write(str(text) + "\n")
        hs.close()
