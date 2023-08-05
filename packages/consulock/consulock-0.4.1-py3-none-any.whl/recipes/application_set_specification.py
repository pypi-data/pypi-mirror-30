class ApplicationSetSpecification:
    def __init__( self, string ):
        self._expressions = string.split( ',' )

    def matches( self, applicationPackage ):
        for expression in self._expressions:
            if self._match( expression, applicationPackage ):
                return True

        return False

    def _match( self, expression, applicationPackage ):
        if expression ==  '*':
            return True

        if '/' in expression:
            bundleId, platform = expression.split( '/' )
            if platform != applicationPackage.platform:
                return False
            if bundleId == '*':
                return True

            return bundleId == applicationPackage.bundleId

        return expression == applicationPackage.md5sum
