from typing import Callable, List, Optional, TypeVar, Iterator

from intermake.engine.host_manager import RunHost
from mhelper import abstract, override, virtual, ResourceIcon, MEnum, ansi_format_helper, ArgsKwargs

from intermake.engine import constants
from intermake.engine.async_result import Result
from intermake.visualisables.visualisable import EColour, IVisualisable, UiInfo


T = TypeVar( "T" )

__author__ = "Martin Rusilowicz"


class _PluginHostSettings:
    """
    :attr number_of_results_to_keep: Number of results to keep in history
    :attr welcome_message: Whether to display the welcome message when the host starts
    """
    
    
    def __init__( self ):
        self.number_of_results_to_keep = 10
        self.welcome_message = False


class ERunMode( MEnum ):
    """
    How the host should run. Also determines the initial configuration.
    
    :remarks: See also `create_simple_host_provider` and `create_simple_host_provider_from_class`.
              `ARG`, `CLI`, `PYI`, `PYS`, `JUP` all run under `ConsoleHost` by default, whilst `GUI` runs under the Qt `GuiHost`.
    
    :data ARG: Parses command line arguments
    :data CLI: Console-based host with a command-line-interactive frontend.
    :data PYI: Console-based host with a Python-interactive frontend. For interactive sessions, this imports the plugins into locals.
    :data PYS: Console-based host without a frontend. For your own Python scripts, this does not modify the environment.
    :data GUI: Graphical host with a graphical frontend.
    :data JUP: Console-based host without a frontend. For Jupyter notebook, this imports the plugins into locals.
    """
    ARG = 0
    CLI = 1
    PYI = 2
    PYS = 3
    GUI = 4
    JUP = 5


class ERunStatus( MEnum ):
    RUN = 0
    PAUSE = 1
    RESUME = 2
    STOP = 3


class ResultsCollection( IVisualisable ):
    """
    Maintains a collection of results.
    Items are added to the back, thus [-1] is the most recent result.
    The size of the list is constrained by `_PluginHostSettings.number_of_results_to_keep`.
    """
    
    
    def __init__( self, owner: "PluginHost" ) -> None:
        self.__data: List[Result] = []
        self.__owner: PluginHost = owner
    
    
    def __str__( self ):
        return "{} results".format( len( self ) )
    
    
    def visualisable_info( self ) -> UiInfo:
        return UiInfo( name = "results",
                       doc = "",
                       value = str( self ),
                       colour = EColour.YELLOW,
                       icon = ResourceIcon( ":/intermake/folder.svg" ),
                       type_name = "ResultsFolder",
                       extra_indexed = self.__data )
    
    
    def append( self, result: Result ) -> None:
        self.__data.append( result )
        
        while len( self ) > self.__owner.host_settings.number_of_results_to_keep:
            self.__data.pop( 0 )
    
    
    def __len__( self ) -> int:
        return len( self.__data )
    
    
    def __bool__( self ) -> bool:
        return bool( self.__data )
    
    
    def __getitem__( self, item ) -> Result:
        return self.__data[item]
    
    
    def __iter__( self ) -> Iterator[Result]:
        return iter( self.__data )


@abstract
class PluginHost:
    """
    All plugins run under a `PluginHost`, this is it.

    Operation logic follows:

        (TODO)

    Only `on_run` need be implemented by the derived class.
    """
    _pluginHostCount = 0
    
    
    def __init__( self ):
        """
        CONSTRUCTOR
        """
        PluginHost._pluginHostCount += 1
        self.__settings: _PluginHostSettings = None
        self._index = PluginHost._pluginHostCount
        self.last_results = ResultsCollection( self )
        self.__num_results = 0
        self.last_result = Result( None, None, None, None, None, None )
        self.last_error = Result( None, None, None, None, None, None )
    
    
    @property
    def can_return( self ):
        return True
    
    
    def get_help_message( self ) -> str:
        return self.on_get_help_message()
    
    
    @virtual
    def on_get_help_message( self ) -> str:
        """
        Provides the help the user gets when they type `basic_help`.
        """
        return """You are running in a {} host and I can't give you any help because the creator of this host hasn't provided a `on_get_help_message`.
        Please see `readme.md` in the application directory for more information.""".format( type( self ).__name__ )
    
    
    @property
    def is_gui( self ):
        return not self._is_cli()
    
    
    @property
    def is_cli( self ):
        return self._is_cli()
    
    
    def _is_cli( self ):
        return True
    
    
    @abstract
    def _PLUGINHOST_get_run_mode( self ) -> ERunMode:
        """
        Gets the run-mode hint.
        """
        raise NotImplementedError( "abstract" )
    
    
    def on_status_changed( self, status: ERunStatus ):
        """
        Called when the host status is changed.
        """
        return
    
    
    @property
    def run_mode( self ) -> ERunMode:
        return self._PLUGINHOST_get_run_mode()
    
    
    def register_thread( self, mandate ) -> None:
        """
        Registers a Mandate onto a new thread.
        This means that when MCMD is called this mandate will be retrieved.
        
        Note this function does not perform any thread management for you!
        It simply means that a new thread will be able to correctly receive the mandate from the calling thread.
        Since mandates are not multi-threaded it is assumed that the that the caller has set up any thread-management
        themselves, such as locking any calls to the Mandate or simply suspending the Mandate's original thread. 
        
        :param mandate: Mandate retrieved from the creating thread and being registered with this thread. 
        """
        pass
    
    
    @property
    def host_settings( self ) -> _PluginHostSettings:
        """
        Obtains the settings used to control the base host class.
        :return:    Settings. 
        """
        if self.__settings is None:
            from intermake.engine.environment import MENV
            self.__settings = MENV.local_data.store.retrieve( "host", _PluginHostSettings )
        
        # noinspection PyTypeChecker
        return self.__settings
    
    
    def run_host( self, args: RunHost ) -> None:
        """
        Runs the host's main loop, if it has one.
        :param args:    Arguments 
        :return:        `True` to return to the previous host, `False` to tell the previous host to exit too. 
        """
        try:
            self.on_run_host( args )
        except Exception as ex:
            print( ansi_format_helper.format_traceback( ex ) )
            raise
    
    
    @virtual
    def on_run_host( self, args: RunHost ) -> None:
        """
        Runs the host's main loop, if it has one.
        :param args:    Arguments 
        :return:        `True` to return to the previous host, `False` to tell the previous host to exit too. 
        """
        raise NotImplementedError( "abstract" )
    
    
    @virtual
    def substitute_text( self, text ):
        """
        Formats help text for the current host.
        
        The base implementation replaces $(XXX) from the set of constants. 
        
        Concrete hosts may override this further.
        
        :param text:    Input text 
        :return:        Text to display 
        """
        from intermake.engine.environment import MENV
        
        if text is None:
            return ""
        
        text = text.replace( "$(APPNAME)", MENV.abv_name )
        
        for k, v in MENV.constants.items():
            text = text.replace( "$(" + k + ")", str( v ) )  # TODO: Inefficient
        
        return text
    
    
    @abstract
    def get_mandate( self ):
        """
        Obtains the mandate for the plugin being run (on the current thread).
        It is possible for this to be called by the "system", when no plugin is running, the result should never be `None`.
        
        Note: This is the abstracted delegate, to get the mandate externally, use the `current_mandate()` function.
        This function must be overridden by the concrete host.
        
        :rtype: Mandate 
        """
        raise NotImplementedError( "abstract" )
    
    
    @property
    def console_width( self ):
        """
        Some plugins want to know the width of the screen for text-display purposes.
        This is how they get that.
        
        This calls the `_get_console_width` virtual function.
         
        :return: Width of text, in characters. 
        """
        return min( 180, self._get_console_width() )
    
    
    @property
    def console_width_unsafe( self ):
        """
        `console_width`, without clamping. This may be a large value - use only for wrapping, not for padding!
        """
        return self._get_console_width()
    
    
    @virtual
    def _get_console_width( self ):
        """
        When obtaining the width of the screen this function is called.
        The base implementation suggests no wrapping (an arbitrary large value).
        The derived class may suggest more appropriate text-wrapping limit.
        :return: 
        """
        return 120
    
    
    @abstract
    def call_virtual_run( self, plugin, args: ArgsKwargs ) -> Optional[object]:
        """
        Called for implementation-specific running of a plugin.
        This process exists so the derived hosts execute the plugin in the thread or method of their choice.

        The implementing class should respond by:
            1. Ensuring `PluginHost._get_mandate` returns an appropriate value when called from within `Plugin.call_run`.
            2. Calling `Plugin.call_run` on the plugin object.
         
        :param args:
        :param plugin:
         
        :type args:        ArgsKwargs
        :type plugin:      Plugin
        """
        raise NotImplementedError( "Abstract" )
    
    
    @virtual
    def has_form( self ):
        """
        Returns if it is okay to call `form`. 
        """
        return False
    
    
    @property
    def form( self ):
        return self.get_form()
    
    
    @virtual
    def get_form( self ):
        """
        Gets the form associated with the host
        Meaningless for a non-GUI host
        """
        raise ValueError( "This plugin must be run under a GUI." )
    
    
    def translate_name( self, name: str ) -> str:
        """
        Given the `name` of an object, translates it into something more friendly to the user.
        """
        raise NotImplementedError( "Abstract" )
    
    
    def set_last_result( self, result: Result ):
        """
        :param result:
         
        :type result: Result
        :rtype: None
        """
        self.__num_results += 1
        
        result.title = str( self.__num_results ) + ". " + result.title
        result.index = self.__num_results
        self.last_results.append( result )
        
        if result.is_success:
            if result.result is not None:
                self.last_result = result
        else:
            if result.exception is not None:
                self.last_error = result


class _AsyncResultAsVisualisable( IVisualisable ):
    """
    Wraps an individual result to an `IVisualisable` so the user can explore it. 
    """
    
    
    def __init__( self, name, data: Result, comment ):
        """
        :param name:    Name of the result (name of the result, e.g. last, error, 1, 2, 3...)
        :param data:    The actual AsyncResult 
        :param comment: Comment on the result (where it came from, e.g. my_super_plugin)
        """
        self.name = name
        self.data = data
        self.comment = comment
    
    
    @override
    def visualisable_info( self ) -> UiInfo:
        return UiInfo( name = self.name,
                       doc = self.comment or self.data.title,
                       type_name = "Result",
                       value = str( self.data ),
                       colour = EColour.RED if self.data.is_error else EColour.YELLOW if self.data.result is None else EColour.BLUE,
                       icon = ResourceIcon( ":/intermake/failure.svg" ) if self.data.is_error else ResourceIcon( ":/intermake/success.svg" ) if self.data.result is None else ResourceIcon( ":/intermake/successplus.svg" ),
                       extra = { "result"   : self.data.result,
                                 "exception": self.data.exception,
                                 "traceback": self.data.traceback,
                                 "messages" : self.data.messages } )


class ResultsExplorer( IVisualisable ):
    """
    The `ResultsExplorer` class is used to explore results from the execution of previous
    plugins, wrapping the set of results into an `IVisualisable` object. 
    """
    
    
    @override
    def visualisable_info( self ) -> UiInfo:
        from intermake.engine.environment import MENV
        host = MENV.host
        
        return UiInfo( name = constants.EXPLORER_KEY_RESULTS,
                       doc = "Explore your query history",
                       type_name = constants.VIRTUAL_FOLDER,
                       value = self.__visualisable_info_value(),
                       colour = EColour.YELLOW,
                       icon = ResourceIcon( ":/intermake/folder.svg" ),
                       extra_named = [_AsyncResultAsVisualisable( "last_result", host.last_result, "Holds the last successful result" ),
                                      _AsyncResultAsVisualisable( "last_error", host.last_error, "Holds the last failure result" )] \
                                     + [_AsyncResultAsVisualisable( "result_{}".format( i ), x, "Result number {}".format( i ) ) for i, x in host.last_results] )
    
    
    @override
    def __str__( self ):
        return constants.EXPLORER_KEY_RESULTS
    
    
    @staticmethod
    def __visualisable_info_value():
        """
        Value property of `visualisable_info`.
        """
        from intermake.engine.environment import MENV
        host = MENV.host
        
        if not host.last_results:
            return "(empty)"
        
        last_result = host.last_results[-1]
        
        if last_result.is_success:
            if last_result.result is not None:
                return "Data: {}".format( last_result.title )
            else:
                return "Success: {}".format( last_result.title )
        else:
            return "Error: {}".format( last_result.title )


DHostProvider = Callable[[], PluginHost]
"""
Callable that takes no arguments and returns a plugin host.
"""
