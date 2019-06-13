from .logging import log


class Queue:
    def __init__(self):
        self.items = []
        self.popped_items = []

    @property
    def has_items(self):
        return bool(self.items)

    def get_next(self):
        if self.has_items:
            return self.pop()
        else:
            log.warning('No more items in queue')

    def pop(self):
        current = self.items.pop(0)
        self.popped_items.append(current)
        log.info(f'Popped {current}\nQueue length: {len(self.items)}')

        return current

    def push(self, url):
        if not isinstance(url, str):
            log.warning(f'Cannot add object of type {type(url)} to queue!')
            return None

        try:
            url = self._parse_url(url)
        except TypeError:
            return None

        if url in self.popped_items:
            log.info(f"Already scanned the {url}; omitting")
            return None

        if url in self.items:
            log.info(f"Url {url} is already in queue; omitting")
            return None

        log.info(f'Adding {url} to the queue\nQueue length: {len(self.items)}')
        self.items.append(url)

        return url

    def _parse_url(self, url: str):
        if 'mailto' in url:
            raise TypeError

        if '@' in url:
            raise TypeError

        # wytnij wszystkie znaki po hashu włącznie
        if '#' in url:
            url = url[:url.index('#')]

        return url
