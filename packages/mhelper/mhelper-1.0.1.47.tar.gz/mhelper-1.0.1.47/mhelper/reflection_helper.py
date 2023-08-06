import inspect
import warnings
from collections import OrderedDict
from typing import List, Optional, Union, Callable, TypeVar, Type, Dict, cast, Tuple, Sized, Iterable, Iterator, ItemsView

from mhelper import string_helper
from mhelper.special_types import NOT_PROVIDED
from mhelper.exception_helper import SwitchError
from mhelper.generics_helper import MAnnotation, MAnnotationFactory
from mhelper.special_types import MOptional, MUnion


T = TypeVar( "T" )

_TUnion = type( Union[int, str] )

TTristate = Optional[bool]


class AnnotationInspector:
    """
    Class to inspect PEP484 generics.
    """
    
    
    def __init__( self, annotation: object ):
        """
        CONSTRUCTOR
        :param annotation: `type` to inspect 
        """
        if isinstance( annotation, AnnotationInspector ):
            raise TypeError( "Encompassing an `AnnotationInspector` within an `AnnotationInspector` is probably an error." )
        
        self.value = annotation
    
    
    def __str__( self ) -> str:
        """
        Returns the underlying type string
        """
        if isinstance( self.value, type ):
            result = self.value.__name__
        else:
            result = str( self.value )
        
        if result.startswith( "typing." ):
            result = result[7:]
        
        return result
    
    
    @property
    def is_mannotation( self ):
        """
        Is this an instance of `MAnnotation`?
        """
        return isinstance( self.value, MAnnotation )
    
    
    def is_mannotation_of( self, parent: Union[MAnnotation, MAnnotationFactory] ):
        """
        Is this an instance of `MAnnotation`, specifically a `specific_type` derivative?
        """
        if not self.is_mannotation:
            return False
        
        assert isinstance( self.value, MAnnotation )
        
        if isinstance( parent, MAnnotationFactory ):
            return self.value.factory is parent
        elif isinstance( parent, MAnnotation ):
            return self.value.factory is parent.factory
        else:
            raise SwitchError( "parent", parent )
    
    
    @property
    def mannotation( self ) -> MAnnotation:
        """
        Returns the MAnnotation object, if this is an MAnnotation, otherwise raises an error.
        
        :except TypeError: Not an MAnnotation.
        """
        if not self.is_mannotation:
            raise TypeError( "«{}» is not an MAnnotation[T].".format( self ) )
        
        return cast( MAnnotation, self.value )
    
    
    @property
    def mannotation_arg( self ):
        """
        If this is an instance of `MAnnotation`, return the underlying type, otherwise, raise an error.
        """
        if not self.is_mannotation:
            raise TypeError( "«{}» is not an MAnnotation[T].".format( self ) )
        
        assert isinstance( self.value, MAnnotation )
        return self.value.child
    
    
    @property
    def is_generic_list( self ) -> bool:
        """
        Is this a `List[T]`?
        
        (note: this does not include `list` or `List` with no `T`)
        """
        return isinstance( self.value, type ) and issubclass( cast( type, self.value ), List ) and self.value is not list and hasattr( self.value, "__args__" )
    
    
    @property
    def generic_list_type( self ):
        """
        Gets the T in List[T]. Otherwise raises `TypeError`.
        """
        if not self.is_generic_list:
            raise TypeError( "«{}» is not a List[T].".format( self ) )
        
        # noinspection PyUnresolvedReferences
        return self.value.__args__[0]
    
    
    @property
    def is_union( self ) -> bool:
        """
        Is this a `Union[T, ...]`?
        Is this a `MUnion[T, ...]`?
        """
        return isinstance( self.value, _TUnion ) or self.is_mannotation_of( MUnion )
    
    
    def is_directly_below( self, upper_class: type ) -> bool:
        """
        Is `self.value` a sub-class of `lower_class`?
        """
        if not self.is_type:
            return False
        
        try:
            return issubclass( cast( type, self.value ), upper_class )
        except TypeError as ex:
            raise TypeError( "Cannot determine if «{}» is directly below «{}» because `issubclass({}, {})` returned an error.".format( self, upper_class, self, upper_class ) ) from ex
    
    
    def is_directly_above( self, lower_class: type ) -> bool:
        """
        Is `lower_class` a sub-class of `self.value`?
        """
        if not self.is_type:
            return False
        
        if self.is_generic_list:
            # Special case for List[T]
            return issubclass( lower_class, list )
        
        try:
            return issubclass( lower_class, cast( type, self.value ) )
        except TypeError as ex:
            raise TypeError( "Cannot determine if «{}» is directly above «{}» because `issubclass({}, {})` returned an error.".format( self, lower_class, lower_class, self ) ) from ex
    
    
    def is_directly_below_or_optional( self, upper_class: type ):
        """
        Returns if `type_or_optional_type` is a subclass of `upper_class`.
        """
        type_ = self.type_or_optional_type
        
        if type_ is not None:
            return issubclass( type_, upper_class )
        else:
            return False
    
    
    def get_directly_below( self, upper_class: type ) -> Optional[type]:
        """
        This is the same as `is_directly_below`, but returns the true `type` (`self.value`) if `True`.
        """
        if self.is_directly_below( upper_class ):
            return cast( type, self.value )
    
    
    def get_directly_above( self, lower_class: type ) -> Optional[type]:
        """
        This is the same as `is_directly_above`, but returns the true `type` (`self.value`) if `True`.
        """
        if self.is_directly_above( lower_class ):
            return cast( type, self.value )
    
    
    def is_indirectly_below( self, upper_class: type ) -> bool:
        """
        Is `self.value` a sub-class of `upper_class`, or an annotation enclosing a class that is a sub-class of `upper_class`? 
        """
        return self.get_indirectly_below( upper_class ) is not None
    
    
    def is_indirectly_above( self, lower_class: type ) -> bool:
        """
        Is `lower_class` a sub-class of `self.value`, or a sub-class of an annotation enclosed within `self.value`?
        """
        return self.get_indirectly_above( lower_class ) is not None
    
    
    def get_indirectly_above( self, lower_class: type ) -> Optional[type]:
        """
        This is the same as `is_indirectly_below`, but returns the true `type` that is above `lower_class`.
        """
        return self.__get_indirectly( lower_class, AnnotationInspector.is_directly_above )
    
    
    def get_indirectly_below( self, upper_class: type ) -> Optional[type]:
        """
        This is the same as `is_indirectly_above`, but returns the true `type` that iis below `upper_class`.
        """
        return self.__get_indirectly( upper_class, AnnotationInspector.is_directly_below )
    
    
    def __get_indirectly( self, query: type, predicate: "Callable[[AnnotationInspector, type],bool]" ) -> Optional[object]:
        """
        Checks inside all `Unions` and `MAnnotations` until the predicate matches, returning the type (`self.value`) when it does.
        """
        if predicate( self, query ):
            return self.value
        
        if self.is_union:
            for arg in self.union_args:
                arg_type = AnnotationInspector( arg ).__get_indirectly( query, predicate )
                
                if arg_type is not None:
                    return arg_type
        
        if self.is_mannotation:
            annotation_type = AnnotationInspector( self.mannotation_arg ).__get_indirectly( query, predicate )
            
            if annotation_type is not None:
                return annotation_type
        
        return None
    
    
    @property
    def union_args( self ) -> List[type]:
        """
        Returns the list of Union parameters `[...]`.
        """
        if not self.is_union:
            raise TypeError( "«{}» is not a Union[T].".format( self ) )
        
        # noinspection PyUnresolvedReferences
        if self.is_mannotation_of( MUnion ):
            return self.mannotation_arg
        else:
            return cast( _TUnion, self.value ).__args__
    
    
    @property
    def is_optional( self ) -> bool:
        """
        If a `Union[T, U]` where `None` in `T`, `U`.
        """
        if self.is_mannotation_of( MOptional ):
            return True
        
        if not self.is_union:
            return False
        
        if len( self.union_args ) == 2 and type( None ) in self.union_args:
            return True
        
        return False
    
    
    @property
    def is_multi_optional( self ) -> bool:
        """
        If a `Union[...]` with `None` in `...`
        """
        if self.is_mannotation_of( MOptional ):
            return True
        
        if not self.is_union:
            return False
        
        if None in self.union_args:
            return True
        
        return False
    
    
    @property
    def optional_types( self ) -> Optional[List[type]]:
        """
        Returns `...` in a `Union[None, ...]`, otherwise raises `TypeError`.
        """
        if self.is_mannotation_of( MOptional ):
            return [self.mannotation_arg]
        
        if not self.is_union:
            raise TypeError( "«{}» is not a Union[T].".format( self ) )
        
        union_params = self.union_args
        
        if type( None ) not in union_params:
            raise TypeError( "«{}» is not a Union[...] with `None` in `...`.".format( self ) )
        
        union_params = list( self.union_args )
        union_params.remove( type( None ) )
        return union_params
    
    
    @property
    def optional_type( self ) -> Optional[type]:
        """
        Returns `T` in a `Union[T, U]` (i.e. an `Optional[T]`). Otherwise raises `TypeError`.
        """
        t = self.optional_types
        
        if len( t ) == 1:
            return t[0]
        else:
            raise TypeError( "«{}» is not a Union[T, None] (i.e. an Optional[T]).".format( self ) )
    
    
    @property
    def type_or_optional_type( self ) -> Optional[type]:
        """
        If this is an `Optional[T]`, returns `T`.
        If this is a `T`, returns `T`.
        Otherwise returns `None`.
        """
        if self.is_optional:
            return self.optional_type
        elif self.is_type:
            assert isinstance( self.value, type )
            return self.value
        else:
            return None
    
    
    @property
    def safe_type( self ) -> Optional[type]:
        """
        If this is a `T`, returns `T`, else returns `None`.
        """
        if self.is_type:
            assert isinstance( self.value, type )
            return self.value
        else:
            return None
    
    
    @property
    def is_type( self ):
        """
        Returns if my `type` is an actual `type`, not an annotation object like `Union`.
        """
        return isinstance( self.value, type )
    
    
    @property
    def name( self ):
        """
        Returns the type name
        """
        if not self.is_type:
            raise TypeError( "«{}» is not a <type>.".format( self ) )
        
        return self.value.__name__
    
    
    def is_viable_instance( self, value ):
        """
        Returns `is_viable_subclass` on the value's type.
        """
        return self.is_indirectly_above( type( value ) )


def as_delegate( x: Union[T, Callable[[], T]], t: Type[T] ) -> Callable[[], T]:
    """
    If `x` is a `t`, returns a lambda returning `x`, otherwise, assumes `x` is already a lambda and returns `x`.
    This is the opposite of `dedelegate`.
    """
    if isinstance( x, t ):
        return (lambda x: lambda: x)( x )
    else:
        return x


def defunction( x ):
    """
    If `x` is a function or a method, calls `x` and returns the result.
    Otherwise, returns `x`.
    """
    if inspect.isfunction( x ) or inspect.ismethod( x ):
        return x()
    else:
        return x


def dedelegate( x: Union[T, Callable[[], T]], t: Type[T] ) -> T:
    """
    If `x` is not a `t`, calls `x` and returns the result.
    Otherwise, returns `x`.
    This is the opposite of `as_delegate`.
    """
    if not isinstance( x, t ):
        x = x()
    
    return x


def public_dict( d: Dict[str, object] ) -> Dict[str, object]:
    """
    Yields the public key-value pairs.
    """
    r = { }
    
    for k, v in d.items():
        if not k.startswith( "_" ):
            r[k] = v
    
    return r


def find_all( root: object ) -> Dict[int, Tuple[str, str, object]]:
    def __reflect_all( root: object, target: Dict[int, object], name, depth ):
        if id( root ) in target:
            return
        
        short_name = name[-40:]
        
        print( "DEPTH = " + str( depth ) )
        
        print( "ENTER {}".format( short_name ) )
        print( "TYPE = " + type( root ).__name__ )
        
        if type( root ) in (list, dict, tuple):
            print( "LENGTH = " + repr( len( cast( Sized, root ) ) ) )
        else:
            print( "VALUE = " + repr( root ) )
        
        target[id( root )] = type( root ).__name__, name, root
        
        if isinstance( root, dict ):
            print( "ITERATING " + str( repr( len( root ) ) ) + " ITEMS" )
            for i, (k, v) in enumerate( root.items() ):
                print( "START DICT_ITEM {}".format( i ) )
                __reflect_all( v, target, name + "[" + repr( k ) + "]", depth + 1 )
                print( "END DICT_ITEM {}".format( i ) )
        elif isinstance( root, list ) or isinstance( root, tuple ):
            print( "ITERATING " + str( repr( len( root ) ) ) + " ITEMS" )
            for i, v in enumerate( root ):
                print( "START ITEM {}".format( i ) )
                __reflect_all( v, target, name + "[" + repr( i ) + "]", depth + 1 )
                print( "END ITEM {}".format( i ) )
        elif hasattr( root, "__getstate__" ):
            print( "GETTING STATE" )
            print( "START STATE" )
            __reflect_all( root.__getstate__(), target, name + ".__getstate__()", depth + 1 )
            print( "END STATE" )
        elif hasattr( root, "__dict__" ):
            print( "ITERATING DICT OF " + str( repr( len( root.__dict__ ) ) ) + " ITEMS" )
            for i, (k, v) in enumerate( root.__dict__.items() ):
                print( "START DICT_ITEM {}".format( i ) )
                __reflect_all( v, target, name + "." + repr( k ), depth + 1 )
                print( "END DICT_ITEM {}".format( i ) )
        
        print( "EXIT {}".format( short_name ) )
    
    
    target_ = { }
    __reflect_all( root, target_, "root", 0 )
    return target_


def try_get_attr( object_: object, attr_name: str, default = None ):
    if hasattr( object_, attr_name ):
        return getattr( object_, attr_name )
    else:
        return default


def is_list_like( param ):
    return isinstance( param, list ) or isinstance( param, tuple ) or isinstance( param, set ) or isinstance( param, frozenset )


class ICode:
    """
    Interface for code object (for Intellisense only)
    """
    
    
    def __init__( self ):
        self.__class__ = None
        self.__delattr__ = None
        self.__dir__ = None
        self.__doc__ = None
        self.__eq__ = None
        self.__format__ = None
        self.__ge__ = None
        self.__getattribute__ = None
        self.__gt__ = None
        self.__hash__ = None
        self.__init__ = None
        self.__le__ = None
        self.__lt__ = None
        self.__ne__ = None
        self.__new__ = None
        self.__reduce__ = None
        self.__reduce_ex__ = None
        self.__repr__ = None
        self.__setattr__ = None
        self.__sizeof__ = None
        self.__str__ = None
        self.__subclasshook__ = None
        self.co_argcount = None
        self.co_cellvars = None
        self.co_code = None
        self.co_consts = None
        self.co_filename = None
        self.co_firstlineno = None
        self.co_flags = None
        self.co_freevars = None
        self.co_kwonlyargcount = None
        self.co_lnotab = None
        self.co_name = None
        self.co_names = None
        self.co_nlocals = None
        self.co_stacksize = None
        self.co_varnames = None
        raise NotImplementedError( "type hinting only - not intended for construction" )


class IFunctionBase:
    """
    Interface for function object (for Intellisense only)
    """
    
    
    def __init__( self ):
        self.__annotations__ = None
        self.__call__ = None
        self.__class__ = None
        self.__closure__ = None
        self.__code__ = ICode()
        self.__defaults__ = None
        self.__delattr__ = None
        self.__dict__ = None
        self.__dir__ = None
        self.__doc__ = None
        self.__eq__ = None
        self.__format__ = None
        self.__ge__ = None
        self.__get__ = None
        self.__getattribute__ = None
        self.__globals__ = None
        self.__gt__ = None
        self.__hash__ = None
        self.__init__ = None
        self.__kwdefaults__ = None
        self.__le__ = None
        self.__lt__ = None
        self.__module__ = None
        self.__name__ = None
        self.__ne__ = None
        self.__new__ = None
        self.__qualname__ = None
        self.__reduce__ = None
        self.__reduce_ex__ = None
        self.__repr__ = None
        self.__setattr__ = None
        self.__sizeof__ = None
        self.__str__ = None
        self.__subclasshook__ = None
        raise NotImplementedError( "type hinting only - not intended for construction" )


IFunction = Union[IFunctionBase, Callable]


class FnArg:
    """
    Function argument details
    """
    
    
    def __init__( self, name: str, annotation: AnnotationInspector, default: Optional[object], description: Optional[str] ):
        """
        CONSTRUCTOR
        :param name:                Name of the argument 
        :param annotation:          Type of the argument, if annotated, else `None` 
        :param description:         Description of the argument, if provided, else `""` 
        :param default:             Default value of the argument, if provided, else `NOT_PROVIDED` 
        """
        if not isinstance( annotation, AnnotationInspector ):
            annotation = AnnotationInspector( annotation )
        
        self.name = name
        self.annotation = annotation
        self.description = description
        self.default = default
    
    
    def __repr__( self ):
        return "FnArg({} : {} = {} #{})".format( self.name, self.annotation, self.default, self.description )
    
    
    def __str__( self ):
        return "{} : {} = {}".format( self.name, self.annotation, self.default )
    
    
    @property
    def type( self ):
        warnings.warn( "Deprecated - use annotation", DeprecationWarning )
        return self.annotation


class FnInspect:
    """
    Class for inspecting a function.
    """
    
    
    def __init__( self, fn: IFunction ):
        self.function = fn  # type: IFunction
        
        self.name = fn.__name__  # type: str
        self.args = []  # type: List[FnArg]
        
        arg_names = fn.__code__.co_varnames[:fn.__code__.co_argcount]
        
        arg_types = { }
        
        self.return_type = None
        
        for k, v in fn.__annotations__.items():
            if k != "return":
                arg_types[k] = v
            else:
                self.return_type = v
        
        doc = fn.__doc__  # type:str
        
        arg_descriptions = extract_documentation( doc, "param", False )
        
        arg_defaults = { }
        has_args = (fn.__code__.co_flags & 0x4) == 0x4
        has_kwargs = (fn.__code__.co_flags & 0x8) == 0x8
        
        if fn.__defaults__:
            num_defaults = len( fn.__defaults__ )
            default_offset = len( arg_names ) - num_defaults
            
            if has_args:
                default_offset -= 1
            
            if has_kwargs:
                default_offset -= 1
            
            for i, v in enumerate( fn.__defaults__ ):
                name = arg_names[default_offset + i]
                arg_defaults[name] = v
        
        for arg_name in arg_names:
            arg_desc_list = arg_descriptions.get( arg_name, None )
            arg_desc = "\n".join( arg_desc_list ) if arg_desc_list else ""
            arg_desc = string_helper.fix_indents( arg_desc )
            arg_type = arg_types.get( arg_name, None )
            arg_default = arg_defaults.get( arg_name, NOT_PROVIDED )
            
            if arg_type is None and arg_default is not NOT_PROVIDED and arg_default is not None:
                arg_type = type( arg_default )
            
            self.args.append( FnArg( arg_name, AnnotationInspector( arg_type ), arg_default, arg_desc ) )
        
        fn_desc = "\n".join( arg_descriptions[""] )
        fn_desc = string_helper.fix_indents( fn_desc )
        
        self.description = fn_desc
    
    
    def __str__( self ):
        return str( self.function )
    
    
    def call( self, *args, **kwargs ):
        """
        Calls the function.
        """
        # noinspection PyCallingNonCallable
        return self.function( *args, **kwargs )


def extract_documentation( doc, param_keyword = "param", as_string = True ) -> Union[Dict[str, str], Dict[str, List[str]]]:
    """
    Extracts the documentation into a dictionary
    :param doc:             Documentation string
    :param param_keyword:   Keyword to use for parameters, e.g. "param" 
    :param as_string:       `True`: Return each entry as a `str` with "\n" for or newline
                            `False`: Return each entry as a `list` with a `str` on each line.
                            
    :return:                Dictionary of argument name vs. documentation. The primary documentation is under the param name `""`.
    """
    arg_descriptions = { }
    
    param_keyword = ":{} ".format( param_keyword )
    current_desc = []
    arg_descriptions[""] = current_desc
    current_indent = -1
    if doc is not None:
        for line in doc.split( "\n" ):
            if line.lstrip().startswith( param_keyword ):
                line = line.replace( param_keyword, " " * len( param_keyword ) )
                name = line.split( ":", 1 )[0]
                line = line.replace( name, " " * len( name ), 1 )
                line = line.replace( ":", " ", 1 )
                current_indent = string_helper.get_indent( line )
                current_name = name.strip()
                current_desc = [string_helper.remove_indent( current_indent, line )]
                arg_descriptions[current_name] = current_desc
            elif not line.lstrip().startswith( ":" ):
                if current_indent == -1:
                    current_indent = string_helper.get_indent( line )
                
                current_desc.append( string_helper.remove_indent( current_indent, line ) )
            else:
                current_desc = []
    
    if as_string:
        for k in list( arg_descriptions.keys() ):
            arg_descriptions[k] = "\n".join( arg_descriptions[k] ).strip()
    
    return arg_descriptions


class ArgsKwargs:
    def __init__( self, *args, **kwargs ) -> None:
        self.args = args
        self.kwargs = kwargs


class _FnArgValue:
    def __init__( self, arg: FnArg, value: object ):
        self.arg = arg
        self.__value = value
    
    
    @property
    def value( self ) -> object:
        return self.__value
    
    
    @value.setter
    def value( self, value: object ):
        if not self.arg.annotation.is_viable_instance( value ):
            msg = "Trying to set the value «{}» on the argument «{}» but the value is of type «{}» and the argument takes «{}»."
            raise TypeError( msg.format( value, self.arg.name, type( value ), self.arg.annotation ) )
        
        self.__value = value


class FnArgValueCollection:
    """
    Manages a set of arguments and their values.
    """
    
    
    def __init__( self, args: Iterable[FnArg], provided: ArgsKwargs = None ):
        """
        CONSTRUCTOR
        :param provided:    Values to apply to the arguments
        """
        self.__values: Dict[str, _FnArgValue] = OrderedDict()
        
        for arg in args:
            self.__values[arg.name] = _FnArgValue( arg, arg.default )
        
        if provided:
            if len( provided.args ) > len( self.__values ):
                raise ValueError( "Attempt to specify {} values but this function takes {}.".format( len( provided.args ), len( self.__values ) ) )
            
            for arg, value in zip( self.__values.values(), provided.args ):
                arg.value = value
            
            for key, value in provided.kwargs.items():
                try:
                    self.__values[key].value = value
                except KeyError as ex:
                    raise KeyError( "There is no argument named «{}».".format( key ) )
    
    
    def tokwargs( self ) -> Dict[str, object]:
        """
        Converts the arguments to kwargs that can be passed to a method.
        Only the arguments of type `HFunctionParameterType[T]` are passed through, where T indicates the type passed to the function.
        
        Note: Since all plugin arguments must be named and plugins do not currently support variadic arguments, there is no equivalent `toargs`.
        """
        result = { }
        
        for arg in self.__values.values():
            if arg.value is not NOT_PROVIDED:
                result[arg.arg.name] = arg.value
        
        return result
    
    
    def __len__( self ):
        return len( self.__values )
    
    
    def __iter__( self ) -> Iterator[FnArg]:
        return iter( x.arg for x in self.__values.values() )
    
    
    def items( self ) -> Iterable[Tuple[FnArg, object]]:
        for name, value in self.__values.items():
            yield self.get_arg( name ), value.value
    
    
    def __get_argvalue( self, key: Union[FnArg, str] ) -> _FnArgValue:
        if isinstance( key, FnArg ):
            key = key.name
        
        return self.__values[key]
    
    
    def get_value( self, key: Union[FnArg, str] ) -> Optional[object]:
        """
        Equivalent to `get_arg`, but returns the value on the `PluginArgValue`.
        """
        return self.__get_argvalue( key ).value
    
    
    def set_value( self, key: Union[FnArg, str], value: Optional[object] ) -> None:
        """
        Sets the value of the argument with the specified key.
        See `PluginArgValue.set_value` for details on accepted values.

        :param key:     A `PluginArg`. Unlike `get` a name is not accepted.
        :param value:   The value to apply.
        """
        self.__get_argvalue( key ).value = value
    
    
    def get_arg( self, key: Union[FnArg, str] ) -> "FnArg":
        """
        Retrieves the `PluginArgValue` of the specified `PluginArg` or `str` (name).

        :except KeyError:  If the argument does not exist
        :except TypeError: If the argument is not a `PluginArg` or `str`.
        """
        return self.__get_argvalue( key ).arg
    
    
    def get_incomplete( self ) -> List[str]:
        """
        Returns the set of arguments that require a value to be set before run() is called
        """
        return [x.arg.name for x in self.__values.values() if x.value is NOT_PROVIDED]


HNotFunctionParameterType = MAnnotationFactory( "HNotFunctionParameterType" )
