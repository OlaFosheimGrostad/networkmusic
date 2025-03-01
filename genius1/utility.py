from html.parser import HTMLParser


class _HtmlStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self._result = []
        self._builder = []

    def flush_line(self):
        tmp = ''.join(self._builder)
        self._result.append(tmp)
        self._builder.clear()

    def handle_starttag(self, tag, attrs):
        if tag == 'br':
            self.flush_line()

    def handle_data(self, data):
        self._builder.append(data)

    def get_result_as_string(self) -> str:
        if len(self._builder) != 0:
            self.flush_line()
        return '\n'.join(self._result)


def strip_lyrics_webpage(html_source: str) -> str:
    i1 = html_source.index('>', html_source.index('<div data-lyrics-container="true" '))
    i2 = html_source.index('<div class="LyricsFooter')
    lyrics_html = html_source[i1+1:i2]
    stripper = _HtmlStripper()
    stripper.feed(lyrics_html)
    return stripper.get_result_as_string()
