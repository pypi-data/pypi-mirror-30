from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog, QDialogButtonBox

from mhelper_qt.designer.frm_generic_text_designer import Ui_Dialog


class FrmGenericText( QDialog ):
    """
    A generic text box, similar to Notepad.
    
    ```
    +------------------------------+
    + title                      X + 
    +------------------------------+
    | +--------------------------+ | 
    | | text                     | |
    | |                          | |
    | |                          | |
    | |                          | |
    | +--------------------------+ | 
    |                 [ok][cancel] |
    +------------------------------+
    ```
    """
    
    def __init__( self, parent, title, text ):
        """
        CONSTRUCTOR
        """
        QDialog.__init__( self, parent )
        self.ui = Ui_Dialog( self )
        self.setWindowTitle( title )
        self.ui.TXT_MAIN.setText( text )
    
    
    @staticmethod
    def request( parent, title, text ):
        frm = FrmGenericText( parent, title, text )
        frm.ui.BTNBOX_MAIN.button( QDialogButtonBox.Cancel ).setVisible( False )
        
        return frm.exec_()
    
    
    @pyqtSlot()
    def on_BTNBOX_MAIN_accepted( self ) -> None:
        """
        Signal handler:
        """
        self.accept()
    
    
    @pyqtSlot()
    def on_BTNBOX_MAIN_rejected( self ) -> None:
        """
        Signal handler:
        """
        self.reject()
