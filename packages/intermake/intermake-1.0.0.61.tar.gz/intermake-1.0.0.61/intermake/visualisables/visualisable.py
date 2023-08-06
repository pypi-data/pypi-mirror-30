from enum import Enum
from typing import Any, Dict, Iterator, List, Optional, Tuple, Union, Type
# noinspection PyPackageRequirements
from flags import Flags

from mhelper import SwitchError, abstract, exception_helper, override, reflection_helper, MGeneric, string_helper, FindError
from mhelper.qt_resource_objects import ResourceIcon


class IVisualisable:
    """
    Provides an abstraction of UI properties beyond a simple `__str__`.
    """
    
    
    @abstract
    def visualisable_info( self ) -> "UiInfo":
        """
        ABSTRACT
        Obtains the UI representation of this object.
        See `UiInfo` for more details.
        
        This should not be called manually - use `VisualisablePath.info`.
        """
        raise NotImplementedError( "abstract" )


OUBasic = Union[str, bool, float, int]
OUAcceptable = Optional[Union[str, bool, float, int, List[OUBasic], Dict[str, OUBasic], Tuple[OUBasic], IVisualisable]]
# OUExtraIter = Optional[ Union[ Callable[ [ ], Iterable[ OUAcceptable ] ], Iterable[ OUAcceptable ] ] ]
OUExtraIter = Any
# OUExtra = Optional[ Union[ Callable[ [ ], Dict[ str, OUAcceptable ] ], Dict[ str, OUAcceptable ] ] ]
OUExtra = Any


class EColour( Enum ):
    MUTED_FOREGROUND = -2
    NORMAL = -1
    BLACK = 0
    BLUE = 1
    GREEN = 2
    CYAN = 3
    RED = 4
    MAGENTA = 5
    YELLOW = 6
    WHITE = 7


class VisualisablePath( MGeneric ):
    """
    UiInfo meta-data.
    """
    SEP = "/"
    
    
    def __init__( self,
                  previous: Optional["VisualisablePath"],
                  key: str,
                  value: object,
                  is_root: bool ):
        self.previous = previous
        self.key = key
        self.__value = value
        self.is_root = is_root
    
    
    def join( self, dest: str ) -> "VisualisablePath":
        """
        Returns a new `VisualisablePath` incorporating the new path.
        :param dest: String representation of path
        """
        from intermake.engine.environment import MENV, MCMD
        
        # Where are we now?
        current = self
        env = MENV
        
        # Do we go back to the root?
        for x in (str( env.root.visualisable_info().name ), self.SEP):
            if dest.startswith( x ):
                dest = dest[len( x ):]
                current = self.get_root()
                break
        
        # Iterate over the elements
        for element in dest.split( self.SEP ):
            if not element:
                continue
            
            # No change: "."
            if element == ".":
                continue
            
            # Up one level: ".."
            if element == "..":
                if current.previous is None:
                    raise KeyError( "Cannot go up to «{}» (you are already at the top level' - «{}»)".format( element, current ) )
                else:
                    current = current.previous
                    continue
            
            element = MCMD.host.translate_name( element ).lower()
            children = list( current.info().iter_children() )
            
            try:
                the_next = string_helper.find( source = children,
                                               search = element,
                                               namer = lambda x: MCMD.host.translate_name( x.key ).lower(),
                                               fuzzy = False )
            except FindError:
                try:
                    the_next = string_helper.find( source = children,
                                                   search = element,
                                                   namer = lambda x: MCMD.host.translate_name( x.get_value().visualisable_info().name ).lower(),
                                                   fuzzy = False )
                except FindError as ex:
                    raise LookupError( "Cannot find «{}» in «{}».".format( element, current ) ) from ex
            
            current = the_next
        
        return current
    
    
    @classmethod
    def type_restriction( cls ) -> Type[IVisualisable]:
        """
        Obtains the generic parameter (if not specified returns IVisualisable).
        """
        if cls.__parameters__ is None or len( cls.__parameters__ ) == 0:
            return IVisualisable
        elif len( cls.__parameters__ ) == 1:
            return cls.__parameters__[0]
        else:
            raise ValueError( "A `VisualisablePath` was constructed with the confusing generic parameters «{0}».".format( cls.__parameters__ ) )
    
    
    def info( self ) -> "UiInfo":
        info = self.get_value().visualisable_info()
        info.parent_path = self
        return info
    
    
    @property
    def path( self ):
        if self.previous:
            return self.previous.path + self.SEP + self.key
        elif self.is_root:
            return self.SEP + self.key
        else:
            return "..." + self.SEP + self.key
    
    
    def __str__( self ):
        if self.is_root:
            return self.key
        else:
            return self.path
    
    
    @classmethod
    def get_root( cls ):
        from intermake.engine.environment import MENV
        return cls.from_visualisable_root( MENV.root )
    
    
    @classmethod
    def from_visualisable_root( cls, vis: object ) -> "VisualisablePath":
        return VisualisablePath( None, cls.__propose_name( vis, "root" ), vis, True )
    
    
    @classmethod
    def __propose_name( cls, vis, default ):
        if isinstance( vis, IVisualisable ):
            name = vis.visualisable_info().name
        else:
            name = default
        return name
    
    
    @classmethod
    def from_visualisable_temporary( cls, vis: object ) -> "VisualisablePath":
        """
        Creates a `VisualisablePath` from an object. 
        :param vis:  Target object. 
        """
        return VisualisablePath( None, cls.__propose_name( vis, "temporary" ), vis, False )
    
    
    def get_value( self ) -> "IVisualisable":
        return as_visualisable( self.get_raw_value() )
    
    
    def get_type( self ) -> type:
        if isinstance( self.__value, IVisualisable ):
            return type( self.__value )
        else:
            return NamedValue
    
    
    def get_raw_type( self ) -> type:
        return type( self.get_raw_value() )
    
    
    def get_raw_value( self ) -> Optional[object]:
        return reflection_helper.defunction( self.__value )


class EIterVis( Flags ):
    __no_flags_name__ = "NONE"
    __all_flags_name__ = "ALL"
    BASIC = 1
    PROPERTIES = 2
    NAMED_CONTENTS = 4
    INDEXED_CONTENTS = 8
    CONTENTS = 4 | 8


class UiInfo:
    """
    Contains information on an IVisualisable.
    
    See __init__ for field descriptions.
    """
    
    
    def __init__( self,
                  *,
                  name: str,
                  doc: str = "",
                  type_name: Optional[str] = None,
                  value: str,
                  colour: Optional[EColour] = None,
                  icon: Union[str, ResourceIcon, None] = None,
                  extra: OUExtra = None,
                  extra_indexed: OUExtraIter = None,
                  extra_named: OUExtraIter = None ):
        """
        Specifies information about an IVisualisable object.
        
        Additional arguments (extra_list and extra) are provided to allow custom information.
        
        * Do not repeat default arguments (e.g. name) in the custom information
        * Extra arguments may be:
            * An IVisualisable
            * A basic type (int, str, float, bool) (providing they are named explicitly via `extra`, or `extra_indexed`)
            * A list providing any of the above
            * A callable providing any of the above 
        
        :param name:            Name of the object.
        :param doc:         Comment on the object.
                                This should provide help information.
                                User-provided comments, etc, should be in `extra`.
        :param type_name:       User readable name of the object type.
                                Deprecated (no longer displayed).
        :param value:           Value of the object.
        :param colour:          Colour of the object (CLI).
        :param icon:            Icon of the object (GUI).
        :param extra:           Extra properties. This dict can yield any `object`s. The properties are named after the `dict.keys`.
        :param extra_named:     Extra properties. This iterable must only yield `IVisualisable`s. The properties are named after the `IVisualisable.visualisable_info().name`.
        :param extra_indexed:   Extra properties. This iterable can yield any `object`s. The properties are named after the order in which they appear. 
        """
        
        if isinstance( icon, str ):
            icon = ResourceIcon( ":/intermake/" + icon + ".svg" )
        
        self.name = name
        self.doc = doc
        self.type_name = type_name
        self.value = value
        self.colour = colour if (colour is not None) else EColour.NORMAL
        self.icon = icon or ResourceIcon( ":/intermake/unknown.svg" )
        self.extra = extra
        self.extra_named = extra_named
        self.extra_indexed = extra_indexed
        self.parent_path = None
    
    
    def iter_children( self, *, previous: VisualisablePath = None, iter: EIterVis = EIterVis.ALL ) -> Iterator[VisualisablePath]:
        """
        Iterates the children of this `UiInfo`, yielding `NamedValue`s.
        """
        if previous is None:
            previous = self.parent_path
        
        try:
            if iter.BASIC:
                yield VisualisablePath( previous, "name", str( self.name ), False )
                yield VisualisablePath( previous, "documentation", str( self.doc ), False )
            
            if iter.PROPERTIES:
                meta_dict = reflection_helper.defunction( self.extra )
                
                if meta_dict is not None:
                    for key, value in meta_dict.items():
                        value = reflection_helper.defunction( value )
                        yield VisualisablePath( previous, key, value, False )
            
            if iter.NAMED_CONTENTS:
                meta_named = reflection_helper.defunction( self.extra_named )
                
                if meta_named is not None:
                    for value in meta_named:
                        exception_helper.assert_type( "value", value, IVisualisable )
                        
                        yield VisualisablePath( previous, str( value.visualisable_info().name ), value, False )
            
            if iter.INDEXED_CONTENTS:
                meta_iter = reflection_helper.defunction( self.extra_indexed )
                
                if meta_iter is not None:
                    for index, item in enumerate( meta_iter ):
                        yield VisualisablePath( previous, "{}".format( index ), item, False )
        except Exception as ex:
            raise ValueError( "Problem iterating children of {}. See causing error for details.".format( self ) ) from ex
    
    
    def supplement( self, **kwargs ) -> "UiInfo":
        """
        Fluent interface that updates `self.extra`.
        """
        self.extra.update( kwargs )
        return self
    
    
    def __str__( self ):
        return "«{0}» = «{1}» ({2})".format( self.name, self.value, self.type_name )
    
    
    def ccolour( self ) -> Tuple[str, str]:
        """
        Console colour
        :return: Tuple (FG, BG) 
        """
        from colorama import Back, Fore
        
        c = self.colour
        if c == EColour.RED:
            return Fore.RED, Back.RED
        elif c == EColour.GREEN:
            return Fore.GREEN, Back.GREEN
        elif c == EColour.BLUE:
            return Fore.BLUE, Back.BLUE
        elif c == EColour.CYAN:
            return Fore.CYAN, Back.CYAN
        elif c == EColour.MAGENTA:
            return Fore.MAGENTA, Back.MAGENTA
        elif c == EColour.YELLOW:
            return Fore.YELLOW, Back.YELLOW
        elif c == EColour.BLACK:
            return Fore.BLACK, Back.BLACK
        elif c == EColour.WHITE:
            return Fore.WHITE, Back.WHITE
        elif c == EColour.NORMAL:
            return Fore.RESET, Back.RESET
        elif c == EColour.MUTED_FOREGROUND:
            return Fore.LIGHTBLACK_EX, Back.LIGHTBLACK_EX
        else:
            raise SwitchError( "c", c )
    
    
    def qcolour( self ):
        """
        QT Colour
        :rtype: QColor
        """
        from PyQt5.QtGui import QColor
        from PyQt5.QtCore import Qt
        
        c = self.colour
        if c == EColour.RED:
            return QColor( Qt.darkRed )
        elif c == EColour.GREEN:
            return QColor( Qt.darkGreen )
        elif c == EColour.BLUE:
            return QColor( Qt.darkBlue )
        elif c == EColour.CYAN:
            return QColor( Qt.darkCyan )
        elif c == EColour.MAGENTA:
            return QColor( Qt.darkMagenta )
        elif c == EColour.YELLOW:
            return QColor( Qt.darkYellow )
        elif c == EColour.BLACK:
            return QColor( Qt.black )
        elif c == EColour.WHITE:
            return QColor( Qt.darkYellow )
        elif c == EColour.NORMAL:
            return QColor( Qt.black )
        elif c == EColour.MUTED_FOREGROUND:
            return QColor( Qt.gray )
        else:
            raise SwitchError( "c", c )


def as_visualisable( x ) -> IVisualisable:
    """
    Obtains the object `x` as an `IVisualisable`, putting it in a wrapper if necessary.
    """
    if isinstance( x, IVisualisable ):
        return x
    
    return NamedValue( "", x )


class NamedValue( IVisualisable ):
    """
    Used to convert basic types to an IVisualisable.
    """
    
    
    def __init__( self, name, value ):
        """
        CONSTRUCTOR
        :param name:        Name and key of the value 
        :param value:       Underlying value 
        """
        if isinstance( value, IVisualisable ):
            raise TypeError( "`IVisualisable` «{}» provided to NamedValue (name = «{}»). This is probably a mistake.".format( name, value ) )
        
        self.name = name
        self.value = value
        self.__icon = None
        self.__colour = None
        self.__type_name = None
        self.__comment = None
        self.__vstr = None
    
    
    @override
    def visualisable_info( self ) -> UiInfo:
        if self.__icon is None:
            self.__type_name = "{}".format( type( self.value ).__name__ )
            
            if self.value is None:
                self.__icon = "empty"
                self.__colour = EColour.MUTED_FOREGROUND
            elif isinstance( self.value, int ):
                self.__icon = "integer"
                self.__colour = EColour.MAGENTA
            elif isinstance( self.value, float ):
                self.__icon = "integer"
                self.__colour = EColour.MAGENTA
            elif isinstance( self.value, list ) or isinstance( self.value, tuple ) or isinstance( self.value, dict ):
                self.__icon = "list"
                self.__colour = EColour.MAGENTA if len( self.value ) else EColour.MUTED_FOREGROUND
                self.__vstr = string_helper.format_array( self.value )
            elif isinstance( self.value, str ):
                self.__icon = "string"
                self.__colour = EColour.MAGENTA
            elif isinstance( self.value, bool ):
                self.__icon = "success" if self.value else "failure"
                self.__colour = EColour.MAGENTA
            elif hasattr( self.value, "__iter__" ):
                self.__type_name = "iterable"
                self.__icon = "list"
                self.__colour = EColour.MAGENTA
            else:
                self.__icon = "unknown"
                self.__colour = EColour.MAGENTA
                self.__type_name = "internal"
                self.__comment = "Internal type: {}".format( type( self.value ) )
        
        result = UiInfo( name = self.name,
                         doc = self.__comment,
                         type_name = self.__type_name,
                         value = str( self ),
                         colour = self.__colour,
                         icon = self.__icon )
        
        if isinstance( self.value, list ) or isinstance( self.value, tuple ):
            result.extra_indexed = self.value
        elif isinstance( self.value, dict ):
            result.extra = self.value
        elif not isinstance( self.value, str ) and hasattr( self.value, "__iter__" ):
            result.extra_indexed = self.value
        
        return result
    
    
    def __str__( self ):
        if not isinstance( self.value, str ) and hasattr( self.value, "__iter__" ):
            return string_helper.format_array( self.value )
        else:
            return str( self.value )
