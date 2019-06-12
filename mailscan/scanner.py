import mmap
import time

from requests import adapters
from fake_useragent import UserAgent
import re
from threading import Thread, active_count
from urllib.parse import urlparse

from requests_html import HTMLSession

from mailscan.logging import log
from mailscan.queue import Queue as UrlQueue


class Scanner:
    _regexp_mail = r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,6}'

    def __init__(self, starting_url):
        self.starting_url = starting_url
        self.url_queue = UrlQueue()
        self.session = self._init_session()
        self.headers = {'User-Agent': UserAgent().chrome}
        self.wait_count = 0
        self.url_queue.push(self.starting_url)

    def _init_session(self):
        sess = HTMLSession()
        adapter = adapters.HTTPAdapter(pool_connections=100, pool_maxsize=100)
        sess.mount('http://', adapter)
        sess.mount('https://', adapter)

        return sess

    def scan(self):
        while True:
            if self.url_queue.has_items:
                print(f'ACTIVE THREADS: {active_count()}')

                if active_count() >= 100:
                    time.sleep(5)
                else:
                    current = self.url_queue.get_next()
                    worker = Thread(target=self.parse, args=(current,))
                    worker.setDaemon(True)
                    worker.start()

            else:
                if active_count() == 0:
                    if self.wait_count >= 10:
                        log.info(f'Waited {self.wait_count} times for queue population. Exiting...')
                        break

                    log.info('Waiting for queue population')
                    time.sleep(5)
                    self.wait_count += 1

    def parse(self, url):
        webpage = self.session.get(url, allow_redirects=True, verify=False, headers=self.headers)

        if 'html' not in webpage.headers.get('Content-Type'):
            log.warning(
                f'Provided {webpage.url} is not of wanted Content-Type (is {webpage.headers.get("Content-Type")})')
            return False

        for a in webpage.html.find('a'):
            if 'href' in a.attrs:
                href = a.attrs.get('href')

                if href.startswith('/'):
                    href = '/'.join(webpage.url.split('/')[0:3]) + href

                if '://' not in href:
                    log.error(f'Provided URL has no proto specified ({href})')
                    continue

                if href is None or len(href) < 10:
                    log.error(f'Provided URL {href} is too short')
                    continue

                domain = '.'.join(urlparse(webpage.url).netloc.split('.')[-2:])
                if domain not in href:
                    log.warning(f"URL {href} is not in provided domain {domain}; omitting")
                    continue

                self.url_queue.push(href)

        for mail in re.findall(self._regexp_mail, webpage.content.decode(webpage.encoding)):
            self._add_mail(webpage.url, mail)
            return True

    def _add_mail(self, webpage, mail):
        with open('./mails.csv', mode='a+') as f:  # , mmap.mmap(f.fileno(), 0, mmap.MAP_PRIVATE, mmap.PROT_READ) as s:
            # if bytes(mail, encoding='UTF8') in s.read():
            #     log.warning(f'Tried to add {mail}, which is already added')
            #     return

            log.info(f'SUCCESS! Got {mail}!')
            f.writelines(f'"{webpage}";"{mail}"\n')
