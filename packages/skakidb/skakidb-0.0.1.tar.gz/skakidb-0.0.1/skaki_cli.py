from cursesmenu import *
from cursesmenu.items import *

from skakidb.utils import *

init()

menu = CursesMenu( "skaki db-cli" , "Index Options" )

delete_index_item = FunctionItem( "Delete" , delete_index )
create_index_item = FunctionItem( "Create" , create_index )
perform_index_item = FunctionItem( "Perform" , perform_index )

menu.append_item( delete_index_item )
menu.append_item( create_index_item )
menu.append_item( perform_index_item )

menu.show()