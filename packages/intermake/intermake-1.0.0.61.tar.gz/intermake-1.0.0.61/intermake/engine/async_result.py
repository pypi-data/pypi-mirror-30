from traceback import format_exc
from typing import Callable, List, Optional

from intermake.engine.progress_reporter import Message
from intermake.visualisables.visualisable import IVisualisable, UiInfo, EColour


__author__ = "Martin Rusilowicz"


class Result( IVisualisable ):
    """
    Holds a result from Intermake.
    """
    
    
    def __init__( self, title, result, exception, stacktrace, messages: Optional[List[Message]], plugin ):
        """
        :param title:           Title of the query 
        :param result:          Result of the query (if successful)  
        :param exception:       Result of the query (if unsuccessful) 
        :param stacktrace:      Stack trace accompanying the `exception` 
        :param messages:        Messages recorded during the query (regardless of outcome) 
        :param plugin:          Plugin with which the query was was made
        """
        self.title = title
        self.result = result
        self.exception = exception
        self.traceback = stacktrace
        self.messages = messages
        self.plugin = plugin
        self.index = -1
    
    
    def visualisable_info( self ):
        return UiInfo( name = self.title,
                       doc = "",
                       type_name = "Result",
                       value = str( self.exception ) if self.is_error else str( self.result ),
                       colour = EColour.RED if self.is_error else EColour.GREEN,
                       icon = "error" if self.is_error else "success",
                       extra = {
                           "result"   : self.result,
                           "exception": self.exception,
                           "messages" : self.messages,
                           "traceback": self.traceback,
                           "plugin"   : self.plugin,
                           "index"    : self.index
                       } )
    
    
    def raise_exception( self ):
        if self.exception:
            raise self.exception
    
    
    @property
    def is_success( self ):
        return self.exception is None
    
    
    @property
    def is_error( self ):
        return self.exception is not None
    
    
    @property
    def foremost( self ):
        if self.is_success:
            return self.result
        else:
            return self.exception
    
    
    def __str__( self ):
        if self.is_success:
            if self.result is None:
                return str( self.title ) + " = (Success)"
            else:
                return str( self.title ) + " = " + str( self.result )
        else:
            return str( self.title ) + " = (Error:" + str( self.exception ) + ")"
