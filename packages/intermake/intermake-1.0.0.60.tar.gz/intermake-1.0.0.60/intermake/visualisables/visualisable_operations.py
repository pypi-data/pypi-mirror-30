"""
OBSOLETE, DELETE PLEASE.
"""
from typing import Iterable, Optional, Type, cast, List

from intermake.engine.environment import MENV, MCMD
from mhelper import string_helper, MGeneric, FindError
from intermake.visualisables.visualisable import IVisualisable, VisualisablePath


class PathToVisualisable( MGeneric ):
    """
    Path to a visualisable.
      
    GENERIC CLASS:
        * May have a generic parameter (T) denoting the type of the final element, e.g. `PathToVisualisable[DocketFolder]`.
    """
    
    SEP = "/"
    """Path separator"""
    
    
    def __init__( self, path: Iterable[ VisualisablePath] ):
        """
        Constructs from a path.
        Note: Use `from_path` to automatically set the generic parameter rather than using `PathToVisualisable(...)`.
        """
        
        # str is iterable, make sure we aren't using that
        if isinstance( path, str ):
            raise TypeError( "Cannot convert `str` to `PathToVisualisable` through coercion. Maybe you meant to call `path_to`?" )
        
        self.path = tuple( path )
        
        for x in self.path:
            if not isinstance( x, VisualisablePath ):
                raise ValueError( "`PathToVisualisable` must be constructed with `VisualisablePath` instances, but «{0}» is not an `VisualisablePath`.".format( x ) )
        
        if self.type_restriction() is not None:
            if not issubclass( self.path[ -1 ].get_type(), self.type_restriction() ):
                raise ValueError( "<PathToVisualisable[T]> must be have a T=«{}»-pointing instance at the path end, but a «{}» «{}» is not this.".format( self.type_restriction(), self.path[ -1 ].get_type(), self.path[ -1 ].get_raw_value() ) )
    
    
    @staticmethod
    def root_path( target: IVisualisable ):
        """
        Creates a path to a root object.
        """
        return PathToVisualisable[ type( target ) ]( [VisualisablePath( None, target.visualisable_info().name, target )] )
    
    
    def __getstate__( self ):
        raise ValueError( "Attempt to serialise non-serialisable class «{}» («{}»).".format( type( self ).__name__, self ) )
    
    
    @classmethod
    def type_restriction( cls ) -> Type[ IVisualisable ]:
        """
        Obtains the generic parameter (if not specified returns IVisualisable).
        """
        if cls.__parameters__ is None or len( cls.__parameters__ ) == 0:
            return IVisualisable
        elif len( cls.__parameters__ ) == 1:
            return cls.__parameters__[ 0 ]
        else:
            raise ValueError( "PathToVisualisable was constructed with confusing generic parameters: {0}".format( cls.__parameters__ ) )
    
    
    def __str__( self ) -> str:
        """
        Path as a `str`
        """
        result = [ str( self.path[ 0 ].get_value().visualisable_info().name ) ]
        
        for x in self.path[ 1: ]:
            result.append( str( x.key ) )
        
        return self.SEP.join( result )
    
    
    def get_last( self ) -> IVisualisable:
        """
        Last element in the path, the same type as `type_restriction`.
        """
        return self.path[ -1 ].get_value()
    
    
    def get_parent( self ) -> Optional[ IVisualisable ]:
        """
        Penultimate element in path. No type restriction. May be `None` if the path is not long enough.
        """
        if len( self.path ) > 1:
            return self.path[ -2 ].get_value()
        else:
            return None
    
    
    def combine( self, to_append: VisualisablePath ) -> "PathToVisualisable":
        """
        Appends a new element to the path and yields the new path.
        """
        return PathToVisualisable( list( self.path ) + [ to_append ] )
    
    
    @classmethod
    def find_path( cls, *items: IVisualisable ):
        """
        Finds the path from a series of items.
        """
        path = cast( List[ VisualisablePath], [ ] )
        
        for item in items:
            if not path:
                path.append( VisualisablePath( None, item.visualisable_info().name, item ) )
            else:
                last = path[ -1 ].get_value()
                success = False
                
                for child_info in last.visualisable_info().iter_children():
                    if child_info.get_raw_value() == item:
                        path.append( child_info )
                        success = True
                        break
                
                if not success:
                    raise ValueError( "Cannot find the path because the item «{}» doesn't exist in its parent «{}». The full set of items given is «{}».".format( item, last, items ) )
        
        return cls( path )
    
    
    
