from typing import Callable
from colorama import Back, Fore, Style
from enum import Enum

from mhelper import MEnum


__author__ = "Martin Rusilowicz"

DEFAULT_NAME = "intermake"

PLUGIN_TYPE_COMMAND = "command"
EXPLORER_KEY_PLUGINS = "Plugins"
EXPLORER_KEY_RESULTS = "Results"
VIRTUAL_FOLDER = "SPECIAL"

RES_FOLDER = "folder"
RES_UNKNOWN = "unknown"
RES_COMMAND = "command"

INFOLINE_MESSAGE = Back.GREEN + Fore.WHITE + "MSG" + Style.RESET_ALL + " "
INFOLINE_ERROR = Back.RED + Fore.WHITE + "ERR" + Style.RESET_ALL + " "
INFOLINE_WARNING = Back.YELLOW + Fore.RED + "WRN" + Style.RESET_ALL + " "
INFOLINE_INFORMATION = Back.BLUE + Fore.WHITE + "INF" + Style.RESET_ALL + " "
INFOLINE_PROGRESS = Back.GREEN + Fore.BLUE + "PRG" + Style.RESET_ALL + " "
INFOLINE_ECHO = Fore.BLACK + Back.CYAN + Style.DIM + "ECO" + Style.RESET_ALL + " "
INFOLINE_SYSTEM = Back.YELLOW + Fore.WHITE + "SYS" + Style.RESET_ALL + " "
INFOLINE_EXTERNAL_STDOUT = Back.WHITE + Fore.BLUE + "APP" + Style.RESET_ALL + " "
INFOLINE_EXTERNAL_STDERR = Back.WHITE + Fore.RED + "APE" + Style.RESET_ALL + " "
INFOLINE_VERBOSE = Back.BLUE + Fore.CYAN + "VER" + Style.RESET_ALL + " "

INFOLINE_MESSAGE_CONTINUED = Back.GREEN + Fore.WHITE + "   " + Style.RESET_ALL + " "
INFOLINE_WARNING_CONTINUED = Back.YELLOW + Fore.RED + "   " + Style.RESET_ALL + " "
INFOLINE_INFORMATION_CONTINUED = Back.BLUE + Fore.WHITE + "   " + Style.RESET_ALL + " "
INFOLINE_PROGRESS_CONTINUED = Back.GREEN + Fore.BLUE + "   " + Style.RESET_ALL + " "
INFOLINE_ECHO_CONTINUED = Fore.BLACK + Back.CYAN + Style.DIM + "   " + Style.RESET_ALL + " "
INFOLINE_SYSTEM_CONTINUED = Back.YELLOW + Fore.WHITE + "   " + Style.RESET_ALL + " "
INFOLINE_ERROR_CONTINUED = Back.RED + Fore.WHITE + "   " + Style.RESET_ALL + " "
INFOLINE_EXTERNAL_STDOUT_CONTINUED = Back.WHITE + Fore.BLUE + " . " + Style.RESET_ALL + " "
INFOLINE_EXTERNAL_STDERR_CONTINUED = Back.WHITE + Fore.RED + " . " + Style.RESET_ALL + " "
INFOLINE_VERBOSE_CONTINUED = Back.BLUE + Fore.CYAN + "   " + Style.RESET_ALL + " "

FOLDER_SETTINGS = "settings"
FOLDER_TEMPORARY = "temporary"
FOLDER_PLUGIN_DATA = "data"


class EDisplay( MEnum ):
    """
    Various methods for converting `UpdateInfo` to a string.
    """
    TIME_REMAINING = 0
    OPERATIONS_REMAINING = 1
    TIME_PER_OPERATION = 2
    OPERATIONS_PER_SECOND = 3
    SAMPLE_RANGE = 4
    OPERATIONS_COMPLETED = 5
    TIME_TAKEN = 6
    TIME_REMAINING_SHORT = 7
    TOTAL_RANGE = 8


class EStream( MEnum ):
    """
    Indicates the nature of a progress update, hinting (but not enforcing) the appropriate behaviour of the receiving host (CLI or GUI).
    The `styles` listed below are the default styles for the default hosts.
    
    :data PROGRESS:             General progress update.
                                Sent by: Any plugin may send this.
                                         Progress bar updates are also sent using this stream.
                                Style:   De-emphasised. Does not prevent GUI from closing window after plugin completes.
                                
    :data INFORMATION:          Key information.
                                Sent by: Any plugin may send this.
                                Style:   Displayed. Keeps GUI window open after plugin completes
                                
    :data WARNING:              Key warning or non-critical error.
                                Sent by: Any plugin may send this.
                                         `warnings.warn` is also directed here.
                                Style:   Emphasised. Keeps GUI window open.
                                
    :data ECHO:                 Echoed command.
                                Sent by: Only Intermake internals send this, to echo commands back to the user.
                                Style:   Hidden by default in CLI. Ignored by GUI.
                                
    :data SYSTEM:               System messages.
                                Sent by: Only Intermake internals send this, to display messages of no particular origin.
                                Style:   Displayed in CLI. Ignored by GUI.
                                
    :data ERROR:                Error messages.
                                Sent by: Only Intermake internals send this, to display errors and traceback.
                                         - Use `raise` to identify an error.
                                Style:   Displayed in CLI, ignored by GUI, which uses the `Exception` object verbatim.
                                    
    :data EXTERNAL_STDOUT:      External messages.
                                Sent by: Only Intermake internals send this, to relay messages received from external tools.
                                         - Use `subprocess_helper.run_subprocess` to run a process with piping to this stream.
                                Style:   Similar to `VERBOSE`.

    :data EXTERNAL_STDERR:      See `EXTERNAL_STDOUT`.
                        
    :data VERBOSE:              Verbose messages.
                                Sent by: Any plugin may send this, but its use for logging is discouraged.
                                         - For logging, Intermake uses `mhelper.Logger`, other plugins will use their own preferred tool.
                                Style:   Hidden by default.
                                         Possible to view later if the last result is available to view.
                        
    """
    PROGRESS = 1
    INFORMATION = 2
    WARNING = 3
    ECHO = 4
    SYSTEM = 5
    ERROR = 6
    EXTERNAL_STDOUT = 7
    EXTERNAL_STDERR = 8
    VERBOSE = 9


class EThread( MEnum ):
    """
    Designates the preferred thread mode of plugins.
    
    :data SINGLE:       Must run single threaded.
                        
                        * In the GUI the plugin executes on its own thread.
                        * In the CLI the plugin executes on the main thread.
                        
                        Used for plugins that aren't tolerant of multi-threaded or multi-cored systems.
                    
    :data MULTI:        Can run multi-threaded or multi-cored.
                        
                        * In the GUI the several instances of the plugin execute on their own individual threads.
                        * In the CLI one instance of the plugin will be executed in the main thread, but it can be expected that the user has setup several simultaneous $(APPNAME) processes (e.g. on a compute cluster).
                        
                        Internally, `MCMD.thread()` and `MCMD.num_threads()` can be consulted to identify how the workload should be divided.
                        This is the number of threads for the GUI and the user-provided number of processes for the CLI.
                        
                        Used for plugins that are tolerant of multi-threaded and multi-cored systems.
                        
                        Note: There is no guarantee that all threads will be run on the same computer, the user may be using a compute cluster.
                    
    :data UNMANAGED:    Manages its own threading.
    
                        * The plugin will execute in the main thread.
                        * Feedback, if any, must be implemented manually.
                        * MCMD.print() and other feedback related methods may not function as intended.
                         
                        Used for plugins that manage their own threading or remain in memory (e.g. GUIs).
                        
                        (An UNMANAGED plugin is essentially a raw Python function that is displayed to the user). 
    """
    SINGLE = 0
    MULTI = 1
    UNMANAGED = 2
