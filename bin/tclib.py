#!/usr/bin/env python

""" standard """
import argparse
import json
import os
import pip
import shutil
import subprocess
import sys
import traceback
from setuptools.command import easy_install
""" third-party """
""" custom """

parser = argparse.ArgumentParser()
parser.add_argument(
    '--app_name', help='Fully qualified path of App.', required=False)
parser.add_argument(
    '--app_path', help='Fully qualified path of App.', required=False)
parser.add_argument(
    '--config', help='Configuration file for gen lib.', required=False)
#     '--config', default="tcex.json", help='Configuration file for gen lib.', required=False)
args, extra_args = parser.parse_known_args()


# TODO: Clean this up when time allows
class TcLib(object):
    def __init__(self, args):
        """ """
        self._args = args
        self.app_path = os.getcwd()
        self.exit_code = 0

        # color settings
        self.DEFAULT = '\033[m'
        self.BOLD = '\033[1m'
        # colors
        self.CYAN = '\033[36m'
        self.GREEN = '\033[32m'
        self.MAGENTA = '\033[35m'
        self.RED = '\033[31m'
        self.YELLOW = "\033[33m"
        # bold colors
        self.BOLD_CYAN = '{}{}'.format(self.BOLD, self.CYAN)
        self.BOLD_GREEN = '{}{}'.format(self.BOLD, self.GREEN)
        self.BOLD_MAGENTA = '{}{}'.format(self.BOLD, self.MAGENTA)
        self.BOLD_RED = '{}{}'.format(self.BOLD, self.RED)
        self.BOLD_YELLOW = '{}{}'.format(self.BOLD, self.YELLOW)

    def install_libs(self, data=None):
        """Install Requred Libraries using easy install."""
        # maybe call subprocess for multiple python versions?
        if self._args.config is not None:
            self.install_libs_multiple()
        else:
            self.install_libs_single()

    def install_libs_multiple(self):
        """ """
        file_path = os.path.join(self.app_path, self._args.config)
        if os.path.isfile(file_path):
            with open(file_path, 'r') as fh:
                data = json.load(fh)
            # os.environ['HOME']
            for data in data.get('lib_versions', []):
                print('Building Lib Dir: {}{}{}'.format(
                    self.BOLD_CYAN, data.get('lib_dir'), self.DEFAULT))
                exe_command = [
                    os.path.expanduser(data.get('python_executable')),
                    '-m',
                    'pip',
                    'install',
                    '-r',
                    'requirements.txt',
                    '--ignore-installed',
                    '--quiet',
                    '--target',
                    os.path.join(self.app_path, data.get('lib_dir'))
                ]
                print('Running: {}{}{}'.format(self.BOLD_GREEN, ' '.join(exe_command), self.DEFAULT))
                p = subprocess.Popen(
                    exe_command, shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE)
                out, err = p.communicate()

                if p.returncode != 0:
                    print('FAIL')

    ## def _easy_install(self, app_path, app_name, lib_path):
    ##     """ """
    ##     # install dependencies
    ##     stdout = sys.stdout
    ##     stderr = sys.stderr
    ##     try:
    ##         with open(os.path.join(app_path, '{}-libs.log'.format(app_name)), 'w') as log:
    ##             sys.stdout = log
    ##             sys.stderr = log
    ##             easy_install.main(['-axZ', '-d', lib_path, str(app_path)])
    ##     except SystemExit as e:
    ##         raise Exception(str(e))
    ##     finally:
    ##         sys.stdout = stdout
    ##         sys.stderr = stderr

    def _pip_install(self, app_path, app_name, lib_path):
        """ """
        args = [
            'install',
            '-r',
            'requirements.txt',
            '--ignore-installed',
            '--quiet',
            '--target',
            lib_path
        ]
        command = '{} {}'.format('pip', ' '.join(args))
        print('Running: {}{}{}'.format(self.BOLD_GREEN, command, self.DEFAULT))
        pip.main(args)

    def _make_lib_dir(self, directory):
        """ """
        if not os.path.isdir(directory):
            os.mkdir(directory)

    def install_libs_single(self):
        """ """
        lib_directory = 'lib_{}.{}.{}'.format(
            sys.version_info.major, sys.version_info.minor, sys.version_info.micro)
        print('Creating Lib Directory: {}{}{}'.format(self.BOLD_CYAN, lib_directory, self.DEFAULT))

        # set defaults if no user provide values
        app_path = args.app_path
        if app_path is None:
            app_path = os.getcwd()
        app_name = args.app_name
        if app_name is None:
            app_name = os.path.basename(app_path)

        # build lib path and create if it doesn't exist
        lib_path = os.path.join(app_path, lib_directory)
        self._make_lib_dir(lib_path)

        # update environment for new path
        os.environ['PYTHONPATH'] = '{0}'.format(lib_path)
        # self._easy_install(app_path, app_name, lib_path)
        self._pip_install(app_path, app_name, lib_path)

        if not os.listdir(lib_path):
            err = 'Encountered error running easy_install for {}.  Check log file for details.'
            err = err.format(app_name)
            raise Exception(err)

        # self._cleanup(app_path, app_name, lib_directory)

    ## def _cleanup(self, app_path, app_name, lib_directory):
    ##     """ """
    ##     # cleanup app directory
    ##     files = os.listdir(os.path.join(app_path))
    ##     for file in files:
    ##         remove = False
    ##         if file.endswith('egg-info'):
    ##             remove = True
    ##         elif file == 'build':
    ##             remove = True
    ##         elif file == 'temp':
    ##             remove = True
    ##         elif file == '__pycache__':
    ##             remove = True
    ##
    ##         if remove:
    ##             file_path = os.path.join(app_path, file)
    ##             print('Removing:  {}{}{}'.format(self.BOLD_CYAN, file, self.DEFAULT))
    ##             shutil.rmtree(file_path)
    ##
    ##     # cleanup lib directory
    ##     files = os.listdir(os.path.join(app_path, lib_directory))
    ##     for file in files:
    ##         print('file', file)
    ##         if file.endswith('egg-info'):
    ##             egg_path = os.path.join(app_path, lib_directory, file)
    ##             print('Removing:  {}{}{}'.format(self.BOLD_CYAN, egg_path, self.DEFAULT))
    ##             shutil.rmtree(egg_path)


if __name__ == '__main__':
    try:
        tcl = TcLib(args)
        tcl.install_libs()
        sys.exit(tcl.exit_code)
    except Exception as e:
        # TODO: Update this, possibly raise
        print(traceback.format_exc())
        sys.exit(1)
