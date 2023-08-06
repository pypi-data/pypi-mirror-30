from mhelper import Logger


_PluginHost = "PluginHost"

_LOG = Logger( "host_manager" )


def run_host( host: _PluginHost ) -> None:
    """
    Runs a host.
    """
    RunHost( host )
    
class UserExitError( BaseException ):
    """
    Used as a special error to indicate the user wishes to exit.
    This is always raised past the usual `ConsoleHost` error, thus allowing termination of the front-end via its handler.
    """
    pass


class RunHost:
    """
    Arguments passed to a host when it runs.
    
    :attr __previous_host:  Previous host
    :attr can_return:       Whether the new host has a previous host to return to
    :attr exit:             If new host sets this to `True` the application will exit the host is released.
                            Use only when `can_return` is set, otherwise the application will exit anyway.
    :attr persist:          If the new host sets this to `True` it is not released when the `run_host` function
                            exits and must call `release` manually. 
    """
    
    
    def __init__( self, host: _PluginHost ):
        """
        CONSTRUCTOR
        """
        from intermake.engine.environment import MENV
        from intermake.hosts.base import ERunStatus
        
        
        self.__previous_host = MENV.host
        self.__host = host
        self.can_return = self.__previous_host.can_return
        self.exit = False
        self.persist = False
        
        MENV.host.on_status_changed( ERunStatus.PAUSE )
        MENV._set_host( host )
        MENV.host.on_status_changed( ERunStatus.RUN )
        
        try:
            _LOG( "RUN HOST : {}", self.__host )
            MENV.host.run_host( self )
        except Exception as ex:
            raise ValueError( "Error running host «{}».".format( MENV.host ) ) from ex
        
        if not self.persist:
            self.release()
    
    
    def release( self ):
        _LOG( "RELEASE HOST : {}", self.__host )
        from intermake.engine.environment import MENV
        from intermake.hosts.base import ERunStatus
        
        if MENV.host is not self.__host:
            raise ValueError( "Attempt to exit a host but this host «{}» has already exited in lieu of «{}».".format( self.__host, MENV.host ) )
        
        MENV.host.on_status_changed( ERunStatus.STOP )
        MENV._set_host( self.__previous_host )
        MENV.host.on_status_changed( ERunStatus.RESUME )
        
        if self.exit:
            raise UserExitError( "Host requested all other hosts exit." )
