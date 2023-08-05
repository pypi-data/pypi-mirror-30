#!/usr/bin/python3
# This file is part of juju-act, a juju plugin to invoke juju actions
# from the command line in a useful way, dealing with the async API
# for you.
#
# Copyright 2015-2018 Canonical Ltd.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3, as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranties of
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import argparse
from distutils.version import LooseVersion
from functools import lru_cache
import json
import os
import subprocess
import sys
from tempfile import NamedTemporaryFile
from textwrap import dedent
import yaml


__version__ = '1.0.1'


class DescriptionAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        parser.exit(0, parser.description.splitlines()[0] + '\n')


class VersionAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        parser.exit(0, __version__ + '\n')


def act_cmd(args=sys.argv[1:]):
    description = dedent("""\
        Run a juju action and display the result.

        This command wraps the builtin run-action and show-action-output
        commands with an interface more usable for interactive use.
        """)
    v20 = has_juju_version('2.0')
    if v20:
        epilog_help = 'juju run-action --help'
    else:
        epilog_help = 'juju action do --help'
    epilog = dedent("""\
        See '{}' for further details about usage.

        Exits with return code 0 if action completed, 1 if the action
        failed.
        """.format(epilog_help))
    parser = argparse.ArgumentParser(description=description, epilog=epilog)
    parser.add_argument('--description', action=DescriptionAction, nargs=0)
    parser.add_argument('--version', action=VersionAction, nargs=0)
    parser.add_argument('unit', metavar='UNIT', type=str,
                        help='Unit to run action on')
    parser.add_argument('action', metavar='ACTION', type=str,
                        help='Action to run')
    parser.add_argument('act_args', metavar='ARGS', type=str, nargs='*',
                        help='Action parameters (overrides --params) '
                             'in key.key.key=value format. The values are '
                             'parsed as yaml, unless --string-args is used')
    if v20:
        parser.add_argument('-m', '--model',
                            metavar="MODEL", type=str, action='store')
    else:
        parser.add_argument('-e', '--environment',
                            metavar="MODEL", type=str, action='store')
    parser.add_argument('--format', metavar='FMT', type=str,
                        action='store', default='yaml',
                        help='Output format (yaml|json)')
    parser.add_argument('-o', '--output', metavar='FILE', type=str,
                        action='store', default=None,
                        help='Specify an output file')
    parser.add_argument('--params', metavar='YAML', type=str,
                        action='store', default=None,
                        help='Path to yaml-formatted params file')
    parser.add_argument('--string-args', default=False, action="store_true",
                        help='Arguments are strings, and not parsed as yaml')
    parser.add_argument('--wait', dest='wait',
                        help='How long to wait for results',
                        action='store', default='0')
    if v20:
        parser.add_argument('-B', '--no-browser-login', default=False,
                            action='store_true',
                            help='Do not use web browser for authentication')

    args = parser.parse_args(args)

    # Run the action
    with NamedTemporaryFile() as outf:
        if v20:
            run_cmd = ['juju', 'run-action', args.unit, args.action,
                       '--format=json', '--output={}'.format(outf.name)]
            if args.model:
                run_cmd.append('--model={}'.format(args.model))
        else:
            run_cmd = ['juju', 'action', 'do', args.unit, args.action,
                       '--format=json', '--output={}'.format(outf.name)]
            if args.environment:
                run_cmd.append('--environment={}'.format(args.environment))

        if args.params:
            run_cmd.append('--params={}'.format(args.params))

        if args.string_args:
            run_cmd.append('--string-args')

        if v20 and args.no_browser_login:
            run_cmd.append('--no-browser-login')

        run_cmd.extend(args.act_args)
        rc = subprocess.call(run_cmd)
        if rc != 0:
            sys.exit(rc)

        m = json.load(open(outf.name, 'r'))
        action_id = list(m.values())[0]

    # Collect the result
    if v20:
        out_cmd = ['juju', 'show-action-output', action_id]
        if args.model:
            out_cmd.append('--model={}'.format(args.model))
    else:
        out_cmd = ['juju', 'action', 'fetch', action_id]
        if args.environment:
            out_cmd.append('--environment={}'.format(args.environment))
    if args.format:
        out_cmd.append('--format={}'.format(args.format))
    # if args.output:
    #    out_cmd.append('--output={}'.format(args.output))
    out_cmd.append('--wait={}'.format(args.wait))
    result = subprocess.check_output(out_cmd, universal_newlines=True)

    # Output
    if args.output:
        try:
            print(result, file=open(args.output, 'w'))
        except Exception:
            print('ERROR: failed to store result of action {} in {}'
                  ''.format(action_id, args.output),
                  file=sys.stderr)
            raise
    else:
        print(result)
    if args.format == 'json':
        m = json.loads(result)
    else:
        m = yaml.safe_load(result)
    if m['status'] == 'completed':
        sys.exit(0)
    elif m['status'] == 'failed':
        sys.exit(1)
    else:
        print('ERROR: Unknown return status {}'.format(m['status']),
              file=sys.stderr)
        sys.exit(99)


def has_juju_version(ver):
    """Return True if the Juju version is the same or later than `ver`"""
    return LooseVersion(juju_version()) >= LooseVersion(ver)


@lru_cache()
def juju_version():
    raw_ver = subprocess.check_output(['juju', '--version'],
                                      universal_newlines=True)
    return raw_ver.strip().split('-', 1)[0]


if __name__ == '__main__':
    # I use these to launch the entry points from the source tree.
    # Most installations will be using the setuptools generated
    # launchers.
    script = os.path.basename(sys.argv[0])
    if script == 'juju-act':
        sys.exit(act_cmd())
    else:
        raise RuntimeError('Unknown script {}'.format(script))
