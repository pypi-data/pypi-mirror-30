from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem


TAG_header_map = "TAG_header_map"
TAG_data = "TAG_data"


def get_or_create_column( tree: QTreeWidget, key: str ):
    if hasattr( tree, TAG_header_map ):
        header_map = getattr( tree, TAG_header_map )
    else:
        header_map = { }
        setattr( tree, TAG_header_map, header_map )
    
    col_index = header_map.get( key )
    
    if col_index is None:
        col_index = len( header_map )
        header_map[key] = col_index
        
        if tree.headerItem() is None:
            tree.setHeaderItem( QTreeWidgetItem() )
        
        tree.headerItem().setText( col_index, key )
    
    return col_index


def get_selected_data( tree: QTreeWidget ):
    sel = tree.selectedItems()
    
    if len( sel ) == 1:
        return get_data( sel[0] )
    else:
        return None


def set_data( item, data ):
    setattr( item, TAG_data, data )


def get_data( item ):
    if hasattr( item, TAG_data ):
        return getattr( item, TAG_data )
    else:
        return None
