#https://github.com/goldsmith/Wikipedia
import wikipedia


class Wikipedia(object):

    @staticmethod
    def setup(self):
        wikipedia.set_lang("en")

    @staticmethod
    def test():
        wikipedia.summary("Facebook")
        print("test")

    @staticmethod
    def search(keyword):
        return wikipedia.search(keyword)

    # page = 'content', 'summary', 'images', 'references', 'links', 'sections', url, title
    @staticmethod
    def get_page(title, pageid=None):
        return wikipedia.page(title=title, pageid=pageid)
