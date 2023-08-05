from .api import Api
from . import webcrawler
import logging

from time import sleep
from datetime import datetime

FUNCS = [
    'hacker_news',
    'hacker_news_archive',
    'heise_security',
    'fefe',
    'shz_ticker',
    'golem_ticker',
]

class Manager:

    def __init__(self, funcs):
        self.funcs = []
        for func in funcs:
            try:
                self.funcs.append(getattr(webcrawler, func))
            except Exception as e:
                logging.warning('no function called ' + str(func))

        self.api = Api()

    def login(self, username, password, api_url=''):
        if len(api_url)>0: self.api.load_schema(api_url)

        return self.api.login(username, password)

    def check(self):
        '''return True if everything is okay'''
        return not self.api.error

    def run(self):
        if self.api.error:
            logging.debug('Api Error - exit function')

        for func in self.funcs:
            urls = func()

            counter = 0
            for url in urls:
                if self.api.link_create(url):
                    counter += 1

            logging.info('Add '+str(counter)+' urls from function '+str(func))

    def periodic(self, seconds):
        running = True
        try:
            while running:
                logging.info('Run periodic at '+ str(datetime.now()))
                self.run()

                logging.info('Sleep for {} seconds'.format(seconds))
                for i in range(seconds): sleep(1)

        except KeyboardInterrupt:
            running = False
            logging.debug('Shutdown')
