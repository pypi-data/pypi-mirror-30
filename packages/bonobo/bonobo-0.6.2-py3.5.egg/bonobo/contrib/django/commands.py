from logging import getLogger
from types import GeneratorType

import bonobo
from bonobo.plugins.console import ConsoleOutputPlugin
from bonobo.util.term import CLEAR_EOL
from colorama import Fore, Back, Style
from django.core.management import BaseCommand
from django.core.management.base import OutputWrapper
from mondrian import term

from .utils import create_or_update


class ETLCommand(BaseCommand):
    @property
    def logger(self):
        try:
            return self._logger
        except AttributeError:
            self._logger = getLogger(type(self).__module__)
            return self._logger

    create_or_update = staticmethod(create_or_update)

    def create_parser(self, prog_name, subcommand):
        return bonobo.get_argument_parser(super().create_parser(prog_name, subcommand))

    def add_arguments(self, parser):
        """
        Entry point for subclassed commands to add custom arguments.
        """
        pass

    def get_graph(self, *args, **options):
        def not_implemented():
            raise NotImplementedError('You must implement {}.get_graph() method.'.format(self))

        return bonobo.Graph(not_implemented)

    def get_services(self):
        return {}

    def info(self, *args, **kwargs):
        self.logger.info(*args, **kwargs)

    def handle(self, *args, **options):
        _stdout_backup, _stderr_backup = self.stdout, self.stderr

        self.stdout = OutputWrapper(ConsoleOutputPlugin._stdout, ending=CLEAR_EOL + '\n')
        self.stderr = OutputWrapper(ConsoleOutputPlugin._stderr, ending=CLEAR_EOL + '\n')
        self.stderr.style_func = lambda x: Fore.LIGHTRED_EX + Back.RED + '!' + Style.RESET_ALL + ' ' + x

        with bonobo.parse_args(options) as options:
            services = self.get_services()
            graph_coll = self.get_graph(*args, **options)

            if not isinstance(graph_coll, GeneratorType):
                graph_coll = (graph_coll, )

            for i, graph in enumerate(graph_coll):
                assert isinstance(graph, bonobo.Graph), 'Invalid graph provided.'
                print(term.lightwhite('{}. {}'.format(i + 1, graph.name)))
                result = bonobo.run(graph, services=services)
                print(term.lightblack(' ... return value: ' + str(result)))
                print()

        self.stdout, self.stderr = _stdout_backup, _stderr_backup
