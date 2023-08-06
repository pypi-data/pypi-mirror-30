from __future__ import print_function

import abc
import itertools
import sys
from collections import defaultdict
from enum import Enum

from typing import Union, List, Any, Callable, Type, Dict, Set

from yattag import Doc

from pytconf.color_utils import print_highlight, color_hi, print_title, color_ok, color_warn, print_warn
from pytconf.convert import convert_string_to_int, convert_int_to_string, \
    convert_string_to_list_int, \
    convert_list_int_to_string, convert_string_to_list_str, convert_list_str_to_string, convert_string_to_string, \
    convert_string_to_bool, convert_bool_to_string, convert_string_to_int_or_none, convert_int_or_none_to_string, \
    convert_string_to_int_default
from pytconf.enum_subset import EnumSubset
from pytconf.extended_enum import str_to_enum_value, enum_type_to_list_str

from six import with_metaclass

PARAMS_ATTRIBUTE = "_params"
DEFAULT_GROUP_NAME = "default"
SPECIAL_COMMANDS = {"help", "help-suggest", "help-all"}


class HtmlGen(object):
    def __init__(self):
        document, tag, text, line = Doc().ttl()
        self.document = document
        self.tag = tag
        self.text = text
        self.line = line


class PytconfConf(object):
    def __init__(self):
        self._configs = set()
        self._config_names = set()
        self.main_function = None
        self.function_name_to_configs = dict()  # type: Dict[str, List[Config]]
        self.function_name_to_suggest_configs = dict()  # type: Dict[str, List[Config]]
        self.function_name_to_callable = dict()  # type: Dict[str, Callable]
        self.function_group_names = defaultdict(set)  # type: Dict[str, Set[str]]
        self.function_group_descriptions = dict()  # type: Dict[str, str]
        self.function_group_list = []

    def register_main(self, f):
        self.main_function = f

    def register_config(self, cls, name):
        """
        register a configuration class
        :param cls:
        :param name:
        :return:
        """
        self._configs.add(cls)
        self._config_names.add(name)

    @classmethod
    def print_errors(cls, errors):
        # type: (List[str]) -> None
        if errors:
            print()
            for error in errors:
                print_warn(error)
            print()

    def show_help(self):
        # type: () -> None
        print("Usage: {} [OPTIONS] COMMAND [ARGS]...".format(self.main_function.__name__))
        doc = self.main_function.__doc__
        if doc is not None:
            print()
            doc = doc.strip()
            doc = "\n".join(map(lambda x: "  {}".format(x.strip()), doc.split("\n")))
            print_highlight("{}".format(doc))
        print()
        print("Options:")
        print("  --help         Show mandatory help")
        print("  --help-suggest Show mandatory+suggestions help")
        print("  --help-all    Show all help")
        print()
        print("Commands:")
        for function_group in self.function_group_list:
            description = self.function_group_descriptions[function_group]
            print("  {}: {}".format(function_group, description))
            for name in sorted(self.function_group_names[function_group]):
                f = self.function_name_to_callable[name]
                doc = f.__doc__
                if doc is None:
                    print_highlight("    {}".format(name))
                else:
                    doc = doc.strip()
                    print("    {}: {}".format(color_hi(name), doc))
            print()

    def show_help_for_function(self, function_name, show_help_full, show_help_suggest):
        # type: (str, bool, bool) -> None

        print("Usage: {} {} [OPTIONS] [ARGS]...".format(
            self.main_function.__name__,
            function_name,
        ))
        function_selected = self.function_name_to_callable[function_name]
        doc = function_selected.__doc__
        if doc is not None:
            doc = doc.strip()
            print()
            print_highlight("  {}".format(doc))
        print()
        print("Options:")
        print()
        for config in self.function_name_to_configs[function_name]:
            self.show_help_for_config(config)
        if show_help_suggest:
            for config in self.function_name_to_suggest_configs[function_name]:
                self.show_help_for_config(config)
        if show_help_full:
            for config in self._configs:
                self.show_help_for_config(config)

    @classmethod
    def show_help_for_config(cls, config):
        if config == Config:
            return
        doc = config.__doc__
        if doc is not None:
            doc = doc.strip()
            print_title("  {}".format(doc))
        else:
            print_title("  Undocumented parameter set")
        for name, param in config.get_params().items():
            if param.default is NO_DEFAULT:
                default = color_warn("MANDATORY")
            else:
                default = color_ok(param.t2s(param.default))
            print("    {} [{}]: {} [{}]".format(
                color_hi(name),
                param.get_type_name(),
                param.help_string,
                default,
            ))
            more_help = param.more_help()
            if more_help is not None:
                print("      {}".format(more_help))
        print()

    def parse_args(self, command_selected, flags, _free_args):
        # type: (str, Dict[str, str], List[str]) -> bool
        """
        Parse the args and fill the global data
        Currently we disregard the free parameters
        :param command_selected:
        :param flags:
        :param _free_args:
        :return:
        """
        configs = self.function_name_to_configs[command_selected]
        suggested_configs = self.function_name_to_suggest_configs[command_selected]

        # create the attribute_to_config map
        attribute_to_config = dict()  # type: Dict[str, Config]
        for config in itertools.chain(configs, suggested_configs):
            for attribute in config.get_attributes():
                if attribute in attribute_to_config:
                    raise ValueError("attribute [{}] double".format(attribute))
                attribute_to_config[attribute] = config

        # set the flags into the "default" field
        unknown_flags = []
        for flag_raw, value in flags.items():
            edit = value.startswith('=')
            if flag_raw not in attribute_to_config:
                unknown_flags.append(flag_raw)
            config = attribute_to_config[flag_raw]
            param = config.get_param_by_name(flag_raw)
            if edit:
                v = param.s2t_generate_from_default(value[1:])
            else:
                v = param.s2t(value)
            setattr(config, flag_raw, v)

        # check for missing parameters and show help if there are any missing
        missing_parameters = []
        for config in configs:
            for attribute in config.get_attributes():
                value = getattr(config, attribute)
                if value is NO_DEFAULT:
                    missing_parameters.append(attribute)
        if unknown_flags or missing_parameters:
            if missing_parameters:
                print()
                print_warn("missing parameters [{}]".format(",".join(missing_parameters)))
            if unknown_flags:
                print()
                print_warn("unknown flags [{}]".format(",".join(unknown_flags)))
            print("problems found, not running")
            print()
            self.show_help_for_function(command_selected, show_help_full=False, show_help_suggest=False)
            return False

        # move all default values to place
        for config in itertools.chain(configs, self._configs):
            for attribute in config.get_attributes():
                param = getattr(config, attribute)  # type: Param
                if isinstance(param, Param):
                    if param.default is not NO_DEFAULT:
                        setattr(config, attribute, param.default)
        return True

    def config_arg_parse_and_launch(self):
        # we don't need the first argument which is the script path
        args = sys.argv[1:]  # type: List[str]
        # name of arg and it's value
        flags = dict()  # type: Dict[str, str]
        special_flags = set()
        errors = []  # type: List[str]
        free_args = []
        while args:
            current = args.pop(0)
            if current.startswith("--"):
                real = current[2:]
                number_of_equals = real.count("=")
                if number_of_equals == 1:
                    flag_name, flag_value = real.split("=")
                    flags[flag_name] = flag_value
                elif number_of_equals == 0:
                    if args:
                        more = args.pop(0)
                        flags[real] = more
                    elif real in SPECIAL_COMMANDS:
                        special_flags.add(real)
                    else:
                        errors.append("argument [{}] needs a follow-up argument".format(real))
                else:
                    errors.append("can not parse argument [{}]".format(real))
            else:
                free_args.append(current)
        show_help = False
        show_help_full = False
        show_help_suggest = False

        if len(errors) > 0:
            show_help = True

        if "help" in special_flags:
            show_help = True
        if "help-suggest" in special_flags:
            show_help = True
            show_help_suggest = True
        if "help-all" in special_flags:
            show_help = True
            show_help_full = True

        command_selected = None
        if len(free_args) >= 1:
            command = free_args.pop(0)
            if command in self.function_name_to_callable:
                command_selected = command
            else:
                errors.append("Unknown command [{}]".format(command))

        if len(self.function_name_to_callable) == 1:
            for name in self.function_name_to_callable.keys():
                command_selected = name

        if len(free_args) > 0:
            errors.append("free args are not allowed")

        if show_help or errors or command_selected is None:
            self.print_errors(errors)
            if command_selected:
                self.show_help_for_function(command_selected, show_help_full, show_help_suggest)
            else:
                self.show_help()
        else:
            f = self.function_name_to_callable[command_selected]
            if self.parse_args(command_selected, flags, free_args):
                f()

    def get_html(self):
        # type: () -> None
        html_gen = HtmlGen()
        doc = self.main_function.__doc__
        assert doc is not None
        doc = doc.strip()
        html_gen.line('h1', doc)
        html_gen.line('h2', "API specifications")
        with html_gen.tag('ul'):
            for function_group_name in self.function_group_list:
                function_group_description = self.function_group_descriptions[function_group_name]
                html_gen.line('li', function_group_name, title='function group name: ')
                html_gen.line('li', function_group_description, title='function group description: ')
                with html_gen.tag('li'):
                    for function_name in sorted(self.function_group_names[function_group_name]):
                        self.get_html_for_function(function_name, html_gen)
        return html_gen.document.getvalue()

    def get_html_for_function(self, function_name, html_gen):
        with html_gen.tag('ul'):
            f = self.function_name_to_callable[function_name]
            if f.__doc__ is None:
                function_doc = "not description for this function"
            else:
                function_doc = f.__doc__.strip()
            html_gen.line('li', function_name, title='function name: ')
            html_gen.line('li', function_doc, title='function description: ')
            with html_gen.tag('li'):
                with html_gen.tag('ul'):
                    for config in self.function_name_to_configs[function_name]:
                        with html_gen.tag('li'):
                            self.get_html_for_config(config, html_gen)

    @classmethod
    def get_html_for_config(cls, config, html_gen):
        if config == Config:
            return
        if config.__doc__ is not None:
            doc = config.__doc__.strip()
        else:
            doc = "undocumented config"
        html_gen.line('h3', doc, title='config: ')
        with html_gen.tag('table'):
                for name, param in config.get_params().items():
                    with html_gen.tag('tr'):
                        if param.default is NO_DEFAULT:
                            default = "MANDATORY"
                        else:
                            default = param.t2s(param.default)
                        if param.more_help() is None:
                            more_help = "No more help is documented"
                        else:
                            more_help = param.more_help()
                        html_gen.line('td', name)
                        html_gen.line('td', param.help_string)
                        html_gen.line('td', param.get_type_name())
                        html_gen.line('td', default)
                        html_gen.line('td', more_help)


_pytconf = PytconfConf()


def get_pytconf():
    return _pytconf


def config_arg_parse_and_launch():
    """
    backwards compatibility function
    :return:
    """
    get_pytconf().config_arg_parse_and_launch()


class MetaConfig(type):
    """
    base class for all configs
    """
    def __new__(mcs, name, bases, cls_dict):
        if name != "Config":
            params_dict = dict()
            cls_dict[PARAMS_ATTRIBUTE] = params_dict
            for k, d in cls_dict.items():
                if isinstance(d, Param):
                    # assert d.default is not NO_DEFAULT
                    params_dict[k] = d
                    cls_dict[k] = d.default
        return type.__new__(mcs, name, bases, cls_dict)

    def __init__(cls, name, bases, cls_dict):
        # print(name, bases, cls_dict)
        # if len(cls.mro()) > 2:
        #     register_config(cls, name)
        #     # print("was subclassed by " + name)
        if name != "Config":
            get_pytconf().register_config(cls, name)
        # print(name, cls_dict)
        super(MetaConfig, cls).__init__(name, bases, cls_dict)


class Config(with_metaclass(MetaConfig, object)):
    """
        base class for all configs
    """

    @classmethod
    def get_attributes(cls):
        # type: (Any) -> List[str]
        return getattr(cls, PARAMS_ATTRIBUTE).keys()
        # return [attr for attr in dir(cls) if not callable(getattr(cls, attr))
        #        and not attr.startswith("__")]

    @classmethod
    def get_params(cls):
        # type: (Any) -> Dict[str, Param]
        return getattr(cls, PARAMS_ATTRIBUTE)

    @classmethod
    def get_param_by_name(cls, name):
        # type: (Any, str) -> Param
        return cls.get_params()[name]


NO_DEFAULT = {}
NO_DEFAULT_TYPE = Dict
NO_HELP = "No help for this configuration option"


class Param(object):
    __metaclass__ = abc.ABCMeta
    """
        Parent class of all parameters of configuration
    """

    def __init__(
            self,
            help_string=NO_HELP,
            default=NO_DEFAULT,
            type_name=None,
    ):
        super(Param, self).__init__()
        self.help_string = help_string
        self.default = default
        self.type_name = type_name

    def get_type_name(self):
        return self.type_name

    @abc.abstractmethod
    def s2t(self, s):
        # type: (str) -> object
        pass

    def s2t_generate_from_default(self, s):
        # type: (str) -> object
        raise ValueError("we do not support generation from default")

    @abc.abstractmethod
    def t2s(self, t):
        # type: (object) -> str
        pass

    # noinspection PyMethodMayBeStatic
    def more_help(self):
        # type: () -> Union[str, None]
        return None


class ParamFunctions(Param):
    """
    Parent class of all parameters of configuration
    """

    def __init__(
            self,
            help_string=NO_HELP,
            default=NO_DEFAULT,
            type_name=None,
            function_s2t=None,  # type: Callable
            function_s2t_generate_from_default=None,  # type: Callable
            function_t2s=None,  # type: Callable
    ):
        super(ParamFunctions, self).__init__(
            help_string=help_string,
            default=default,
            type_name=type_name,
        )
        self.function_s2t = function_s2t
        self.function_t2s = function_t2s
        self.function_s2t_generate_from_default = function_s2t_generate_from_default

    def s2t(self, s):
        # type: (str) -> Any
        return self.function_s2t(s)

    def s2t_generate_from_default(self, s):
        # type: (str) -> Any
        return self.function_s2t_generate_from_default(self.default, s)

    def t2s(self, t):
        # type: (Any) -> str
        return self.function_t2s(t)


class ParamFilename(Param):
    def __init__(
            self,
            help_string=NO_HELP,
            default=NO_DEFAULT,
            type_name=None,
            suffixes=None,  # type: List[str]
    ):
        super(ParamFilename, self).__init__(
            help_string=help_string,
            default=default,
            type_name=type_name,
        )
        self.suffixes = suffixes

    def s2t(self, s):
        if self.suffixes is not None:
            assert any(s.endswith(x) for x in self.suffixes), "filename suffix is not accepted"
        return s

    def t2s(self, t):
        return t

    def more_help(self):
        if self.suffixes is None:
            return "no limitation on suffixes"
        else:
            return "allowed suffixes are {}".format(self.suffixes)


class ParamEnum(Param):
    def __init__(
            self,
            help_string=NO_HELP,
            default=NO_DEFAULT,
            enum_type=None,  # type: Type[Enum]
    ):
        super(ParamEnum, self).__init__(
            help_string=help_string,
            default=default,
            type_name="enum",
        )
        self.enum_type = enum_type

    def get_type_name(self):
        return "Enum[{}]".format(self.enum_type.__name__)

    def s2t(self, s):
        # type: (str) -> Any
        return str_to_enum_value(s, self.enum_type)

    def t2s(self, t):
        # type: (Any) -> str
        return t.name

    def more_help(self):
        return "allowed values {}".format(enum_type_to_list_str(self.enum_type))


class ParamEnumSubset(Param):
    def __init__(
            self,
            help_string=NO_HELP,
            default=NO_DEFAULT,
            enum_type=None,  # type: Type[Enum]
    ):
        super(ParamEnumSubset, self).__init__(
            help_string=help_string,
            default=default,
            type_name="enum",
        )
        self.enum_type = enum_type

    def get_type_name(self):
        return "EnumSubset[{}]".format(self.enum_type.__name__)

    def s2t(self, s):
        # type: (str) -> EnumSubset
        return EnumSubset.from_string(e=self.enum_type, s=s)

    def t2s(self, t):
        # type: (EnumSubset) -> str
        return t.to_string()

    def s2t_generate_from_default(self, s):
        # type: (str) -> EnumSubset
        pass

    def more_help(self):
        return "allowed values {}".format(enum_type_to_list_str(self.enum_type))


class ParamChoice(Param):
    def __init__(
            self,
            help_string=NO_HELP,
            default=NO_DEFAULT,
            choice_list=None,  # type: List[str]
    ):
        super(ParamChoice, self).__init__(
            help_string=help_string,
            default=default,
            type_name="Choice",
        )
        self.choice_list = choice_list

    def s2t(self, s):
        # type: (str) -> Any
        return s

    def t2s(self, t):
        # type: (Any) -> str
        return t

    def more_help(self):
        return "allowed values {}".format(",".join(self.choice_list))


class ParamCreator(object):
    """
    Static namespace with all the param creation functions.
    """

    @staticmethod
    def create_int(help_string=NO_HELP, default=NO_DEFAULT):
        # type: (str, Union[int, NO_DEFAULT_TYPE]) -> int
        """
        Create an int parameter
        :param help_string:
        :param default:
        :return:
        """
        # noinspection PyTypeChecker
        return ParamFunctions(
            help_string=help_string,
            default=default,
            type_name="int",
            function_s2t=convert_string_to_int,
            function_t2s=convert_int_to_string,
            function_s2t_generate_from_default=convert_string_to_int_default,
        )

    @staticmethod
    def create_list_int(help_string=NO_HELP, default=NO_DEFAULT):
        # type: (str, Union[List[int], NO_DEFAULT_TYPE]) -> List[int]
        """
        Create a List[int] parameter
        :param help_string:
        :param default:
        :return:
        """
        # noinspection PyTypeChecker
        return ParamFunctions(
            help_string=help_string,
            default=default,
            type_name="List[int]",
            function_s2t=convert_string_to_list_int,
            function_t2s=convert_list_int_to_string,
        )

    @staticmethod
    def create_list_str(help_string=NO_HELP, default=NO_DEFAULT):
        # type: (str, Union[List[str], NO_DEFAULT_TYPE]) -> List[str]
        """
        Create a List[str] parameter
        :param help_string:
        :param default:
        :return:
        """
        # noinspection PyTypeChecker
        return ParamFunctions(
            help_string=help_string,
            default=default,
            type_name="List[str]",
            function_s2t=convert_string_to_list_str,
            function_t2s=convert_list_str_to_string,
        )

    @staticmethod
    def create_int_or_none(help_string=NO_HELP, default=NO_DEFAULT):
        # type: (str, Union[int, None, NO_DEFAULT_TYPE]) -> Union[int, None]
        """
        Create an int parameter
        :param help_string:
        :param default:
        :return:
        """
        # noinspection PyTypeChecker
        return ParamFunctions(
            help_string=help_string,
            default=default,
            type_name="Union[int, None]",
            function_s2t=convert_string_to_int_or_none,
            function_t2s=convert_int_or_none_to_string,
        )

    @staticmethod
    def create_str(help_string=NO_HELP, default=NO_DEFAULT):
        # type: (str, Union[str, NO_DEFAULT_TYPE]) -> str
        """
        Create a string parameter
        :param help_string:
        :param default:
        :return:
        """
        # noinspection PyTypeChecker
        return ParamFunctions(
            help_string=help_string,
            default=default,
            type_name="str",
            function_s2t=convert_string_to_string,
            function_t2s=convert_string_to_string,
        )

    @staticmethod
    def create_bool(help_string=NO_HELP, default=NO_DEFAULT):
        # type: (str, Union[bool, NO_DEFAULT_TYPE]) -> bool
        """
        Create a bool parameter
        :param help_string:
        :param default:
        :return:
        """
        # noinspection PyTypeChecker
        return ParamFunctions(
            help_string=help_string,
            default=default,
            type_name="bool",
            function_s2t=convert_string_to_bool,
            function_t2s=convert_bool_to_string,
        )

    @staticmethod
    def create_new_file(help_string=NO_HELP, default=NO_DEFAULT, suffixes=None):
        # type: (str, Union[str, NO_DEFAULT_TYPE], Union[List[str], None]) -> str
        """
        Create a new file parameter
        :param help_string:
        :param default:
        :param suffixes:
        :return:
        """
        # noinspection PyTypeChecker
        return ParamFilename(
            help_string=help_string,
            default=default,
            type_name="new_file",
            suffixes=suffixes,
        )

    @staticmethod
    def create_existing_file(help_string=NO_HELP, default=NO_DEFAULT, suffixes=None):
        # type: (str, Union[str, NO_DEFAULT_TYPE], Union[List[str], None]) -> str
        """
        Create a new file parameter
        :param help_string:
        :param default:
        :param suffixes:
        :return:
        """
        # noinspection PyTypeChecker
        return ParamFilename(
            help_string=help_string,
            default=default,
            type_name="existing_file",
            suffixes=suffixes,
        )

    @staticmethod
    def create_existing_folder(help_string=NO_HELP, default=NO_DEFAULT, suffixes=None):
        # type: (str, Union[str, NO_DEFAULT_TYPE], Union[List[str], None]) -> str
        """
        Create a new folder parameter
        :param help_string:
        :param default:
        :param suffixes:
        :return:
        """
        # noinspection PyTypeChecker
        return ParamFilename(
            help_string=help_string,
            default=default,
            type_name="existing_folder",
            suffixes=suffixes,
        )

    @staticmethod
    def create_choice(choice_list, help_string=NO_HELP, default=NO_DEFAULT):
        # type: (List[str], str, Union[Any, NO_DEFAULT_TYPE]) -> str
        """
        Create a choice config
        :param choice_list:
        :param help_string:
        :param default:
        :return:
        """
        # noinspection PyTypeChecker
        return ParamChoice(
            help_string=help_string,
            default=default,
            choice_list=choice_list,
        )

    @staticmethod
    def create_enum(enum_type, help_string=NO_HELP, default=NO_DEFAULT):
        # type: (Type[Enum], str, Union[Any, NO_DEFAULT_TYPE]) -> Type[Enum]
        """
        Create an enum config
        :param enum_type:
        :param help_string:
        :param default:
        :return:
        """
        # noinspection PyTypeChecker
        return ParamEnum(
            help_string=help_string,
            default=default,
            enum_type=enum_type,
        )

    @staticmethod
    def create_enum_subset(enum_type, help_string=NO_HELP, default=NO_DEFAULT):
        # type: (Type[Enum], str, EnumSubset) -> EnumSubset
        """
        Create an enum config
        :param enum_type:
        :param help_string:
        :param default:
        :return:
        """
        # noinspection PyTypeChecker
        return ParamEnumSubset(
            help_string=help_string,
            default=default,
            enum_type=enum_type,
        )

    @staticmethod
    def create_existing_bucket(help_string=NO_HELP, default=NO_DEFAULT):
        # type: (str, Union[str, NO_DEFAULT_TYPE]) -> str
        """
        Create a bucket name on gcp
        :param help_string:
        :param default:
        :return:
        """
        # noinspection PyTypeChecker
        return ParamFunctions(
            help_string=help_string,
            default=default,
            type_name="bucket_name",
            function_s2t=convert_string_to_string,
            function_t2s=convert_string_to_string,
        )


def register_function_group(function_group_name, function_group_description):
    # type: (str, str) -> None
    pt = get_pytconf()
    pt.function_group_descriptions[function_group_name] = function_group_description
    pt.function_group_list.append(function_group_name)


def register_main():
    # type: () -> Callable
    def identity(f):
        get_pytconf().register_main(f)
        return f
    return identity


def register_endpoint(configs=(), suggest_configs=(), group=DEFAULT_GROUP_NAME):
    # type: (List[Config], List[Config]) -> Callable
    def identity(f):
        pt = get_pytconf()
        function_name = f.__name__
        pt.function_name_to_callable[function_name] = f
        pt.function_name_to_configs[function_name] = configs
        pt.function_name_to_suggest_configs[function_name] = suggest_configs
        pt.function_group_names[group].add(function_name)
        return f
    return identity






