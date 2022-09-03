#!/usr/bin/env python
# -.- coding: utf-8 -.-

import argparse
import configparser
from pathlib import Path
from datetime import datetime, date
import time
import shutil
import sys


class Fotorzr(object):
    config = None
    config_path = None
    source_path = ''
    target_path = ''
    begin_date = ''

    def __init__(self, source_dir='', target_dir=''):
        self.read_config(args.config)

        if source_dir and target_dir:
            self.set_dirs(source_dir, target_dir)
        else:
            self.set_dirs(
                self.config.get('Path', 'source_dir'),
                self.config.get('Path', 'target_dir')
            )

        # save config
        if args.save is True:
            self.config.set('Path', 'source_dir', str(self.source_path))
            self.config.set('Path', 'target_dir', str(self.target_path))
            self.write_config()

        # set date range
        begin_date = None
        end_date = None
        if b:= args.begin_date:
            begin_date = b
        elif b:= self.config.get('Changes', 'last_date', fallback=''):
            begin_date = b

        if begin_date:
            begin_date = date(
                year=2000 + int(b[0:2]),
                month=int(b[2:4]),
                day=int(b[4:6]))
        self.begin_date = begin_date
        self._print(f'set begin_date => {begin_date}')

    def _print(self, message):
        print (f'fotorzr) {message}')

    def set_dirs(self, source_dir='', target_dir=''):
        source_path = Path(source_dir)
        target_path = Path(target_dir)
        if self.check_dirs([source_path, target_path]):
            self.source_path = source_path
            self.target_path = target_path

            self._print(f"set dirs => source: {self.source_path}, target: {self.target_path}")

    def check_dirs(self, dir_list):
        for i in dir_list:
            if not Path(i).exists():
                self._print(f'path: {i} not exists')
                return False
        return True

    def read_config(self, conf_rel_path):
        self.config = configparser.ConfigParser()
        self.config_path = Path.cwd().joinpath(conf_rel_path)
        self.config.read(self.config_path)

    def exec_copy(self, dry_run=False):
        if not self.source_path or not self.target_path:
            self._print('error: source or target path not ok')
            return False

        new_dir = []
        last_dir = ''
        for foto_file in self.source_path.iterdir():
            file_datetime = datetime.fromtimestamp(foto_file.stat().st_mtime)#.strftime(args.date_format)
            file_date = file_datetime.date()
            last_dir = file_date.strftime(args.date_format)

            if file_date >= self.begin_date:
                target_date_path = self.target_path.joinpath(last_dir)
                self._print('copy file: {} ({}) => {}'.format(
                    foto_file.resolve(),
                    datetime.fromtimestamp(foto_file.stat().st_mtime),
                    target_date_path))

                if last_dir not in new_dir:
                    new_dir.append(last_dir)

                if dry_run is False and target_date_path.exists() is False:
                    self._print(f'create dir: {target_date_path}')
                    target_date_path.mkdir()

                end_date = file_date

                if dry_run is False:
                    shutil.copy2(foto_file, target_date_path)
                else:
                    pass

        self._print('create dirs: {}'.format(', '.join(new_dir)))

        self.config.set('Changes', 'last_date', last_dir)
        self.write_config()
        self._print(f'update last_date: {last_dir}')

    def write_config(self):
        with open(self.config_path, 'w') as configfile:
            self.config.write(configfile)

def main(args):

    if args.dirs:
        foto = Fotorzr(args.dirs[0], args.dirs[1])
    else:
        # use config.ini
        foto = Fotorzr()

    foto.exec_copy(args.is_dry_run)


parser = argparse.ArgumentParser(description='Copy foto from camera to disk')
parser.add_argument('-c', '--config', dest='config', default='config.ini', help='config path')
parser.add_argument('-d', '--dirs', dest='dirs', nargs=2, help='set source target dirs')
parser.add_argument('-s', '--save', action='store_true')
parser.add_argument('-t', '--dry-run', dest='is_dry_run', action='store_true', help='dry run')
parser.add_argument('-f', '--date-format', dest='date_format', default='%y%m%d', help='set target folder format')
parser.add_argument('-b', '--begin-date', dest='begin_date', help='set begin from date')

args = parser.parse_args()

if __name__ == '__main__':
    if len(sys.argv) == 1:
        parser.print_help()
    else:
        main(args)
        #print(args)

