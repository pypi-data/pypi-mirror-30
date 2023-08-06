from intermake.engine.async_result import Result


class IGuiPluginHostWindow:
    def plugin_completed( self, result: Result ) -> None:
        raise NotImplementedError( "abstract" )
    
    def return_to_console( self ) -> bool:
        raise NotImplementedError( "abstract" )