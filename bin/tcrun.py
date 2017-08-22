#!/usr/bin/env python

""" standard """
import argparse
import json
import os
import re
import shutil
import sys
import subprocess
import tempfile
import time
import traceback
""" third-party """
""" custom """


parser = argparse.ArgumentParser()
parser.add_argument(
    '--config', default='tcex.json', help='The configuration file. (default: "tcex.json")')
parser.add_argument(
    '--halt_on_fail', action='store_true', help='Halt on any failure.')
parser.add_argument(
    '--group', default=None, help='The group of profiles to executed.')
parser.add_argument(
    '--profile', default='default', help='The profile to be executed. (default: "default")')
parser.add_argument(
    '--quiet', action='store_true', help='Suppress output.')
parser.add_argument(
    '--unmask', action='store_true', help='Unmask masked args.')
args, extra_args = parser.parse_known_args()


# TODO: Clean this up when time allows
class TcRun(object):
    def __init__(self, args):
        """ """
        self._args = args
        self.app_path = os.getcwd()
        self.config = {}
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

    def _load_config(self):
        """Load the configuration file."""
        if not os.path.isfile(self._args.config):
            msg = 'Provided config file does not exist ({}).'.format(self._args.config)
            sys.exit(msg)

        print('Configuration File: {}{}{}'.format(
            self.BOLD_CYAN, args.config, self.DEFAULT))
        with open(self._args.config) as data_file:
            config = json.load(data_file)

        # load includes
        for directory in config.get('profile_include_dirs', []):
            config.setdefault('profiles', []).extend(self._load_config_include(directory))

        self.config = config

    def _load_config_include(self, include_directory):
        """Load included configuration files."""
        include_directory = os.path.join(self.app_path, include_directory)
        if not os.path.isdir(include_directory):
            msg = 'Provided include directory does not exist ({}).'.format(include_directory)
            sys.exit(msg)

        profiles = []
        for file in sorted(os.listdir(include_directory)):
            if file.endswith('.json'):
                print('Include File: {}{}{}'.format(
                    self.BOLD_CYAN, file, self.DEFAULT))
                config_file = os.path.join(include_directory, file)
                with open(config_file) as data_file:
                    try:
                        profiles.extend(json.load(data_file))
                    except ValueError as e:
                        print('Invalid JSON file {}({}){}.'.format(
                            self.BOLD_RED, e, self.DEFAULT))
                        sys.exit(1)

        return profiles

    def _parameters(self, args):
        """Build CLI arguments to pass to script on the command line.

        This method takes the json data and covert it to CLI args for the execution
        of the script.

        Returns:
            (dict): A dictionary that should be converted to CLI Args
        """
        parameters = []
        parameters_masked = []
        for config_key, config_val in args.items():
            if isinstance(config_val, bool):
                if config_val:
                    parameters.append('--{}'.format(config_key))
                    parameters_masked.append('--{}'.format(config_key))
            elif isinstance(config_val, list):
                # TODO: support env vars in list w/masked values
                for val in config_val:
                    parameters.append('--{}'.format(config_key))
                    parameters_masked.append('--{}'.format(config_key))
                    # val
                    parameters.append('{}'.format(val))
                    parameters_masked.append('{}'.format(self.quoted(val)))
            elif isinstance(config_val, dict):
                msg = 'Error: Dictionary types are not currently supported for field {}'
                msg.format(config_val)
                self._exit(msg, 1)
            else:
                mask = False
                env_var = re.compile(r'^\$env\.(.*)$')
                envs_var = re.compile(r'^\$envs\.(.*)$')

                if env_var.match(str(config_val)):
                    # read value from environment variable
                    env_key = env_var.match(str(config_val)).groups()[0]
                    config_val = os.environ.get(env_key, config_val)
                elif envs_var.match(str(config_val)):
                    # read secure value from environment variable
                    env_key = envs_var.match(str(config_val)).groups()[0]
                    config_val = os.environ.get(env_key, config_val)
                    mask = True

                parameters.append('--{}'.format(config_key))
                parameters_masked.append('--{}'.format(config_key))
                parameters.append('{}'.format(config_val))
                if mask and not self._args.unmask:
                    config_val = 'x' * len(str(config_val))
                    parameters_masked.append('{}'.format(self.quoted(config_val)))
                else:
                    parameters_masked.append('{}'.format(self.quoted(config_val)))
        return {
            'masked': parameters_masked,
            'unmasked': parameters
        }

    def data_args(self, args):
        """Get just the args required for data services"""
        return {
            'api_access_id': args.get('api_access_id'),
            'api_secret_key': args.get('api_secret_key'),
            # 'logging': 'info',
            'logging': args.get('logging'),
            'tc_api_path': args.get('tc_api_path'),
            'tc_log_file': 'data.log',
            'tc_log_path': args.get('tc_log_path'),
            'tc_out_path': args.get('tc_out_path'),
            'tc_playbook_db_context': args.get('tc_playbook_db_context'),
            'tc_playbook_db_path': args.get('tc_playbook_db_path'),
            'tc_playbook_db_port': args.get('tc_playbook_db_port'),
            'tc_playbook_db_type': args.get('tc_playbook_db_type'),
            'tc_temp_path': args.get('tc_temp_path')
        }

    def stage_data(self, profile):
        """Stage any required data."""

        args = self.data_args(profile.get('args'))
        parameters = self._parameters(args)

        for file in profile.get('data_files', []):
            if os.path.isfile(file):
                print('Staging Data: {}{}{}'.format(
                    self.BOLD_CYAN, file, self.DEFAULT))
                fqfp = os.path.join(self.app_path, file)

                command = [
                    'tcdata.py',
                    '--data_file',
                    file
                ]
                # print_command = ' '.join(command + parameters.get('masked'))
                # print(print_command)

                exe_command = command + parameters.get('unmasked')
                p = subprocess.Popen(
                    exe_command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                out, err = p.communicate()

                if p.returncode != 0:
                    print('{}Failed to stage data for file {}{}.'.format(
                        self.BOLD_RED, file, self.DEFAULT))
                    sys.exit(p.returncode)
            else:
                print('{}Could not find file {}{}.'.format(
                    self.BOLD_RED, file, self.DEFAULT))
                sys.exit(1)

    def validate_data(self, profile):
        """Stage any required data."""

        args = self.data_args(profile.get('args'))
        parameters = self._parameters(args)

        v_data = profile.get('validations', [])
        if v_data:
            variables = ', '.join([d.get('variable') for d in v_data])
            print('Validating Variables: {}{}{}'.format(
                self.BOLD_CYAN, variables, self.DEFAULT))
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
                f.write(json.dumps(v_data))
                f.flush()

            command = [
                'tcdata.py',
                '--data_file',
                f.name,
                '--validate'
            ]
            # print_command = ' '.join(command + parameters.get('masked'))
            # print(print_command)

            exe_command = command + parameters.get('unmasked')
            p = subprocess.Popen(
                exe_command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = p.communicate()

            if p.returncode != 0:
                print('{}Failed variable validation{}.'.format(
                    self.BOLD_RED, self.DEFAULT))
                sys.exit(p.returncode)

            # cleanup temp file
            if os.path.isfile(f.name):
                os.remove(f.name)

    def _create_tc_dirs(self, profile):
        """Create app directories for logs and data files."""
        tc_log_path = profile.get('args', {}).get('tc_log_path')
        if tc_log_path is not None and not os.path.isdir(tc_log_path):
            os.makedirs(tc_log_path)
        tc_out_path = profile.get('args', {}).get('tc_out_path')
        if tc_out_path is not None and not os.path.isdir(tc_out_path):
            os.makedirs(tc_out_path)
        tc_tmp_path = profile.get('args', {}).get('tc_tmp_path')
        if tc_tmp_path is not None and not os.path.isdir(tc_tmp_path):
            os.makedirs(tc_tmp_path)

    def run(self):
        """Run the App using the defined config."""

        # load tc config
        self._load_config()

        # get all selected profiles
        selected_profiles = []
        for config in self.config.get('profiles'):
            if config.get('profile_name') == self._args.profile:
                selected_profiles.append(config)
            elif config.get('group') is not None and config.get('group') == self._args.group:
                selected_profiles.append(config)

        if len(selected_profiles) == 0:
            print('{}No profiles selected to run.{}'.format(
                self.BOLD_YELLOW, self.DEFAULT))

        command_count = 0
        ## status_code = 0
        first = True
        reports = []
        for sp in selected_profiles:
            # create temp directories
            self._create_tc_dirs(sp)

            passed = False
            #
            # Sleep between executions
            #
            if not first:
                sleep = sp.get('sleep', self.config.get('sleep', 1))
                time.sleep(sleep)
                print('Sleep: {}{} seconds{}'.format(
                    self.BOLD_CYAN, sleep, self.DEFAULT))
                first = False

            #
            # Profile
            #
            print('Profile: {}{}{}'.format(
                self.BOLD_CYAN, sp.get('profile_name'), self.DEFAULT))
            if sp.get('description'):
                print('Description: {}{}{}'.format(
                    self.BOLD_MAGENTA, sp.get('description'), self.DEFAULT))
            command_count += 1

            # get script name
            script = sp.get('script')
            script_py = sp.get('script')
            if not script_py.endswith('.py'):
                script_py = '{}.py'.format(script_py)

            if script is None or not os.path.isfile(script_py):
                sys.exit('Could not find script ({}).'.format(script_py))
            #
            # Build Command
            #
            command = [
                # self._args.python,
                sys.executable,
                '.',
                script.replace('.py', ''),
            ]
            parameters = self._parameters(sp.get('args'))
            exe_command = command + parameters.get('unmasked')

            #
            # Stage Data
            #
            self.stage_data(sp)

            # output command
            print_command = ' '.join(command + parameters.get('masked'))
            print('Executing: {}{}{}'.format(
                self.BOLD_GREEN, print_command, self.DEFAULT))

            #
            # Run Command
            #
            p = subprocess.Popen(
                exe_command, shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = p.communicate()

            #
            # Logs
            #
            # log_directory = os.path.join(self.app_path, sp.get('args').get('tc_log_path'))
            # for log_file in os.listdir(log_directory):
            #     log_file = os.path.join(log_directory, log_file)
            #     print('Logs: {}{}{}'.format(
            #         self.BOLD_CYAN, log_file, self.DEFAULT))

            #
            # Exit Code
            #
            valid_exit_codes = sp.get('exit_codes', [0])
            if p.returncode in valid_exit_codes:
                print('App Exit Code: {}{}{}'.format(
                    self.BOLD_GREEN, p.returncode, self.DEFAULT))
                passed = True
            else:
                print('App Exit Code: {}{}{} (Valid Exit Codes:{}).'.format(
                    self.BOLD_RED, p.returncode, self.DEFAULT, valid_exit_codes))
                self.exit_code = 1
                if args.halt_on_fail:
                    break

            #
            # Validate Data
            #
            self.validate_data(sp)

            # divider
            print('{}{}{}'.format(self.BOLD, '-' * 100, self.DEFAULT))

            #
            # Script Output
            #
            if not sp.get('quiet') and not self._args.quiet:
                print(self.to_string(out, 'ignore'))

            #
            # Error Output
            #
            if len(err) != 0:
                print(err.decode('utf-8'))

            reports.append({
                'profile': sp.get('profile_name'),
                'passed': passed
            })

        #
        # Report
        #
        if (reports):
            self.report(reports)

    def report(self, data):
        """Format and output report data."""
        print('{}{}{}'.format(self.BOLD_CYAN, 'Reports:', self.DEFAULT))
        for d in data:
            profile = d.get('profile')
            passed = d.get('passed')
            if passed:
                passed_out = '{}{}{}'.format(self.BOLD_GREEN, 'Passed', self.DEFAULT)
            else:
                passed_out = '{}{}{}'.format(self.BOLD_RED, 'Failed', self.DEFAULT)
            print('{0!s:<80}{1!s:<30}'.format(profile, passed_out))


    @staticmethod
    def to_string(data, errors='strict'):
        """Covert x to string in Python 2/3

        Args:
            data (any): Data to ve validated and re-encoded

        Returns:
            (any): Return validate or encoded data

        """
        # TODO: Find better way using six or unicode_literals
        if isinstance(data, (bytes, str)):
            try:
                data = unicode(data, 'utf-8', errors=errors)  # 2to3 converts unicode to str
            except NameError:
                data = str(data, 'utf-8', errors=errors)
        return data

    @staticmethod
    def quoted(data):
        """Quote any parameters that contain spaces or special character

        Returns:
            (string): String containing parameters wrapped in double quotes
        """
        if len(re.findall(r'[!\-\s\$]{1,}', str(data))) > 0:
            data = '\'{}\''.format(data)
        return data


if __name__ == '__main__':
    try:
        tcr = TcRun(args)
        tcr.run()
        sys.exit(tcr.exit_code)
    except Exception as e:
        # TODO: Update this, possibly raise
        print(traceback.format_exc())
        sys.exit(1)