__author__ = "Martin Rusilowicz"


class ResourceIcon:
    """
    References a Qt resource.
    (Does not require the Qt library until :method:`icon` is called).
    """
    
    
    def __init__( self, path: str ):
        """
        CONSTRUCTOR
        :param path: Resource path
        """
        self._path = path
        self._icon = None
        
    @property
    def path( self ):
        return self._path
    
    
    def __repr__( self ):
        return "ResourceIcon(«{0}»)".format( self._path )
    
    
    def __call__( self ):
        """
        Calls :method:`icon`.
        """
        return self.icon()
    
    
    def icon( self ):
        """
        Use to obtain the icon.
        """
        from PyQt5.QtGui import QIcon
        
        if not self._icon:
            self._icon = QIcon( self._path )
        
        return self._icon
