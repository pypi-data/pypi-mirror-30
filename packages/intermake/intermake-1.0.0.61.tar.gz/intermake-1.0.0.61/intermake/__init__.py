"""
intermake package entry-point.
See `readme.md` for details.
"""
import intermake.init
from intermake.engine.host_manager import RunHost
from intermake.engine.async_result import Result
from intermake.engine.environment import start, MENV, MCMD, register, run_jupyter
from intermake.engine.plugin_manager import PluginManager
from intermake.engine.progress_reporter import ActionHandler, IProgressReceiver, QueryInfo, TaskCancelledError, UpdateInfo, Message
from intermake.helpers import coercion_extensions
from intermake.helpers.coercion_extensions import VISUALISABLE_COERCION
from intermake.helpers.table_draw import Table
from intermake.hosts.base import ResultsExplorer, ERunMode, PluginHost
from intermake.hosts.console import ConsoleHost
from intermake.plugins.command_plugin import command, CommandPlugin, help_command
from intermake.engine.constants import EThread, EStream, EDisplay
from intermake.plugins.setter_plugin import SetterPlugin, setter_command
from intermake.engine import cli_helper, theme, constants, environment, constants
from intermake.engine.plugin import Plugin
from intermake.engine.mandate import Mandate
from intermake.engine.theme import Theme
from intermake.plugins import visibilities, command_plugin, common_commands, console_explorer, setter_plugin, test_plugins
from intermake.plugins.visibilities import VisibilityClass
from intermake.visualisables.visualisable import EColour, IVisualisable, UiInfo, NamedValue, as_visualisable, VisualisablePath
from intermake.helpers import subprocess_helper
from intermake.visualisables import visualisable

__author__ = "Martin Rusilowicz"
__version__ = "1.0.0.61"
