import yaml_mako
import recipes
import os

class Command:
    def __init__( self, ** kwargs ):
        self.string = self.PATTERN.format( ** kwargs ).strip()
        self.list = self.string.split()

class CommandLineGenerator:
    def __init__(self, definitionFile, ** kwargs):
        with recipes.open( 'interpreters', definitionFile ) as f:
            self._details = yaml_mako.load(f, ** kwargs )

    def __call__( self, key ):
        if key.startswith( '-' ):
            return key

        return self._details[ key ]
