from typing import Optional, cast

from PyQt5.QtWidgets import QDialog, QWidget

from editorium import EditoriumGrid, EEditGridMode
from intermake_qt.forms.designer.frm_arguments_designer import Ui_Dialog
from intermake_qt.forms.designer.resource_files import resources_rc

from intermake.engine.environment import MENV
from intermake.engine.plugin import Plugin
from mhelper import string_helper, ArgsKwargs, FnArgValueCollection
from mhelper_qt import qt_gui_helper, exceptToGui, exqtSlot


cast( None, resources_rc )

__author__ = "Martin Rusilowicz"

_Coords_ = "Coords"


class FrmArguments( QDialog ):
    def __init__( self, parent, plugin: Plugin, defaults: ArgsKwargs ) -> None:
        """
        CONSTRUCTOR
        """
        QDialog.__init__( self, parent )
        self.ui = Ui_Dialog( self )
        self.main_help_widget = None
        self.__plugin = plugin
        self.result: FnArgValueCollection = None
        self.ui.CHK_HELP.setChecked( _global_options.inline_help )
        self.ui.CHK_HELP.stateChanged[int].connect( self.on_help_toggled )
        
        self.editorium = EditoriumGrid( grid = self.ui.GRID_ARGS,
                                        target = FnArgValueCollection( plugin.args, defaults ),
                                        fn_description = lambda x: MENV.host.substitute_text( x.description ) )
        
        self.__init_controls()
    
    
    @exceptToGui()
    def on_help_toggled( self, _state: int ) -> None:
        _global_options.inline_help = self.ui.CHK_HELP.isChecked()
        self.__init_controls()
    
    
    def __init_controls( self ):
        if self.main_help_widget is not None:
            self.main_help_widget.setParent( None )
        
        info = self.__plugin.visualisable_info()
        description = self.__plugin.get_description()
        description = MENV.host.substitute_text( description )
        self.ui.LBL_PLUGIN_NAME.setText( string_helper.capitalise_first_and_fix( info.name ) )
        self.main_help_widget = self.editorium.create_help_label( description, [self.ui.LBL_PLUGIN_NAME] )
        self.layout().insertWidget( 1, self.main_help_widget )
        
        self.editorium.mode = EEditGridMode.INLINE_HELP if self.ui.CHK_HELP.isChecked() else EEditGridMode.NORMAL
        self.editorium.recreate()
    
    
    @staticmethod
    def request( owner_window: QWidget, plugin: Plugin, *args, **kwargs ) -> Optional[FnArgValueCollection]:
        """
        Shows the arguments request form.
        
        :param owner_window:    Owning window 
        :param plugin:          Plugin to show arguments for 
        :param args:            Optional defaults.
        :param kwargs:          Optional defaults.
        """
        args_kwargs = ArgsKwargs( *args, **kwargs )
        
        try:
            form = FrmArguments( owner_window, plugin, args_kwargs )
            
            if form.exec_():
                return form.result
            else:
                return None
        except Exception as ex:
            from mhelper import ansi_format_helper
            print( ansi_format_helper.format_traceback( ex ) )
            raise
    
    
    def __save_options( self ):
        MENV.local_data.store.commit( _global_options )
        self.__init_controls()
    
    
    @exqtSlot()
    def on_pushButton_clicked( self ) -> None:
        """
        Signal handler:
        """
        
        try:
            result = self.editorium.commit()
            incomplete = result.get_incomplete()
            
            if incomplete:
                raise ValueError( "The following arguments have not been provided:\n{}".format( "\n".join( [("    * " + x) for x in incomplete] ) ) )
            
            self.result = result
            
            self.accept()
        except Exception as ex:
            qt_gui_helper.show_exception( self, "Error", ex )
            return


class _FrmArguments_Options:
    """
    :attr alternate_theme:   Use the alternate theme
    :attr inline_help:       Show help text alongside the arguments, rather than requiring a mouse-over
    """
    
    
    def __init__( self ):
        self.alternate_theme = False
        self.inline_help = True


_global_options = MENV.local_data.store.bind( "gui_arguments", _FrmArguments_Options() )
