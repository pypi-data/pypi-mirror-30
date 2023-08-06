class Std:
    def _elements(self, idx, content=None) -> list:
        if not content:
            content = self.content
        return self.document_fromstring(content, idx)

    def _cover_from_content(self, selector, attr='src') -> str:
        image = self._elements(selector)
        if image and len(image):
            return self.http().normalize_uri(image[0].get(attr))

    @staticmethod
    def _first_select_options(parser, selector, skip_first=True) -> list:
        options = 'option'
        if skip_first:
            options = 'option + option'
        select = parser.cssselect(selector)
        if select:
            return select[0].cssselect(options)
        return []

    @classmethod
    def _images_helper(cls, parser, selector, attr='src') -> list:
        image = parser.cssselect(selector)
        return [i.get(attr).strip(r' \r\n\t\0') for i in image]

    @classmethod
    def _idx_to_x2(cls, idx, default=0) -> list:
        return [
            str(idx[0]),
            str(default if len(idx) < 2 or not idx[1] else idx[1])
        ]

    @staticmethod
    def _join_groups(idx, glue='-') -> str:
        result = []
        for i in idx:
            if i:
                result.append(i)
        return glue.join(result)

    def _get_name(self, selector, url=None) -> str:
        if url is None:
            url = self.get_url()
        return self.re.search(selector, url).group(1)

    def _get_content(self, selector) -> str:
        return self.http_get(selector.format(self.domain, self.manga_name))

    def _base_cookies(self):
        cookies = self.http().get_base_cookies(self.get_url())
        self._storage['cookies'] = cookies.get_dict()

    def parse_background(self, image) -> str:
        selector = r'background.+?url\([\'"]?([^\s]+?)[\'"]?\)'
        url = self.re.search(selector, image.get('style'))
        return self.http().normalize_uri(url.group(1))

    @property
    def content(self):
        content = self._storage.get('main_content', None)
        if content is None:
            content = self.get_main_content()
        return content

    @property
    def manga_name(self) -> str:
        name = self._storage.get('manga_name', None)
        if name is None:
            name = self.get_manga_name()
        return name

    @staticmethod
    def normal_arc_name(idx):
        fmt = 'vol_{:0>3}'
        if len(idx) > 1:
            fmt += '-{}'
        return fmt.format(*idx)
