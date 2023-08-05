import os
import time
import sys
from importlib import import_module
from multiprocessing import Process

import click
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class CustomFileSystemEventHandler(FileSystemEventHandler):
    def __init__(self, target, module):
        self.target = target
        self.module = module
        self.reload()

    def on_any_event(self, event):
        if event.src_path.endswith(('.py', '.md', '.html')):
            self.trigger_reload()

    def reload(self):
        target_kwargs = {
            'module': self.module,
        }

        self.process = Process(target=self.target, kwargs=target_kwargs)
        self.process.daemon = True
        self.process.start()

    def trigger_reload(self):
        self.process.terminate()
        self.process.join()
        self.reload()


def import_string(import_name):
    try:
        module_name, obj_name = import_name.rsplit('.', 1)
    except ValueError:
        module_name = import_name
        obj_name = 'bot'

    base = os.getcwd()
    sys.path.insert(0, base)

    try:
        module = import_module(module_name)
    except Exception as e:
        raise e

    try:
        return getattr(module, obj_name)
    except AttributeError as e:
        raise ImportError(e)


def run_bot(module):
    bot = import_string(module)

    try:
        bot.run()
    except KeyboardInterrupt:
        bot.stop()
        return


def run_with_reload(module):
    handler = CustomFileSystemEventHandler(target=run_bot, module=module)
    observer = Observer()
    observer.schedule(handler, '.', recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


def start(module, reload):
    if not reload:
        return run_bot(module)

    return run_with_reload(module)
