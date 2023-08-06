import threading
import random
import time
import datetime
import requests
import dynamon
import copy


class _Dynamon():
    def __init__(self):
        self.first_run = True
        self.cache = {}  # One list [{x, y}] per id ''
        self.push_is_scheduled = False
        self.path_was_generated = False

    def push(self, *args, id='1'):
        self.ensure_path()
        self.print_info()

        # Parse args and update cache
        x, y = self.parse_args(*args)
        self.update_cache(x, y, id)

        # Schedule a push of the cache
        if not self.push_is_scheduled:
            self.push_is_scheduled = True
            threading.Thread(target=self.push_cache).start()

    def clear(self):
        self.ensure_path()
        self.print_info()
        self.cache = {}
        threading.Thread(target=self.clear_request).start()

    def clear_request(self):
        url = 'https://dynamon.io/' + dynamon.path
        requests.delete(url)

    def ensure_path(self):
        if not dynamon.path:
            dynamon.path = self.generate_random_path()
            self.path_was_generated = True

    def print_info(self):
        if self.first_run:
            print('Dynamon: Output at https://dynamon.io/' + dynamon.path)
            if self.path_was_generated:
                print('Set path manually by: dynamon.path = \'my-unique-path\'')
            self.first_run = False

    def parse_args(self, *args):
        if len(args) == 0:
            raise Exception('Missing argument.')
        elif len(args) == 1:
            x = self.get_now_iso()
            y = args[0]
        elif len(args) == 2:
            x = args[0]
            y = args[1]
        else:
            raise Exception('Invalid arguments.')

        return x, y

    def update_cache(self, x, y, id):
        if not id in self.cache:
            self.cache[id] = [[]]

        if not self.is_iterable(y):
            y = [y]

        for i, yi in enumerate(y):
            if len(self.cache[id]) < i + 1:
                self.cache[id].append([])
            self.cache[id][i].append({'x': x, 'y': yi})

    def push_cache(self):
        # During this time self.cache will build up by calls to self.push.
        time.sleep(dynamon.cache_timeout)

        # Abort if cache has been emptied.
        if not self.cache: return

        # Empty the queue and keep a local copy because
        # the http request will take a while to finalize.
        queue = copy.deepcopy(self.cache)
        self.cache = {}

        self.push_is_scheduled = False

        url = 'https://dynamon.io/' + dynamon.path

        requests.post(url, json=queue)

    def get_now_iso(self):
        return datetime.datetime.utcnow().isoformat() + 'Z'

    def is_iterable(self, obj):
        """Returns True for native lists, numpy arrays, etc."""
        try:
            iter(obj)
            return True
        except:
            return False

    def generate_random_path(self):
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
        return ''.join(random.choice(chars) for _ in range(8))


# Expose no more than needed
_dynamon = _Dynamon()
push = _dynamon.push
clear = _dynamon.clear
