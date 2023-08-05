import os
import io
HERE = os.path.dirname( __file__ )

class RecipeNotFoundException( Exception ):
    pass

def get( prefix, filename = '' ):
    result = os.path.join( HERE, prefix, filename )
    result = result.rstrip( '/' )
    if not os.path.exists( result ):
        raise RecipeNotFoundException( filename )

    return result

def open( prefix, filename ):
    return io.open( get( prefix, filename ) )
