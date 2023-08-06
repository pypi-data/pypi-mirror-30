#
# Copyright 2017 The E2C Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

from typing import Callable
from typing import Dict
from typing import Generic
from typing import List
from typing import Tuple
from typing import TypeVar

from e2c.actor import Actor
from e2c.analyser import Analyser
from e2c.const import *
from e2c.errors import *
from e2c.parser import Parser
from e2c.visualizer import Visualizer

Request = TypeVar('Request')
Response = TypeVar('Response')


# ======================================================= #
# RESULT
# ======================================================= #


class Result(object):
    """ The result class to represents the result.
    """

    def __init__(self):
        self.value = None
        self.value_callback = None

    def set(self, data: object) -> None:
        """
        The method to set the value.

        :type data: object
        :param data: Any data.
        :rtype: None
        """
        if self.value_callback:
            self.value_callback(data)
        else:
            self.value = data


# ======================================================= #
# BASE GRAPH
# ======================================================= #


class BaseGraph(Generic[Request, Response]):
    """ 
    The core graph brings all components together.
    """

    def __init__(self,
                 actors: Dict[str, Actor],
                 analyser: Analyser or None,
                 parser: Parser or None,
                 visualiser: Visualizer or None,
                 script: List[str] = None):
        """
        Creates a new graph.

        :type actors: `Dict[str, Actor]`
        :param actors: The actors to work with.

        :type analyser: `e2c.analyser.Analyser`
        :param analyser: A instance of the analyser.

        :type parser: `e2c.parser.Parser`
        :param parser: A instance of the parser.

        :type visualiser: `e2c.visualiser.Visualiser`
        :param visualiser: A instance of the visualiser.

        :type script: List[str]
        :param script: The string list of the graph to parse.
        """
        self.name = DEFAULT
        self._analyser = analyser
        self._parser = parser
        self._visualizer = visualiser
        self._result = Result()
        self._tracer = None
        self._end = None
        self._actors = actors
        self.actor(SELF, self._process)
        self.actor(OUT, self._result.set)
        self.activate_trace = True
        if script:
            self.parse_graph(script)

    def _process(
            self,
            request: Request,
            run: Callable,
            end: Callable = None,
            err: Callable = None,
            trace: Callable = None) -> None:
        """
        The method to start the first actor after call 'run'.

        :type request: 'Request'
        :param request: The data to be transmitted.

        :type run: Callable
        :param run: The run function.

        :type end: Callable
        :param end: The end function.

        :type err: Callable
        :param err: The error function.

        :type trace: Callable
        :param trace: The trace function.

        :rtype: None
        """
        try:
            self._tracer = trace
            self._end = end
            if not run:
                raise E2CGraphError(
                    'Missing .{} -- ? in graph!'.format(RUN))
            run(request)
        except Exception as exc:
            if not err: raise exc
            err(exc)

    def on_trace(self, name: str) -> None:
        """
        The method to track the trace path.

        :type name: str
        :param name: The name of the running actor.
        :rtype: None
        """
        if self._tracer:
            try:
                # deactivate trace in tracing process
                # to avoid recursion
                self.activate_trace = False
                if name != OUT:
                    self._tracer(name)
            finally:
                self.activate_trace = True

    def actor(self, name: str, callable: Callable) -> None:
        """
        Registers a new actor by specified name and the callable function or method or class.

        :type name: str
        :param name: The name under which the function can be called..

        :type callable: Callable
        :param callable: The callable function or method or class.

        :rtype: None
        """
        if name in self._actors and self._actors[name].callable:
            raise E2CGraphError(
                'Actor {} was already registered!'.format(name))
        if name not in self._actors:
            self._actors[name] = Actor(self, name, None)
        self._actors[name].callable = callable

    def analyse(self, quiet=True) -> None:
        """
        Starts the analyser.

        :type quiet: bool
        :param quiet: True to print out messages.
        :rtype: None
        """
        self._analyser.run(quiet)

    def visualize(self, folder: str = None) -> None:
        """
        Starts the visualiser.

        :type folder: str
        :param folder: The directory where the graph is written.

        :rtype: None
        """
        self._visualizer.run(folder, self.name)

    def configure(self, file_name: str) -> None:
        """
        Opens the specified file and builds up the graph.

        :type  file_name: str
        :param file_name: The filename to load from file.

        :rtype: None
        """
        try:
            with open(file_name, 'r') as f:
                self.parse_graph(f.readlines())
        except Exception as exc:
            raise E2CGraphError(exc)

    def parse_graph(self, script: List[str]) -> None:
        """ 
        Parses the script and builds the graph.

        :type script: List[str]
        :param script: The script to parse.

        :rtype: None
        """

        def set_name(name: str) -> None:
            self.name = name

        self._parser.run(script, set_name)

    def run(self, request: Request = None, actor: str = None) -> Response:
        """
        Runs the graph and returns the return value.

        :type request: Request
        :param request: The data to be transmitted

        :type actor: str
        :param actor: The optional name of the actor to start.

        :rtype: Response
        :return: The return value.
        """
        self.analyse(True)
        if not actor:
            self._actors[SELF].run(request)
        else:
            if actor not in self._actors:
                raise E2CGraphError(
                    '{} is not a registered actor!'.format(actor))
            runner = self._actors[SELF].clone()
            runner.actors[RUN].clear()
            runner.on(RUN, self._actors[actor])
            runner.run(request)
        if self._end:
            self._end._actor.run(request)
        return self._result.value

    def run_continues(
            self, request: Request = None,
            result: Callable[[Response], None] = None, actor: str = None) -> None:
        """
        Runs the graph and calls a result callback.

        :type request: Request
        :param request: The data to be transmitted.

        :type result: Callable[[Response], None]
        :param result: The result callback.

        :type actor: str
        :param actor: The optional name of the actor to start.

        :rtype: None
        """
        self._result.value_callback = result
        self.run(request, actor)


# ======================================================= #
# GRAPH
# ======================================================= #


class Graph(Generic[Request, Response], BaseGraph[Request, Response]):
    """
    A class for running E2C operations.
    A `Graph` object encapsulates the environment in which `Actor`
    objects are executed.
    """

    def __init__(self, script: Tuple[str] or List[str] = None):
        """
        A class for running E2C operations.

        :type script: Tuple[str] or List[str]
        :param script: The script to builds the graph.
        """
        actors: Dict[str, Actor] = {}

        super(Graph, self).__init__(
            actors,
            Analyser(actors),
            Parser(actors, lambda name: Actor(self, name, None)),
            Visualizer(actors),
            script)
