from typing import Callable, Optional

from PyQt5.QtCore import QPoint, QSize, Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QAbstractButton, QAction, QFrame, QHBoxLayout, QMenu, QSizePolicy, QSpacerItem, QTextEdit, QToolButton, QTreeWidget, QTreeWidgetItem, QLabel, QSplitter
from intermake.engine.environment import MENV
from intermake.engine.plugin import Plugin
from intermake.visualisables import visualisable
from intermake.visualisables.visualisable import EIterVis, IVisualisable, UiInfo, VisualisablePath, NamedValue
from intermake_qt.forms.designer.resource_files import resources
from intermake_qt.forms.frm_arguments import FrmArguments
from intermake_qt.views.tree_view import TreeItemInfo, TreeView
from mhelper import ResourceIcon, ansi_helper, exception_helper, override, string_helper, ignore, FnArgValueCollection
from mhelper_qt import exceptToGui, menu_helper


__author__ = "Martin Rusilowicz"

DGetSource = Callable[[], object]
DSelecting = Callable[[VisualisablePath], bool]
DSelected = Callable[[QTreeWidgetItem], None]


class ResultsView( TreeView ):
    """
    TREE-LIKE TREEVIEW

    Item data is Tuple[Any, Any]:
        Any: The key (displayed using `str()`)
        Any: Anything handled by TypeHandler

    Viewer for query results, dockets, etc.
    """
    
    # Names of Qt property fields
    __PROPERTY_ITEM = "item"
    __PROPERTY_COMMAND = "command"
    
    
    @staticmethod
    def __set_text_to_tvw_comment( text, tvw ):
        data = tvw.selected_data()
        
        if data is None:
            text.setText( "" )
            return
    
    
    def __init__( self,
                  *,
                  tree_widget: QTreeWidget,
                  text_widget: QTextEdit,
                  toolbar_layout: QHBoxLayout,
                  root: VisualisablePath,
                  on_selected: DSelected = None,
                  on_selecting: DSelecting = None,
                  flat: bool = False,
                  show_root: bool = True,
                  title_widget: QLabel = None ):
        """
        CONSTRUCTOR
        :param tree_widget:         Tree widget to manage 
        :param text_widget:         Text widget to manage 
        :param toolbar_layout:      Toolbar layout to manage 
        :param root:              Root object 
        :param on_selected:         How to "select" items (if `None` the select option will not be visible) 
        :param on_selecting:        How to determine if items can be selected (if `None` all items will be selectable)
        :param flat:                Flat (no hierarchy) 
        :param show_root:           Show the root as its own node (always `False` if `flat` is set).
        """
        super().__init__( tree_widget )
        
        # Fields
        self.__num_results = 0
        self.__orig_root = root
        self.__root = root
        self.__title_widget = title_widget
        self.__text_widget = text_widget
        self.__on_selected = on_selected
        self.__on_selecting = on_selecting
        self.__toolbar_layout = toolbar_layout
        self.__flat = flat
        self.__show_root = show_root
        self.__header_map = { }
        self.__buttons = []
        self.__view_comments = True
        
        # Setup
        super().set_resize_on_expand()
        self.widget.setContextMenuPolicy( Qt.CustomContextMenu )
        self.__text_widget.setReadOnly( True )
        self.__text_widget.setStyleSheet( "background:transparent;border:none" )
        splitter: QSplitter = text_widget.parent()
        splitter.setStretchFactor( 0, 3 )
        
        if flat:
            self.widget.setRootIsDecorated( False )
        
        # Toolbar
        self.__btn_refresh = self.__add_button( "Refresh", resources.refresh, toolbar_layout, self.__cmd_refresh )
        self.__btn_back = self.__add_button( "Back", resources.previous, toolbar_layout, self.__cmd_back, in_buttons = False )
        self.__btn_new_window = self.__add_button( "Explore", resources.next, toolbar_layout, self.__cmd_new_window )
        self.__btn_view = self.__add_button( "View", resources.view_text, toolbar_layout, self.__cmd_view )
        self.__btn_run = self.__add_button( "Run", resources.execute, toolbar_layout, self.__cmd_run )
        # self.__add_separator( toolbar_layout )
        # self.__btn_details = self.__add_button( "Details", resources.maximize, toolbar_layout, self.__cmd_details )
        toolbar_layout.addSpacerItem( QSpacerItem( 1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum ) )
        
        # Signals
        self.widget.itemSelectionChanged.connect( self.__on_widget_itemSelectionChanged )
        self.widget.customContextMenuRequested.connect( self.__on_widget_customContextMenuRequested )
        self.widget.itemActivated[QTreeWidgetItem, int].connect( self.__on_widget_itemActivated )
        
        # Populate
        self.rebuild()
    
    
    def __on_widget_itemActivated( self, item: QTreeWidgetItem, column: int ):
        """
        SIGNAL: self.widget::itemActivated
        """
        ignore( column )
        
        data: VisualisablePath = self.item_data( item )
        
        if data is None:
            return
        
        value = data.get_value()
        
        if isinstance( value, Plugin ):
            self.__cmd_run( data )
        elif self.__has_children( data ):
            self.__cmd_new_window( data )
        else:
            self.__cmd_view( data )
    
    
    def rebuild( self ):
        """
        Handles the new set of results
        
        Note that the listing itself is not retained
        """
        
        self.clear()
        
        # The source should be a VisualisablePath or an IVisualisable, it it's not we can coerce it.
        if not isinstance( self.__root, VisualisablePath ):
            if not isinstance( self.__root, IVisualisable ):
                self.__root = visualisable.as_visualisable( self.__root )
            
            self.__root = VisualisablePath.from_visualisable_temporary( self.__root )
        
        # Back button
        self.__btn_back.setEnabled( self.__root is not self.__orig_root )
        
        # Title
        if self.__title_widget is not None:
            self.__title_widget.setText( self.__root.path )
        
        # Setup the headers
        headers = QTreeWidgetItem()
        self.__header_map.clear()
        self.widget.setHeaderItem( headers )
        
        # Add the root
        if self.__root is not None:
            if self.__flat or not self.__show_root:
                for item in self.__root.get_value().visualisable_info().iter_children( previous = self.__root, iter = EIterVis.PROPERTIES | EIterVis.CONTENTS ):
                    self.__add( None, item )
            else:
                self.__add( None, self.__root )
        
        self.resize_columns()
    
    
    def __add( self, parent: Optional[QTreeWidgetItem], child: VisualisablePath ):
        exception_helper.assert_type( "child", child, VisualisablePath )
        self.add_item( parent, child, loader = self.__requires_children( child ) )
    
    
    @property
    def on_selected( self ):
        return self.__on_selected
    
    
    @property
    def on_selecting( self ):
        return self.__on_selecting
    
    
    @staticmethod
    def __add_separator( toolbar_layout ):
        line = QFrame()
        line.setFixedWidth( 8 )
        line.setFrameShape( QFrame.VLine )
        line.setFrameShadow( QFrame.Sunken )
        toolbar_layout.addWidget( line )
    
    
    def __add_button( self, name: str, icon: ResourceIcon, toolbar_layout: QHBoxLayout, command, in_buttons = True ) -> QAbstractButton:
        button = QToolButton()
        button.setFixedSize( QSize( 64, 64 ) )
        button.setText( name )
        button.setIcon( icon.icon() )
        button.setIconSize( QSize( 32, 32 ) )
        button.setToolButtonStyle( Qt.ToolButtonTextUnderIcon )
        toolbar_layout.addWidget( button )
        button.TAG_command = command
        button.clicked[bool].connect( self.__on_toolbar_button_clicked )
        button.setEnabled( False )
        
        if in_buttons:
            self.__buttons.append( button )
        
        return button
    
    
    @exceptToGui()
    def __on_toolbar_button_clicked( self, _: bool ):
        sender = self.widget.window().sender()
        assert isinstance( sender, QAbstractButton )
        command = sender.TAG_command
        command()
    
    
    @exceptToGui()
    def __on_widget_customContextMenuRequested( self, pos: QPoint ):
        tree = self.widget  # type: QTreeWidget
        item = tree.itemAt( pos )
        
        if item is None:
            return
        
        menu = QMenu( self.widget.window() )
        
        for button in self.__buttons:
            assert isinstance( button, QAbstractButton )
            action_item: QAction = menu.addAction( button.text() )
            action_item.setIcon( button.icon() )
            action_item.setEnabled( button.isEnabled() )
            action_item.TAG_command = button.TAG_command
        
        selection = menu_helper.show_menu( self.widget.window(), menu )
        
        if selection is not None:
            selection.TAG_command()
    
    
    @exceptToGui()
    def __on_widget_itemSelectionChanged( self ):
        property: VisualisablePath = self.selected_data()
        
        if property is None:
            for button in self.__buttons:
                button.setEnabled( False )
            
            self.__text_widget.setText( "" )
            return
        
        value = property.get_value()
        
        for button in self.__buttons:
            button.setEnabled( True )
        
        self.__btn_run.setEnabled( isinstance( value, Plugin ) )
        self.__btn_new_window.setEnabled( self.__has_children( property ) )
        
        if self.__btn_run.isEnabled():
            self.__btn_run.setStyleSheet( "font-weight:bold;" )
            self.__btn_new_window.setStyleSheet( "font-weight:normal;" )
            self.__btn_view.setStyleSheet( "font-weight:normal;" )
        elif self.__btn_new_window.isEnabled():
            self.__btn_run.setStyleSheet( "font-weight:normal;" )
            self.__btn_new_window.setStyleSheet( "font-weight:bold;" )
            self.__btn_view.setStyleSheet( "font-weight:normal;" )
        else:
            self.__btn_run.setStyleSheet( "font-weight:normal;" )
            self.__btn_new_window.setStyleSheet( "font-weight:normal;" )
            self.__btn_view.setStyleSheet( "font-weight:bold;" )
        
        text = property.info().doc
        self.__text_widget.setText( text )
        self.__text_widget.setVisible( bool( text ) and self.__view_comments )
    
    
    def root_object( self ) -> Optional[object]:
        return self.__root
    
    
    def __requires_children( self, data: VisualisablePath ):
        if self.__flat:
            return False
        
        return self.__has_children( data )
    
    
    def __has_children( self, data: VisualisablePath ):
        return any( True for _ in data.get_value().visualisable_info().iter_children( previous = data, iter = EIterVis.PROPERTIES | EIterVis.CONTENTS ) )
    
    
    @override
    def on_update_item( self, node_info: TreeItemInfo ):
        """
        OVERRIDE
        """
        
        node: QTreeWidgetItem = node_info.item()
        property: VisualisablePath = node_info.data()
        info: UiInfo = property.get_value().visualisable_info()
        
        # Add children
        if node_info.add_children() and not self.__flat:
            # Add actual items
            children = [child for child in info.iter_children( previous = property, iter = EIterVis.CONTENTS | EIterVis.PROPERTIES )]
            children = sorted( children, key = lambda child: child.key )
            
            for index, child in enumerate( children ):
                if index > 100:
                    # Don't display more than 100 items
                    self.__add( node, VisualisablePath.from_visualisable_temporary( NamedValue( "", "...only displaying the first 100 items." ) ) )
                    break
                
                self.__add( node, child )
            
            # Columns changed
            self.resize_columns()
        
        # Colour the item by its selectability
        if self.__on_selecting is not None:
            if self.__on_selecting( property ):
                colour = info.qcolour()
                colour_2 = QColor( Qt.black )
            else:
                colour = QColor( Qt.gray )
                colour_2 = QColor( Qt.gray )
        else:
            colour = info.qcolour()
            colour_2 = QColor( Qt.black )
        
        # COLUMN: Key
        key_str = MENV.host.translate_name( property.key )
        key_str_b = MENV.host.translate_name( info.name )
        
        if key_str != key_str_b and key_str_b:
            key_str = "{} ({})".format( key_str, key_str_b )
        
        key_str = string_helper.max_width( key_str, 40 )
        
        col_index = self.__get_or_create_column( "Name" )
        node.setText( col_index, key_str )
        node.setForeground( col_index, colour_2 )
        
        # COLUMN: Value
        lines = list( ansi_helper.wrap( str( info.value ), 80 ) )
        text = lines[0] if len( lines ) == 1 else (lines[0] + "…") if lines else ""
        
        if text:
            col_index = self.__get_or_create_column( "Value" )
            node.setText( col_index, text )
            node.setForeground( col_index, colour )
        
        # COLUMN: Type
        # col_index = self.__get_or_create_column( "Type" )
        # node.setText( col_index, str( info.type_name ).lower() )
        # node.setForeground( col_index, colour )
        
        # ICON
        node.setIcon( 0, info.icon.icon() )
        
        # COLUMN: Miscellaneous
        if self.__flat:
            for x in info.iter_children( previous = property, iter = EIterVis.PROPERTIES ):
                text = str( x.get_value() )
                
                if not text or len( text ) > 100:
                    continue
                
                col_index = self.__get_or_create_column( x.key )
                
                node.setText( col_index, text )
    
    
    def __get_or_create_column( self, key: str ):
        col_index = self.__header_map.get( key )
        
        if col_index is None:
            col_index = len( self.__header_map )
            self.__header_map[key] = col_index
            self.widget.headerItem().setText( col_index, key )
        
        return col_index
    
    
    @exceptToGui()
    def __cmd_new_window( self, data: VisualisablePath = None ):
        prop: VisualisablePath = data if data is not None else self.selected_data()
        
        if prop is None:
            return
        
        self.__root = prop
        self.rebuild()
    
    
    @exceptToGui()
    def __cmd_back( self ):
        if self.__root.previous is None or self.__root is self.__orig_root:
            return
        
        self.__root = self.__root.previous
        self.rebuild()
    
    
    @exceptToGui()
    def __cmd_details( self ):
        self.__view_comments = not self.__view_comments
        self.__text_widget.setVisible( self.__view_comments )
    
    
    @exceptToGui()
    def __cmd_run( self, data: VisualisablePath = None ):
        prop: VisualisablePath = data if data is not None else self.selected_data()
        
        if prop is None:
            return
        
        plugin = prop.get_value()
        
        if not isinstance( plugin, Plugin ):
            return
        
        arguments: Optional[FnArgValueCollection] = FrmArguments.request( self.widget.window(), plugin )
        
        if arguments is not None:
            plugin.run_with( arguments )
    
    
    def __cmd_refresh( self ):
        item = self.selected_item()
        
        if item is None:
            return
        
        self.update_item( item, True )
        item.setExpanded( True )
    
    
    def __cmd_view( self, data: VisualisablePath = None ):
        prop: VisualisablePath = data if data is not None else self.selected_data()
        
        if prop is None:
            return
        
        text = str( prop.get_value() )
        
        from intermake_qt.forms.frm_big_text import FrmBigText
        FrmBigText.request( self.window, prop.path, text )
