from html.parser import HTMLParser


class PRNewswireParser(HTMLParser):
    # parses articles to get content

    def __init__(self):
        self.in_set = set()
        self.in_p = False
        self.no_parse_date = False
        self.levels = 0

        self.title = ""
        self.body = ""
        self.date = ""
        self.date_publish = ""
        self.date_create = ""
        self.date_modify = ""
        super().__init__()

    @property
    def res(self):
        result = {
            'date': self.date,
            'title': self.title,
            'body': self.body
        }

        return result

    @property
    def in_body(self):
        return 'body' in self.in_set

    @property
    def in_date(self):
        return 'date' in self.in_set

    @property
    def in_title(self):
        return 'title' in self.in_set

    def outside(self, tag):
        self.in_set.remove(tag)

    def inside(self, tag):
        self.in_set.add(tag)

    def try_get_date(self, attrs):

        date_type = None
        content = None

        for attr in attrs:
            if attr[1] is None:
                continue
            elif attr[0] == 'itemprop':
                date_type = attr[1]
            elif attr[0] == 'content':
                content = attr[1]

        if date_type == 'datePublished':
            self.date_publish = content
            return True
        elif date_type == 'dateCreated':
            self.date_create = content
            return True
        elif date_type == 'dateModified':
            self.date_modify = content
            return True

        return False

    def try_get_title(self, attrs):

        is_title = False
        content = None

        for attr in attrs:
            if attr[1] == 'og:title' or attr[1] == 'twitter:title':
                is_title = True
            elif attr[0] == 'content':
                content = attr[1]

        if is_title:
            self.title = content
            return True

        return False

    def handle_starttag(self, tag, attrs):
        if tag == 'br':
            return

        if tag == 'p' or tag == 'pre':
            self.in_p = True

        if tag == 'title':
            self.inside('title')

        res = self.try_get_title(attrs)
        if not res:
            for attr in attrs:
                if attr[1] == 'articleBody':
                    self.inside('body')
                if attr[1] == 'xn-chron' and not self.no_parse_date:
                    self.inside('date')

        if self.in_body:
            self.levels = self.levels + 1

    def handle_endtag(self, tag):

        if tag == 'p':
            self.in_p = False

        if self.levels > 0:
            self.levels = self.levels - 1

        if self.in_body and self.levels <= 0:
            self.outside('body')

    def handle_data(self, data):

        if '/PRNewswire' in data and self.in_p:
            self.no_parse_date = True
            if not self.in_body:
                self.inside('body')
                self.levels = self.levels + 4

        if self.in_title:
            self.title = data
            self.outside('title')
        elif self.in_date:
            self.date = data
            self.outside('date')
        elif self.in_body:
            self.body = self.body + data


if __name__ == '__main__':

    parser = PRNewswireParser()
    parser.feed('<html><head><title>Test</title></head>'
                '<body><h1>Parse me!</h1></body></html>'
                '<p class="articleBody">Hello World!</p>'
                '<p class="xn-chron">Jan 07, 2021, 11:00 ET</p>')

    print(f'date: {parser.date}')
    print(f'title: {parser.title}')
    print(f'body: {parser.body}')


