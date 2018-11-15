import os
import re
import shutil
import random
import string
import logging


class CodeLines(object):

    def __init__(self, start_line='<?php\n', end_line='', spaces='    '):
        self.start_line = start_line
        self.end_line = end_line
        self.spaces = spaces
        self.lines = []

    def add_line(self, line, indent=0):
        self.lines.append((line, indent))

    def add_lines(self, lines=[]):
        for line, indent in lines:
            self.add_line(line, indent)

    def add_text(self, text):
        lines = [(line, 0) for line in text.strip('\n').split('\n')]
        self.add_lines(lines)

    def dump(self, indent=0):
        lines = []
        # start line
        if self.start_line:
            lines.append(''.join([
                self.spaces * indent,
                self.start_line
            ]))
        # content lines
        for line, i in self.lines:
            i += indent
            lines.append(''.join([
                self.spaces * i,
                line
            ]))
        # end line
        if self.end_line:
            lines.append(''.join[
                self.spaces * indent,
                self.end_line
            ])

        return lines

    def save(self, output, mode='w', indent=0, encoding='utf8'):
        lines = self.dump(indent)
        with open(output, mode, encoding=encoding) as f:
            f.write('\n'.join(lines))

def id_generator(size=32, chars=string.ascii_letters + string.digits + "-_"):
    return ''.join(random.choices(chars, k=size))


def copyfile(src, dst):
    parent_dir = os.path.dirname(dst)
    if not os.path.isdir(parent_dir):
        os.makedirs(parent_dir)
    shutil.copyfile(src, dst)

def get_logger(logger_name='YiiDemo', log_file='running.log'):
    # create logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    fh = logging.FileHandler(log_file)
    # fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    # ch.setLevel(logging.ERROR)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger


def tpl(text, _left_delimiter='{{', _right_delimiter='}}', _ignore_errors=False, 
    **kwargs):
    def callback(m):
        key = m.group(1)
        if (not _ignore_errors) and (key not in kwargs):
            raise KeyError('Missing the keyword: {}'.format(key))
        return str(kwargs.get(key, ''))

    return re.sub(''.join([
        _left_delimiter, '(.+?)', _right_delimiter
    ]), callback, text)