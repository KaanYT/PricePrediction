import feedparser

class Parser(object):

    def __init__(self, *args):
        self.feedParser = feedparser.parse('http://feedparser.org/docs/examples/atom10.xml')

    def parse(link):
        return feedparser.parse(link)
