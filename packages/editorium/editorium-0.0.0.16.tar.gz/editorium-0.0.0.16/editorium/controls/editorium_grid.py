from PyQt5.QtWidgets import QGridLayout, QSpacerItem, QSizePolicy, QGroupBox, QVBoxLayout, QLabel, QMessageBox
from typing import Optional, Callable

import editorium
from mhelper import MEnum, FnArgValueCollection, Coords, string_helper, NOT_PROVIDED
from mhelper.reflection_helper import FnArg, ArgsKwargs
from mhelper_qt import qt_gui_helper


class EEditGridMode( MEnum ):
    NORMAL = 0
    INLINE_HELP = 1


class EditoriumGrid:
    ansi_theme = qt_gui_helper.ansi_scheme_light( bg = "#00000000", fg = "#000000" )
    
    def __init__( self,
                  grid: QGridLayout,
                  target: Optional[FnArgValueCollection],
                  mode: EEditGridMode = EEditGridMode.NORMAL,
                  fn_description: Callable[[FnArg], str] = None ):
        """
        CONSTRUCTOR
        :param grid:            Grid to bind to 
        :param target:          Target to create query for 
        :param mode:            Display mode 
        :param fn_description:  How to obtain descriptions (by default `FnArg.description`) 
        """
        self.grid = grid
        self.target: FnArgValueCollection = target
        self.mode = mode
        self.fn_description = fn_description
        self.editors = []
        
        
        
    
    
    def recreate( self ):
        self.__delete_children()
        self.editors.clear()
        
        coords = Coords( 0, 0 )
        
        for index, plugin_arg in enumerate( self.target ):
            if self.mode == EEditGridMode.NORMAL:
                self.__mk_editor_grid( plugin_arg, coords )
            else:
                self.__mk_editor_expanded( plugin_arg, coords )
        
        self.grid.addItem( QSpacerItem( 1, 1, QSizePolicy.Minimum, QSizePolicy.Expanding ) )
    
    
    def __delete_children( self ):
        for i in reversed( range( self.grid.count() ) ):
            widget = self.grid.itemAt( i ).widget()
            
            if widget is not None:
                widget.setParent( None )
    
    
    def __mk_editor_expanded( self, plugin_arg: FnArg, coords: Coords ):
        # Groupbox
        parameter_groupbox = QGroupBox()
        parameter_groupbox.setTitle( string_helper.capitalise_first_and_fix( plugin_arg.name ) )
        parameter_groupbox.setMaximumWidth( 768 )
        parameter_groupbox.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Minimum )
        parameter_groupbox.setWhatsThis( str( plugin_arg.annotation ) )
        
        # Layout
        parameter_layout = QVBoxLayout()
        parameter_groupbox.setLayout( parameter_layout )
        
        # Position
        self.grid.addWidget( parameter_groupbox, coords.row, coords.col )
        
        coords.row += 1
        
        # Help label
        help_widget = self.create_help_label( self.__get_description( plugin_arg ), [parameter_groupbox] )
        parameter_layout.addWidget( help_widget )
        editor = self.__mk_editorium( plugin_arg, self.target.get_value( plugin_arg ) )
        
        parameter_layout.addWidget( editor.editor )
    
    
    @classmethod
    def create_help_label( cls, help_text: str, controls ) -> QLabel:
        help_text = help_text.strip()
        
        html = qt_gui_helper.ansi_to_html( help_text, lookup = cls.ansi_theme )
        
        html = html.replace( "font-family:sans-serif", "font-family:Times New Roman" )
        
        help_label = QLabel()
        help_label.setProperty( "theme", "helpbox" )
        help_label.setWordWrap( True )
        help_label.setText( html )
        help_label.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Preferred )
        help_label.setWhatsThis( html )
        
        for control in controls:
            control.setToolTip( html )
            control.setWhatsThis( html )
        
        return help_label
    
    
    def __mk_editorium( self, arg : FnArg, value: object ):
        messages = { }
        
        if self.mode == EEditGridMode.INLINE_HELP:
            messages[editorium.OPTION_BOOLEAN_RADIO] = True
        else:
            messages[editorium.OPTION_ALIGN_LEFT] = True
        
        editor = editorium.default_editorium().get_editor( arg.annotation.value, messages = messages )
        editor.editor.setSizePolicy( QSizePolicy.Minimum, QSizePolicy.Minimum )
        
        if value is NOT_PROVIDED:
            value = arg.default
        
        if value is NOT_PROVIDED:
            value = None
        
        editor.set_value( value )
        
        self.editors.append( (arg, editor) )
        return editor
    
    
    def __mk_editor_grid( self, arg: FnArg, coords: Coords ):
        # NAME LABEL
        label = QLabel()
        label.setText( '<a href="." style="color:{}; text-decoration: none">{}</a>'.format( self.ansi_theme.get_default().fore, arg.name ) )
        d = self.__get_description( arg )
        label.setWhatsThis( d )
        label.linkActivated[str].connect( self.help_button_clicked )
        label.setStyleSheet( "QLabel:hover{background:#FFFFE0}" )
        self.grid.addWidget( label, coords.row, coords.col )
        
        # Input
        editor = self.__mk_editorium( arg, self.target.get_value( arg ) )
        self.grid.addWidget( editor.editor, coords.row, coords.col + 1 )
        self.create_help_label( d, [label, editor.editor] )
        
        coords.row += 1
    
    
    def __get_description( self, plugin_arg: FnArg ):
        if self.fn_description:
            return self.fn_description( plugin_arg )
        else:
            return plugin_arg.description
    
    
    def help_button_clicked( self, _: object ):
        html = self.grid.sender().toolTip()
        QMessageBox.information( self.grid, "Help", html )


    def commit( self ) -> FnArgValueCollection:
        """
        Commits the changes and returns the modified value collection.
        """
        result = self.target
        
        for plugin_arg, value_fn in self.editors:
            try:
                result.set_value(plugin_arg, value_fn.get_value())
            except Exception as ex:
                raise ValueError( "The value of the argument «{}» is invalid: ".format( plugin_arg.name ) + str( ex ) ) from ex
        
        return result
