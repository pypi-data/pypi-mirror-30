import os
import yaml
import glob
import pathlib
from recipes import application_set_specification
import recipes
import yaml_mako
import recipes
import collections
from recipes import command_line_generator
import time

class FusionSet:
    HERE = pathlib.Path( __file__ ).parent
    FUSION_SETS_YAML = HERE / 'all.yaml'

    @classmethod
    def _scan( cls ):
        fixtures = recipes.get( 'fixtures' )
        byName = {}
        with cls.FUSION_SETS_YAML.open() as f:
            documents = yaml_mako.load_all( f, fixtures = fixtures )

        for document in documents:
            if document[ 'name' ] in byName:
                raise Exception( 'fusion set names should be unique' )
            byName[ document[ 'name' ] ] = document

        return byName

    @classmethod
    def load( cls, name ):
        byName = cls._scan()
        document = byName[ name ]
        return cls( document )

    @classmethod
    def _groups( cls ):
        documents = cls._scan().values()
        result = collections.defaultdict( lambda: [] )
        for document in documents:
            groupNames = document.get( 'group' )
            if type( groupNames ) is not list:
                groupNames = [ groupNames ]

            if '*' not in groupNames:
                groupNames.append( '*' )

            for groupName in groupNames:
                result[ groupName ].append( document )

        return result

    @classmethod
    def loadGroup( cls, name ):
        groups = cls._groups()
        group = groups[ name ]
        return [ cls( document ) for document in group ]

    def __init__( self, info ):
        self._info = info
        appSet = self._info.get( 'application_set', '*' )
        self._applicationSetSpecification = application_set_specification.ApplicationSetSpecification( appSet )

    @property
    def raw( self ):
        return self._info

    def details( self, platform ):
        result = {}
        result[ 'plugins' ] = self._info[ 'plugins' ]
        result[ platform ] = self._info[ platform ]
        return result

    def appliesTo( self, applicationPackage ):
        if applicationPackage.platform in self._info.keys():
            if self._applicationSetSpecification.matches( applicationPackage ):
                return True
        return False

    def commandLine( self, applicationPackage ):
        if len( self._info[ 'plugins' ] ) == 0:
            plugins = ''
        else:
            plugins = '-p {}'.format( ','.join( sorted( self._info[ 'plugins' ].keys() ) ) )
        arguments = self._arguments( applicationPackage )
        return '{} {}'.format( plugins, arguments ).strip()

    def _arguments( self, applicationPackage ):
        fixtures = recipes.get( 'fixtures' )
        DAY_IN_SECONDS = 60 * 60 * 24
        tomorrow = int( time.time() ) + DAY_IN_SECONDS
        commandLineGenerator = command_line_generator.CommandLineGenerator( 'fusion_command_line.yaml', fixtures = fixtures, tomorrow = tomorrow )

        result = []
        keys = self._info[ applicationPackage.platform ].keys()
        for key in sorted( keys ):
            commandLineArgument = commandLineGenerator( key )
            result.append( commandLineArgument )

        result = ' '.join( result )
        return result

    @property
    def name( self ):
        return self._info[ 'name' ]

    def __repr__( self ):
        return self.name
