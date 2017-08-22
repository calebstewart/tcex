#!/usr/bin/env python

""" standard """
import argparse
import json
import os
import sys
from uuid import uuid4
from collections import OrderedDict
from random import randint
""" third-party """
""" custom """

parser = argparse.ArgumentParser()
parser.add_argument(
    '--config', default='install.json', help='The configuration file. (default: "install.json")')
parser.add_argument(
    '--outfile', help='File to output or append data.')
args, extra_args = parser.parse_known_args()

# colors
# color settings
DEFAULT = '\033[m'
BOLD = '\033[1m'
# colors
CYAN = '\033[36m'
GREEN = '\033[32m'
MAGENTA = '\033[35m'
RED = '\033[31m'
YELLOW = "\033[33m"
# bold colors
BOLD_CYAN = '{}{}'.format(BOLD, CYAN)
BOLD_GREEN = '{}{}'.format(BOLD, GREEN)
BOLD_MAGENTA = '{}{}'.format(BOLD, MAGENTA)
BOLD_RED = '{}{}'.format(BOLD, RED)
BOLD_YELLOW = '{}{}'.format(BOLD, YELLOW)


def main():
    """ """
    if not os.path.isfile(args.config):
        print('{}Configuration file ({}) could not be found.{}'.format(
            BOLD_RED, args.config, DEFAULT))

    with open(args.config) as fh:
        data = json.load(fh)

    #
    # args
    #
    config_args = OrderedDict()
    config_args['api_access_id'] = '$env.API_ACCESS_ID'
    config_args['api_secret_key'] = '$envs.API_SECRET_KEY'
    config_args['logging'] = 'debug'
    config_args['tc_api_path'] = '$env.TC_API_PATH'
    config_args['tc_log_path'] = 'log'
    config_args['tc_log_to_api'] = False
    config_args['tc_out_path'] = 'log'
    config_args['tc_temp_path'] = 'log'
    config_args['tc_playbook_db_type'] = 'Redis'
    config_args['tc_playbook_db_context'] = str(uuid4())
    config_args['tc_playbook_db_path'] = 'localhost'
    config_args['tc_playbook_db_port'] = '6379'
    config_args['tc_playbook_out_variables'] = ''

    for d in data.get('params', []):
        if d.get('type') == 'Boolean':
            config_args[d.get('name')] = d.get('default', False)
        # elif d.get('type') in ['StringArray', 'TCEntityArray']':
        #     config['args'][d.name] = []
        else:
           config_args[d.get('name')] = d.get('default', '')

    #
    # config
    #
    profile_name = data.get('displayName', '').lower().replace(' ', '-')
    if len(profile_name) == 0:
        profile_name = args.config.replace('.install.json', '').lower()
    print('Building Profile: {}{}{}'.format(BOLD_CYAN, profile_name, DEFAULT))

    config = OrderedDict()
    config['args'] = config_args
    config['description'] = ''
    config['exit_code'] = [0]
    config['group'] = 'qa-build'
    config['profile_name'] = profile_name
    config['quiet'] = False
    config['script'] = data.get('programMain')

    #
    # playbook validation
    #
    if data.get('runtimeLevel') == 'Playbook':
        validations = []
        output_variables = []
        job_id = randint(0,9999)
        for d in data.get('playbook', {}).get('outputVariables', []):
            variable = '#App:{:04d}:{}!{}'.format(job_id, d.get('name'), d.get('type'))
            output_variables.append(variable)

            # null check
            od = OrderedDict()
            if d.get('type').endswith('Array'):
                od['data'] = [None, []]
                od['operator'] = 'ni'
            else:
                od['data'] = None
                od['operator'] = 'ne'
            od['variable'] = variable
            validations.append(od)

            # type check
            od = OrderedDict()
            if d.get('type').endswith('Array'):
                od['data'] = 'array'
                od['operator'] = 'it'
            elif d.get('type').endswith('Entity') or d.get('type') == 'KeyValue':
                od['data'] = 'entity'
                od['operator'] = 'it'
            else:
                od['data'] = 'string'
                od['operator'] = 'it'
            od['variable'] = variable
            validations.append(od)

        config['validations'] = validations
        config['args']['tc_playbook_out_variables'] = '{}'.format(','.join(output_variables))

    if args.outfile is not None:
        if os.path.isfile(args.outfile):
            # append
            print('Append to File: {}{}{}'.format(BOLD_CYAN, args.outfile, DEFAULT))
            with open(args.outfile, 'r+') as fh:
                try:
                    data = json.load(fh, object_pairs_hook=OrderedDict)
                except ValueError as e:
                    err = '{}Can not parse JSON data ({}).{}'.format(BOLD_RED, e, DEFAULT)
                    print(err)
                    sys.exit(1)
                # update data
                if isinstance(data, (dict)) and data.get('profiles') is not None:
                    data['profiles'].append(config)
                else:
                    data.append(config)
                fh.seek(0)
                fh.write(json.dumps(data, indent=2))
                fh.truncate()
        else:
            # create
            print('Create File: {}{}{}'.format(BOLD_CYAN, args.outfile, DEFAULT))
            with open(args.outfile, 'w') as fh:
                data = [config]
                fh.write(json.dumps(data, indent=2))
    else:
        print(json.dumps(config, indent=2))


if __name__ == '__main__':
    main()

