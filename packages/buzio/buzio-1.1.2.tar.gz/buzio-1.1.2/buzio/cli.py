# -*- coding: utf-8 -*-
"""Buzio main code.

This is the main code for Buzio Package
It contains the Console class.

Return
------
    * console (obj) = Console instance
    * formatStr (obj) = Console instance with format_only=True
"""
from __future__ import print_function
import datetime
import gettext
import os
import platform
import subprocess
import sys
from colorama import Fore, Style
from unidecode import unidecode

args = {
    'domain': 'messages',
    'localedir': os.path.join('..', 'locale'),
    'fallback': True
}

t = gettext.translation(**args)
_ = t.gettext


def get_terminal_size():
    """Function: get_terminal_size.

    Try to find terminal size using get_terminal_size
    on Python 3 and 'tput' commands for Python 2.
    Limited use on Windows: just returns (80, 25)

    Return
    ------
        Tuple of Int: (col, lines)
    """
    try:
        from shutil import get_terminal_size
        return get_terminal_size(fallback=(80, 24))
    except ImportError:
        if platform.system() == "Windows":
            return (80, 25)
        cols = int(subprocess.check_output(
            'tput cols',
            shell=True,
            stderr=subprocess.STDOUT
        ))
        lines = int(subprocess.check_output(
            'tput lines',
            shell=True,
            stderr=subprocess.STDOUT
        ))
        return (cols, lines)


class Console():
    """Console class.

    Attributes:
        DEFAULT_THEMES (Dict): Default color theme
        format_only (bool): Print or format string only
        prefix (bool): Append prefix on text?
        text (str): text to be formatted/printed
        theme (str): theme selected for print/format
        theme_dict (dict): theme dictionary loaded
        transform (str): keywords for transform text
    """

    DEFAULT_THEMES = {
        'box': Fore.CYAN,
        'choose': Fore.LIGHTYELLOW_EX,
        'confirm': Fore.LIGHTMAGENTA_EX,
        'error': Fore.RED,
        'info': Fore.CYAN,
        'section': Fore.LIGHTYELLOW_EX,
        'success': Fore.GREEN,
        'warning': Fore.YELLOW,
        'dark': Fore.WHITE + Style.DIM
    }

    def __init__(self, format_only=False, default_prefix="",
                 default_transform="", default_theme="",
                 theme_dict=DEFAULT_THEMES):
        """
        Function: __init__
        Summary: InsertHere
        Examples: InsertHere

        Attributes:
            Returns: InsertHere

        Args:
            format_only (bool, optional): Description
            theme_dict (TYPE, optional): Description
        """
        self.format_only = format_only
        self.theme_dict = theme_dict
        self.transform = default_transform
        self.theme = default_theme
        self.prefix = default_prefix

    def _get_style(self):
        """Summary

        Returns:
            TYPE: Description

        Raises:
            ValueError: Description
        """
        if not isinstance(self.theme_dict, dict):
            raise ValueError("Themes List must be a dictionary.")

        return self.theme_dict.get(self.theme, "")

    def _humanize(self, obj, **kwargs):
        """Summary

        Args:
            obj (TYPE): Description

        Returns:
            TYPE: Description
        """
        if obj is None:
            ret = "--"
        elif isinstance(obj, str):
            ret = obj
        elif isinstance(obj, bool):
            ret = _("Yes") if obj else _("No")
        elif isinstance(obj,
                        (datetime.datetime, datetime.date, datetime.time)):
            date_format = kwargs.pop("date_format", False)
            if date_format:
                ret = obj.strftime(date_format)
            else:
                ret = obj.isoformat()
        elif isinstance(obj, list) or isinstance(obj, tuple):
            humanize_list = [
                self._humanize(data, **kwargs)
                for data in obj
            ]
            if self.transform and 'breakline' in self.transform:
                ret = "\n".join(humanize_list)
            else:
                ret = ", ".join(humanize_list)
        elif isinstance(obj, dict):
            if self.transform and 'show_counters' in self.transform:
                ret = "\n".join([
                    "({}) {}: {}".format(
                        i + 1,
                        key,
                        self._humanize(obj[key], **kwargs)
                    )
                    for i, key in enumerate(obj)
                ])
            else:
                ret = "\n".join([
                    "{}: {}".format(key, self._humanize(obj[key], **kwargs))
                    for key in obj
                ])
        else:
            ret = str(obj)

        return ret

    def _print(self, linebreak=False):
        """Summary

        Parameters
        ----------
        linebreak : bool, optional
            Description

        Returns
        -------
        TYPE
            Description
        """
        if self.prefix:
            if self.transform and 'breakline' in self.transform:
                self.text = "{}:\n{}".format(self.prefix, self.text)
            else:
                self.text = "{}: {}".format(self.prefix, self.text)

        if self.transform:
            if 'title' in self.transform:
                self.text = self.text.title()
            if 'upper' in self.transform:
                self.text = self.text.upper()
            if 'small' in self.transform:
                self.text = self.text.lower()

        if self.theme:
            self.text = [
                "{}{}{}{}".format(
                    Style.BRIGHT
                    if self.transform and 'bold' in self.transform else "",
                    self._get_style(),
                    line,
                    Style.NORMAL
                )
                for line in self.text.split("\n")
            ]

        if not self.format_only:
            print("\n".join(self.text), end="\n" if linebreak else "" + "\n")

        string = "{}".format("\n" if linebreak else "")
        return format(string.join(self.text))

    def _run_style(self, obj, theme, transform,
                   use_prefix, prefix, humanize, **kwargs):
        self.transform = transform
        self.text = self._humanize(obj, **kwargs) if humanize else obj
        self.prefix = prefix if use_prefix else ""
        self.theme = theme
        return self._print()

    def success(
            self,
            obj,
            theme="success",
            transform=None,
            use_prefix=True,
            prefix="Success",
            humanize=True,
            **kwargs):
        """
        Args:
            obj (TYPE): Description
            theme (str, optional): Description
            transform (None, optional): Description
            use_prefix (bool, optional): Description
            prefix (str, optional): Description
            humanize (bool, optional): Description

        Returns:
            TYPE: Description
        """
        return self._run_style(obj, theme, transform,
                               use_prefix, prefix, humanize, **kwargs)

    def info(
            self,
            obj,
            theme="info",
            transform=None,
            use_prefix=True,
            prefix="Info",
            humanize=True,
            **kwargs):
        """
        Args:
            obj (TYPE): Description
            theme (str, optional): Description
            transform (None, optional): Description
            use_prefix (bool, optional): Description
            prefix (str, optional): Description
            humanize (bool, optional): Description

        Returns:
            TYPE: Description
        """
        return self._run_style(obj, theme, transform,
                               use_prefix, prefix, humanize, **kwargs)

    def warning(
            self,
            obj,
            theme="warning",
            transform=None,
            use_prefix=True,
            prefix="Warning",
            humanize=True,
            **kwargs):
        """
        Args:
            obj (TYPE): Description
            theme (str, optional): Description
            transform (None, optional): Description
            use_prefix (bool, optional): Description
            prefix (str, optional): Description
            humanize (bool, optional): Description

        Returns:
            TYPE: Description
        """
        return self._run_style(obj, theme, transform,
                               use_prefix, prefix, humanize, **kwargs)

    def error(
            self,
            obj,
            theme="error",
            transform=None,
            use_prefix=True,
            prefix="Error",
            humanize=True,
            **kwargs):
        """
        Args:
            obj (TYPE): Description
            theme (str, optional): Description
            transform (None, optional): Description
            use_prefix (bool, optional): Description
            prefix (str, optional): Description
            humanize (bool, optional): Description

        Returns:
            TYPE: Description
        """
        return self._run_style(obj, theme, transform,
                               use_prefix, prefix, humanize, **kwargs)

    def section(
            self,
            obj,
            theme="section",
            transform=None,
            use_prefix=False,
            prefix="Section",
            full_width=False,
            humanize=True,
            **kwargs):
        """
        Args:
            obj (TYPE): Description
            theme (str, optional): Description
            transform (None, optional): Description
            use_prefix (bool, optional): Description
            prefix (str, optional): Description
            full_width (bool, optional): Description
            humanize (bool, optional): Description

        Returns:
            TYPE: Description
        """
        self.transform = transform
        self.text = self._humanize(obj, **kwargs) if humanize else obj
        if transform and 'center' in transform:
            format_text = "> {:^{num}} <"
            extra_chars = 4
        elif transform and 'right' in transform:
            format_text = "{:>{num}} <<"
            extra_chars = 3
        else:
            format_text = ">> {:<{num}}"
            extra_chars = 3
        if full_width:
            longest_line = get_terminal_size()[0]
        else:
            line_sizes = [
                len(line) + extra_chars
                for line in self.text.split("\n")
            ]
            longest_line = sorted(line_sizes, reverse=True)[0]
        main_lines = [
            format_text.format(line, num=longest_line - 4)
            for line in self.text.split("\n")
        ]
        bottom_line = "{:-^{num}}".format('', num=longest_line)
        self.text = "\n{}\n{}\n".format(
            "\n".join(main_lines),
            bottom_line
        )
        self.prefix = prefix if use_prefix else ""
        self.theme = theme
        return self._print()

    def box(self, obj, theme="box", transform=None, humanize=True, **kwargs):
        """
        Function: box
        Summary: InsertHere
        Examples: InsertHere

        Attributes:
            Returns: InsertHere

        Args:
            obj (TYPE): Description
            theme (str, optional): Description
            transform (None, optional): Description
            humanize (bool, optional): Description

        Returns:
            TYPE: Description
        """
        self.transform = transform
        self.text = self._humanize(obj, **kwargs) if humanize else obj
        line_sizes = [
            len(line)
            for line in self.text.split("\n")
        ]
        longest_line = sorted(line_sizes, reverse=True)[0]

        horizontal_line = "{:*^{num}}".format('', num=longest_line + 6)
        vertical_line = "*{:^{num}}*".format('', num=longest_line + 4)

        main_texts = [
            "*{:^{num}}*".format(
                text_line, num=longest_line + 4
            )
            for text_line in self.text.split("\n")
        ]
        self.text = "{}\n{}\n{}\n{}\n{}".format(
            horizontal_line,
            vertical_line,
            "\n".join(main_texts),
            vertical_line,
            horizontal_line
        )
        self.theme = theme
        self.prefix = None
        return self._print()

    def confirm(
            self,
            obj=None,
            theme="confirm",
            transform=None,
            humanize=True,
            default=None,
            **kwargs):
        """
        Args:
            obj (None, optional): Description
            theme (str, optional): Description
            transform (None, optional): Description
            humanize (bool, optional): Description
            default (None, optional): Description

        Returns:
            TYPE: Description

        Raises:
            ValueError: Description
        """
        if default is not None and not isinstance(default, bool):
            raise ValueError("Default must be a boolean")

        self.transform = transform
        if obj:
            self.text = self._humanize(obj, **kwargs) if humanize else obj
        else:
            self.text = _("Please confirm")
        answered = False
        self.text = "{} {}{} ".format(
            self.text,
            _("(y/n)"),
            "[{}]".format(self._humanize(default, **kwargs)[0])
            if default is not None else "")
        self.prefix = None
        self.theme = theme
        self._print(linebreak=False)
        if self.format_only:
            return self.text
        while not answered:
            ret = input(_("? "))
            if not ret and default is not None:
                ret = default
                answered = True
            elif ret and ret[0].upper() in \
                    [_("Yes")[0].upper(), _("No")[0].upper()]:
                answered = True
        return ret if isinstance(
            ret, bool) else ret[0].upper() == _("Yes")[0].upper()

    def choose(
            self,
            choices,
            question=None,
            theme="choose",
            transform=None,
            humanize=True,
            default=None,
            **kwargs):
        """
        Args:
            choices (TYPE): Description
            question (None, optional): Description
            theme (str, optional): Description
            transform (None, optional): Description
            humanize (bool, optional): Description
            default (None, optional): Description

        Returns:
            TYPE: Description

        Raises:
            ValueError: Description
        """
        if not isinstance(choices, list):
            raise ValueError("Choices must be a list")
        if default:
            found = [
                num
                for num, def_choice in enumerate(choices)
                if def_choice == default
            ]
            if found:
                default_index = found[0] + 1
            else:
                raise ValueError("Default object not found in choices")
        else:
            default_index = None

        self.transform = transform
        i = 1
        self.text = ""
        for choice in choices:
            self.text += "{}. {}\n".format(
                i,
                self._humanize(choice, **kwargs) if humanize else choice
            )
            i += 1
        answered = False
        self.theme = theme
        self.prefix = False
        self._print()
        if self.format_only:
            return self.text
        if not question:
            question = _("Select")
        while not answered:
            try:
                ret = input(
                    "{} (1-{}){}: ".format(
                        question,
                        i - 1,
                        "[{}] ".format(default_index) if default_index else ""
                    )
                )
                if not ret and default_index:
                    ret = default_index
                    answered = True
                elif ret and int(ret) in range(1, i):
                    answered = True
            except ValueError:
                pass
        return choices[int(ret) - 1]

    def unitext(self, obj, theme=None, transform=None,
                humanize=True, **kwargs):
        """
        Function: unitext
        Summary: InsertHere
        Examples: InsertHere

        Attributes:
            Returns: InsertHere

        Args:
            obj (TYPE): Description
            theme (None, optional): Description
            transform (None, optional): Description
            humanize (bool, optional): Description

        Returns:
            TYPE: Description
        """
        self.transform = transform
        self.text = self._humanize(obj, **kwargs) if humanize else obj
        if hasattr(str, 'decode'):
            self.text = self.text.decode("utf-8")
        self.text = unidecode(self.text)
        self.theme = theme
        self.prefix = False
        return self._print()

    def slugify(self, obj, humanize=True, **kwargs):
        """Summary

        Args:
            obj (TYPE): Description
            humanize (bool, optional): Description

        Returns:
            TYPE: Description
        """
        self.text = self._humanize(obj, **kwargs) if humanize else obj
        if hasattr(str, 'decode'):
            self.text = self.text.decode("utf-8")
        self.text = unidecode(self.text)
        self.text = self.text.strip().replace(" ", "_")
        self.text = self.text.lower()
        return self.text

    def progress(self, count, total, prefix=_('Reading'), theme=None,
                 suffix=_('Complete'), barLength=50, **kwargs):
        """
        Args:
            count (TYPE): Description
            total (TYPE): Description
            prefix (str, optional): Description
            theme (None, optional): Description
            suffix (str, optional): Description
            barLength (int, optional): Description

        Returns:
            TYPE: Description
        """
        formatStr = "{0:.2f}"
        percents = formatStr.format(100 * (count / float(total)))
        filledLength = int(round(barLength * count / float(total)))
        bar = '█' * filledLength + '-' * (barLength - filledLength)
        self.text = '\r{} |{}| {}% {} '.format(prefix, bar, percents, suffix)

        if not self.format_only:
            sys.stdout.write(self.text)
            sys.stdout.flush()

        return self.text

    def load_theme(self, theme):
        """
        Function: load_theme
        Summary: InsertHere
        Examples: InsertHere

        Attributes:
            Returns: InsertHere

        Args:
            theme (TYPE): Description

        Raises:
            ValueError: Description
        """
        if not isinstance(theme, dict):
            raise ValueError("Theme must be a dict")
        for key in theme:
            self.theme_dict[key] = theme[key]

    def ask(
            self,
            obj,
            theme="warning",
            transform=None,
            humanize=True,
            validator=None,
            default=None,
            required=False,
            **kwargs):
        """Summary

        Args:
            obj (TYPE): Description
            theme (str, optional): Description
            transform (None, optional): Description
            humanize (bool, optional): Description
            validator (None, optional): Description
            default (None, optional): Description
            required (bool, optional): Description

        Returns:
            TYPE: Description

        Raises:
            ValueError: Description
        """
        self.transform = transform
        self.text = self._humanize(obj, **kwargs) if humanize else obj
        self.theme = theme
        self.prefix = None
        self.text = "{}{}".format(
            self.text,
            " [{}]: ".format(default) if default else " "
        )
        self._print(linebreak=False)

        if self.format_only:
            return self.text
        else:
            answered = False
            ask_text = ": "
            while not answered:
                data = input(ask_text)
                if required and not data and not default:
                    text = self.text
                    self.error(_("Value required"))
                    self.text = text
                else:
                    if validator and data:
                        if not callable(validator):
                            raise ValueError(
                                "Validator must be a function")
                        text = self.text
                        answered = validator(data)
                        if not answered:
                            ask_text = "Please answer again: "
                        self.text = text
                    else:
                        answered = True
            return data if data else default

    def clear(self):
        """Clear terminal."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def select(self,
               obj,
               theme="choose",
               humanize=True,
               question=None,
               default=None,
               **kwargs):
        """Summary

        Args:
            obj (TYPE): Description
            theme (str, optional): Description
            humanize (bool, optional): Description
            question (None, optional): Description
            default (None, optional): Description

        Returns:
            TYPE: Description

        Raises:
            ValueError: Description
        """
        if not isinstance(obj, list):
            raise ValueError("select data must be a list")
        if default is not None:
            try:
                obj[default]
            except (ValueError, IndexError):
                raise ValueError("Select default not valid")
        self.transform = None
        options = [
            self._humanize(item, **kwargs) if humanize else item
            for item in obj
        ]
        phrases = []
        letters = []
        for opt in options:
            letter, phrase = self._get_letter(
                text=opt,
                optlist=letters
            )
            phrases.append(phrase)
            letters.append(letter)

        answered = False
        self.theme = theme
        self.prefix = False
        self.text = "{}: {}{}".format(
            question if question else _("Select"),
            ", ".join([text for text in phrases]),
            " [{}]".format(obj[default]) if default is not None else ""
        )
        self._print(linebreak=False)
        if self.format_only:
            return self.text
        while not answered:
            ret = input("? ")
            if not ret and default is not None:
                return default
            elif ret and ret.upper() in letters:
                answered = True
        return [
            index
            for index, data in enumerate(letters)
            if ret.upper() == data
        ][0]

    def _get_letter(self, text, index=0, optlist=[]):
        """Summary

        Args:
            text (TYPE): Description
            index (int, optional): Description
            optlist (list, optional): Description

        Returns:
            TYPE: Description

        Raises:
            ValueError: Description
        """
        try:
            test_letter = text[index].upper()
        except IndexError:
            raise ValueError("Can not found letter for {} option".format(text))
        if test_letter in optlist:
            index += 1
            test_letter, new_text = self._get_letter(text, index, optlist)
        else:
            new_text = "{}({}){}".format(
                text[:index] if index > 0 else "",
                test_letter,
                text[index + 1:]
            )
        return test_letter, new_text

    def run(
            self,
            task,
            title=None,
            get_stdout=False,
            run_stdout=False,
            verbose=False,
            silent=False,
            use_prefix=True,
            prefix="Cmd"):
        """Run command in subprocess.

        Args:
            task (string): command to run
            title (string, optional): title to be printed
            get_stdout (bool, optional): return stdout from command
            run_stdout (bool, optional): run stdout before command
            verbose (bool, optional): show command in terminal
            silent (bool, optional): occult stdout/stderr when running command

        Return
        ------
            Bool or String: Task success or Task stdout

        """
        if title:
            self.section(title)

        try:
            if run_stdout:
                if verbose:
                    self.info(task, use_prefix=use_prefix, prefix=prefix)
                command = subprocess.check_output(task, shell=True)

                if not command:
                    print('An error occur. Task aborted.')
                    return False

                if verbose:
                    self.info(command, use_prefix=use_prefix, prefix=prefix)
                ret = subprocess.call(command, shell=True)

            elif get_stdout is True:
                if verbose:
                    self.info(task, use_prefix=use_prefix, prefix=prefix)
                ret = subprocess.check_output(task, shell=True)
            else:
                if verbose:
                    self.info(task, use_prefix=use_prefix, prefix=prefix)
                ret = subprocess.call(
                    task if not silent else
                    "{} >/dev/null".format(task),
                    shell=True,
                    stderr=subprocess.STDOUT)

            if ret != 0 and not get_stdout:
                return False
        except BaseException:
            return False

        try:
            ret = ret.decode('utf-8')
        except AttributeError:
            pass

        return True if not get_stdout else ret
