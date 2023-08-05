import os

import yaml


class PlayDB(object):
    def __init__(self):
        config_path = '{}/.cache/playlist'.format(os.getenv('HOME'))

        self._config = '{}/db.yml'.format(config_path)
        if not os.path.isfile(self._config):
            os.makedirs(config_path)
            yaml.safe_dump({}, open(self._config, 'w'))

        self._db = yaml.safe_load(open(self._config, 'r'))

        self._path = os.path.realpath('.')
        if self._path not in self._db:
            self._db[self._path] = {'files': [], 'offset': 0, 'config': ''}

        self._item = self._db[self._path]

    def __del__(self):
        yaml.safe_dump(
            self._db, open(self._config, 'w'), width=76,
            default_flow_style=False)

    def _overflow(self):
        return self._item['offset'] >= len(self._item['files'])

    def add(self, files):
        for file_name in files:
            if not file_name.startswith('.') and os.path.isfile(file_name):
                if file_name not in self._item['files']:
                    self._item['files'].append(file_name)

    def remove(self, files):
        for index, file_name in enumerate(self._item['files']):
            if file_name in files:
                self._item['files'].pop(index)
                if index < self._item['offset']:
                    self._item['offset'] -= 1

    def set(self, filename):
        for index, file_name in enumerate(self._item['files']):
            if file_name == filename:
                self._item['offset'] = index
                return

    def current(self):
        if self._overflow():
            return ''
        return self._item['files'][self._item['offset']]

    def next(self):
        if self._overflow():
            return
        self._item['offset'] += 1

    def show(self):
        print 'Playlist:'
        for index, file_name in enumerate(self._item['files']):
            spacer = ' '
            if index == self._item['offset']:
                spacer = '*'
            print '{} {}'.format(spacer, file_name)
        print '\nConfig: {}'.format(self._item['config'])

    def config(self, config_string):
        self._item['config'] = config_string

    def show_config(self):
        print self._item['config']
