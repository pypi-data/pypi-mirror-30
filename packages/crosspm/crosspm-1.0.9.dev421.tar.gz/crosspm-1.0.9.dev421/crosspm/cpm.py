#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Usage:
    crosspm download [options]
    crosspm lock [DEPS] [DEPSLOCK] [options]
    crosspm usedby [DEPS] [options]
    crosspm pack <OUT> <SOURCE> [options]
    crosspm cache [size | age | clear [hard]]
    crosspm -h | --help
    crosspm --version

Options:
    <OUT>                                Output file.
    <SOURCE>                             Source directory path.
    -h, --help                           Show this screen.
    --version                            Show version.
    -L, --list                           Do not load packages and its dependencies. Just show what's found.
    -v LEVEL, --verbose=LEVEL            Set output verbosity: ({verb_level}) [default: ].
    -l LOGFILE, --log=LOGFILE            File name for log output. Log level is '{log_default}' if set when verbose doesn't.
    -c FILE, --config=FILE               Path to configuration file.
    -o OPTIONS, --options OPTIONS        Extra options.
    --deps-path=FILE                     Path to file with dependencies [./{deps_default}]
    --dependencies-content=CONTENT       Content for dependencies.txt file
    --dependencies-lock-content=CONTENT  Content for dependencies.txt.lock file
    --depslock-path=FILE                 Path to file with locked dependencies [./{deps_lock_default}]
    --lock-on-success                    Save file with locked dependencies next to original one if download succeeds
    --out-format=TYPE                    Output data format. Available formats:({out_format}) [default: {out_format_default}]
    --output=FILE                        Output file name (required if --out_format is not stdout)
    --output-template=FILE               Template path, e.g. nuget.packages.config.j2 (required if --out_format=jinja)
    --no-fails                           Ignore fails config if possible.
    --recursive                          Process all packages recursively to find and lock all dependencies
    --prefer-local                       Do not search package if exist in cache

"""

import logging
import os
import time

from docopt import docopt

from crosspm import version
from crosspm.helpers.archive import Archive
from crosspm.helpers.config import (
    CROSSPM_DEPENDENCY_LOCK_FILENAME,
    CROSSPM_DEPENDENCY_FILENAME,
    Config,
)
from crosspm.helpers.content import DependenciesContent
from crosspm.helpers.downloader import Downloader
from crosspm.helpers.exceptions import *
from crosspm.helpers.locker import Locker
from crosspm.helpers.output import Output
from crosspm.helpers.python import get_object_from_string
from crosspm.helpers.usedby import Usedby

app_name = 'CrossPM (Cross Package Manager) version: {version} The MIT License (MIT)'.format(version=version)


def do_run(func):
    def wrapper(self, *args, **kwargs):
        try:
            res = func(self, *args, **kwargs)
        except CrosspmExceptionWrongArgs as e:
            print(__doc__)
            return self.exit(e.error_code, e.msg)

        except CrosspmException as e:
            print_stdout('')
            return self.exit(e.error_code, e.msg)

        except Exception as e:
            print_stdout('')
            self._log.exception(e)
            return self.exit(CROSSPM_ERRORCODE_UNKNOWN_ERROR, 'Unknown error occurred!')
        return 0, res

    return wrapper


class CrossPM:
    _ready = False

    def __init__(self, args=None, throw_exceptions=None, return_result=False):
        self._config = None
        self._output = None
        self._return_result = return_result

        if throw_exceptions is None:
            # legacy behavior
            if self._return_result:
                self._throw_exceptions = False
            else:
                self._throw_exceptions = True
        else:
            self._throw_exceptions = throw_exceptions

        self._log = logging.getLogger('crosspm')
        self._args = docopt('{}\n{}'.format(app_name,
                                            __doc__.format(verb_level=Config.get_verbosity_level(),
                                                           log_default=Config.get_verbosity_level(0, True),
                                                           deps_default=CROSSPM_DEPENDENCY_FILENAME,
                                                           deps_lock_default=CROSSPM_DEPENDENCY_LOCK_FILENAME,
                                                           out_format=Output.get_output_types(),
                                                           out_format_default='stdout',
                                                           ),
                                            ),
                            argv=args,
                            version=version)

        if isinstance(self._args, str):
            if self._throw_exceptions:
                print(app_name)
                print(self._args)
                exit()

        self._ready = True

    @do_run
    def read_config(self):
        _deps_path = self._args['--deps-path']
        # Передаём содержимое напрямую
        if _deps_path is None and self._args['--dependencies-content'] is not None:
            _deps_path = DependenciesContent(self._args['--dependencies-content'])
        _depslock_path = self._args['--depslock-path']
        if _depslock_path is None and self._args['--dependencies-lock-content'] is not None:
            _depslock_path = DependenciesContent(self._args['--dependencies-lock-content'])
        if self._args['lock']:
            if self._args['DEPS']:
                _deps_path = self._args['DEPS']
            if self._args['DEPSLOCK']:
                _depslock_path = self._args['DEPSLOCK']
        self._config = Config(self._args['--config'], self._args['--options'], self._args['--no-fails'], _depslock_path,
                              _deps_path, self._args['--lock-on-success'], self._args['--recursive'],
                              self._args['--prefer-local'])
        self._output = Output(self._config.output('result', None), self._config.name_column, self._config)

    def exit(self, code, msg):
        self._log.critical(msg)
        if self._throw_exceptions:
            sys.exit(code)
        else:
            return code, msg

    @do_run
    def check_common_args(self):
        if self._args['--output']:
            output = self._args['--output'].strip().strip("'").strip('"')
            output_abs = os.path.abspath(output)
            if os.path.isdir(output_abs):
                raise CrosspmExceptionWrongArgs(
                    '"%s" is a directory - can\'t write to it'
                )
            self._args['--output'] = output

    @do_run
    def set_logging_level(self):
        level_str = self._args['--verbose'].strip().lower()

        log = self._args['--log']
        if log:
            log = log.strip().strip("'").strip('"')
            log_abs = os.path.abspath(log)
            if os.path.isdir(log_abs):
                raise CrosspmExceptionWrongArgs(
                    '"%s" is a directory - can\'t write log to it'
                )
            else:
                log_dir = os.path.dirname(log_abs)
                if not os.path.exists(log_dir):
                    os.makedirs(log_dir)
        else:
            log_abs = None

        level = Config.get_verbosity_level(level_str or 'console')
        self._log.handlers = []
        if level or log_abs:
            self._log.setLevel(level)
            format_str = '%(asctime)-19s [%(levelname)-9s] %(message)s'
            if level_str == 'debug':
                format_str = '%(asctime)-19s [%(levelname)-9s] %(name)-12s: %(message)s'
            formatter = logging.Formatter(format_str, datefmt="%Y-%m-%d %H:%M:%S")

            if level:
                sh = logging.StreamHandler(stream=sys.stderr)
                sh.setLevel(level)
                # sh.setFormatter(formatter)
                self._log.addHandler(sh)

            if log_abs:
                if not level_str:
                    level = Config.get_verbosity_level(0)
                fh = logging.FileHandler(filename=log_abs)
                fh.setLevel(level)
                fh.setFormatter(formatter)
                self._log.addHandler(fh)

    def run(self):
        time_start = time.time()
        if self._ready:

            errorcode, msg = self.set_logging_level()
            self._log.info(app_name)
            errorcode, msg = self.check_common_args()
            if errorcode == 0:
                errorcode, msg = self.read_config()

                if errorcode == 0:
                    if self._args['download']:
                        errorcode, msg = self.command(Downloader)
                        # self.command()

                    elif self._args['lock']:
                        errorcode, msg = self.command(Locker)

                    elif self._args['usedby']:
                        errorcode, msg = self.command(Usedby)

                    elif self._args['pack']:
                        errorcode, msg = self.pack()

                    elif self._args['cache']:
                        errorcode, msg = self.cache()
        else:
            errorcode, msg = CROSSPM_ERRORCODE_WRONG_ARGS, self._args
        time_end = time.time()
        self._log.info('Done in %2.2f sec' % (time_end - time_start))
        return errorcode, msg

    @do_run
    def command(self, command_):
        if self._return_result:
            params = {}
        else:
            if self._args['--out-format'] == 'stdout':
                if self._args['--output']:
                    raise CrosspmExceptionWrongArgs(
                        "unwanted argument '--output' while argument '--out-format={}'".format(
                            self._args['--out-format'],
                        ))
            elif not self._args['--output']:
                raise CrosspmExceptionWrongArgs(
                    "argument '--output' required when argument '--out-format={}'".format(
                        self._args['--out-format'],
                    ))

            params = {
                'out_format': ['--out-format', ''],
                'output': ['--output', ''],
                'output_template': ['--output-template', ''],
                # 'out_prefix': ['--out-prefix', ''],
                # 'depslock_path': ['--depslock-path', ''],
            }

            for k, v in params.items():
                params[k] = self._args[v[0]] if v[0] in self._args else v[1]
                if isinstance(params[k], str):
                    params[k] = params[k].strip('"').strip("'")

            # try to dynamic load --output-template from python module
            output_template = params['output_template']
            if output_template:
                # Try to load from python module
                module_template = get_object_from_string(output_template)
                if module_template is not None:
                    self._log.debug(
                        "Found output template path '{}' from '{}'".format(module_template, output_template))
                    params['output_template'] = module_template
                else:
                    self._log.debug("Output template '{}' use like file path".format(output_template))

            # check template exist
            output_template = params['output_template']
            if output_template and not os.path.exists(output_template):
                raise CrosspmException(CROSSPM_ERRORCODE_CONFIG_NOT_FOUND,
                                       "Can not find template '{}'".format(output_template))

        do_load = not self._args['--list']
        # hack for Locker
        if command_ is Locker:
            do_load = self._config.recursive

        # if do_load:
        #     self._config.cache.auto_clear()
        cpm_ = command_(self._config, do_load)
        cpm_.entrypoint()

        if self._return_result:
            return self._return(cpm_)
        else:
            # self._output.write(params, packages)
            self._output.write_output(params, cpm_.get_tree_packages())
        return ''

    def _return(self, cpm_downloader):
        if str(self._return_result).lower() == 'raw':
            return cpm_downloader.get_raw_packages()
        if str(self._return_result).lower() == 'tree':
            return cpm_downloader.get_tree_packages()
        else:
            return self._output.output_type_module(cpm_downloader.get_tree_packages())

    @do_run
    def pack(self):
        Archive.create(self._args['<OUT>'], self._args['<SOURCE>'])

    @do_run
    def cache(self):
        if self._args['clear']:
            self._config.cache.clear(self._args['hard'])
        elif self._args['size']:
            self._config.cache.size()
        elif self._args['age']:
            self._config.cache.age()
        else:
            self._config.cache.info()


if __name__ == '__main__':
    app = CrossPM()
    app.run()
