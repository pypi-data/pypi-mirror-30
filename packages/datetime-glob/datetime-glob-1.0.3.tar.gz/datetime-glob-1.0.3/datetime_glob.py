#!/usr/bin/env python3
""" parses date/time from paths using glob wildcard pattern intertwined with a subset of strftime directives. """
import calendar
import collections
import copy
import datetime
import os
# yapf: disable
import pathlib
import re
from typing import Optional, List, Pattern, MutableMapping, Union  # pylint: disable=unused-import

import lexery

LEXER = lexery.Lexer(
    rules=[
        lexery.Rule(identifier='*', pattern=re.compile(r'\*')),
        lexery.Rule(identifier='?', pattern=re.compile(r'\?')),
        lexery.Rule(identifier='%d', pattern=re.compile(r'%d')),
        lexery.Rule(identifier='%-d', pattern=re.compile(r'%-d')),
        lexery.Rule(identifier='%m', pattern=re.compile(r'%m')),
        lexery.Rule(identifier='%-m', pattern=re.compile(r'%-m')),
        lexery.Rule(identifier='%y', pattern=re.compile(r'%y')),
        lexery.Rule(identifier='%Y', pattern=re.compile(r'%Y')),
        lexery.Rule(identifier='%H', pattern=re.compile(r'%H')),
        lexery.Rule(identifier='%-H', pattern=re.compile(r'%-H')),
        lexery.Rule(identifier='%M', pattern=re.compile(r'%M')),
        lexery.Rule(identifier='%-M', pattern=re.compile(r'%-M')),
        lexery.Rule(identifier='%S', pattern=re.compile(r'%S')),
        lexery.Rule(identifier='%-S', pattern=re.compile(r'%-S')),
        lexery.Rule(identifier='%f', pattern=re.compile(r'%f')),
        lexery.Rule(identifier='%%', pattern=re.compile(r'%%')),
        lexery.Rule(identifier='text', pattern=re.compile(r'[^%*?]'))
    ]
)


# yapf: enable


class PatternSegment:
    """ defines a regular expression for a given path segment. """

    def __init__(self) -> None:
        self.regex = None  # type: Optional[Pattern]

        # group index -> token class, sorted by group index
        self.group_map = collections.OrderedDict()  # type: MutableMapping[int, str]


def parse_pattern_segment(pattern_segment: str) -> PatternSegment:
    """
    Parses the given pattern segment to a regular expression.

    :param pattern_segment: pattern path segment
    :return: regular expression with a group map corresponding to the glob pattern segment.
    """
    # pylint: disable=too-many-branches
    # pylint: disable=too-many-statements
    token_lines = None  # type: Optional[List[List[lexery.Token]]]
    lexerr = None  # type: Optional[lexery.Error]
    try:
        token_lines = LEXER.lex(pattern_segment)
    except lexery.Error as err:
        lexerr = err

    if lexerr is not None:
        raise ValueError("Invalid pattern segment: {}".format(lexerr))

    tokens = []  # type: List[lexery.Token]
    for line in token_lines:
        tokens.extend(line)

    patseg = PatternSegment()
    group = 1  # group index in the regular expression, used to map groups to token classes

    parts = ['^']
    for token in tokens:
        if token.identifier == '*':
            parts.append('.*')
        elif token.identifier == '?':
            parts.append('.')
        elif token.identifier == '%d':
            parts.append('(0[1-9]|1[0-9]|2[0-9]|3[0-1])')
            patseg.group_map[group] = token.identifier
            group += 1
        elif token.identifier == '%-d':
            parts.append('(1[0-9]|2[0-9]|3[0-1]|[1-9])')
            patseg.group_map[group] = token.identifier
            group += 1
        elif token.identifier == '%m':
            parts.append('(0[1-9]|1[1-2])')
            patseg.group_map[group] = token.identifier
            group += 1
        elif token.identifier == '%-m':
            parts.append('(1[1-2]|[1-9])')
            patseg.group_map[group] = token.identifier
            group += 1
        elif token.identifier == '%y':
            parts.append('([0-9]{2})')
            patseg.group_map[group] = token.identifier
            group += 1
        elif token.identifier == '%Y':
            parts.append('([0-9]{4})')
            patseg.group_map[group] = token.identifier
            group += 1
        elif token.identifier == '%H':
            parts.append('(0[0-9]|1[0-9]|2[0-3])')
            patseg.group_map[group] = token.identifier
            group += 1
        elif token.identifier == '%-H':
            parts.append('(1[0-9]|2[0-3]|[0-9])')
            patseg.group_map[group] = token.identifier
            group += 1
        elif token.identifier == '%M':
            parts.append('([0-5][0-9])')
            patseg.group_map[group] = token.identifier
            group += 1
        elif token.identifier == '%-M':
            parts.append('([1-5][0-9]|[0-9])')
            patseg.group_map[group] = token.identifier
            group += 1
        elif token.identifier == '%S':
            parts.append('([0-5][0-9])')
            patseg.group_map[group] = token.identifier
            group += 1
        elif token.identifier == '%-S':
            parts.append('([1-5][0-9]|[0-9])')
            patseg.group_map[group] = token.identifier
            group += 1
        elif token.identifier == '%f':
            parts.append('([0-9]{6})')
            patseg.group_map[group] = token.identifier
            group += 1
        elif token.identifier == '%%':
            parts.append('%')
        elif token.identifier == 'text':
            parts.append(re.escape(token.content))
        else:
            raise NotImplementedError("Unhandled token: {}".format(token))

    parts.append('$')
    patseg.regex = re.compile(''.join(parts))
    return patseg


def parse_pattern(pattern: str) -> List[PatternSegment]:
    """
    Splits the given pattern into path segments and converts each path segment to a regular expression.

    :param pattern: glob pattern intertwined with strftime directives.
    :return: list of regular expressions where each expression corresponds to a pattern path segment .
    """
    if pattern == '/':
        raise ValueError("Can not match root: {}".format(pattern))

    if pattern == '':
        raise ValueError("Can not match empty pattern")

    if pattern.endswith('/'):
        raise ValueError("Unexpected trailing slash ('/'): {}".format(pattern))

    segments = pattern.split(os.sep)  # type: List[str]

    segments = [segment for segment in segments if segment != '' and segment != '.']

    for segment in segments:
        if segment == '..':
            raise ValueError("Parent directory ('..') not allowed in a pattern: {}".format(pattern))

    lexerr = None  # type: Optional[lexery.Error]
    try:
        patsegs = [parse_pattern_segment(pattern_segment=segment) for segment in segments]
        return patsegs
    except lexery.Error as err:
        lexerr = err

    assert lexerr is not None
    raise ValueError("Invalid pattern: {}".format(lexerr))


class Match:
    """ represents date/time matches in the path. """

    def __init__(self,
                 year: Optional[int] = None,
                 month: Optional[int] = None,
                 day: Optional[int] = None,
                 hour: Optional[int] = None,
                 minute: Optional[int] = None,
                 second: Optional[int] = None,
                 microsecond: Optional[int] = None) -> None:
        # pylint: disable=too-many-arguments
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.second = second
        self.microsecond = microsecond

    def as_datetime(self) -> datetime.datetime:
        """
        :return: match as a date/time
        :raises: ValueError if one of the expected fields is missing
        """
        if self.year is None:
            raise ValueError("year was not set, can not construct a datetime")

        if self.month is None:
            raise ValueError("month was not set, can not construct a datetime")

        if self.day is None:
            raise ValueError("day was not set, can not construct a datetime")

        return datetime.datetime(
            year=self.year,
            month=self.month,
            day=self.day,
            hour=0 if self.hour is None else self.hour,
            minute=0 if self.minute is None else self.minute,
            second=0 if self.second is None else self.second,
            microsecond=0 if self.microsecond is None else self.microsecond)

    def as_date(self) -> datetime.date:
        """
        :return: match as a date; time part is ignored
        :raises: ValueError if one of the expected fields is missing
        """
        if self.year is None:
            raise ValueError("year was not set, can not construct a date")

        if self.month is None:
            raise ValueError("month was not set, can not construct a date")

        if self.day is None:
            raise ValueError("day was not set, can not construct a date")

        return datetime.date(year=self.year, month=self.month, day=self.day)

    def as_time(self) -> datetime.time:
        """
        :return: match as a time; date part is ignored and missing fields are assumed to be 0.
        """
        return datetime.time(
            hour=0 if self.hour is None else self.hour,
            minute=0 if self.minute is None else self.minute,
            second=0 if self.second is None else self.second,
            microsecond=0 if self.microsecond is None else self.microsecond)

    def __repr__(self) -> str:
        return "datetime_glob.Match(year = {}, month = {}, day = {}, hour = {}, " \
               "minute = {}, second = {}, microsecond = {})".format(
            self.year, self.month, self.day, self.hour, self.minute, self.second, self.microsecond)


EMPTY_MATCH = Match()


def match_segment(segment: str, pattern_segment: PatternSegment, match: Match = EMPTY_MATCH) -> Optional[Match]:
    """
    Performs a step of incremental matching. If the `pattern_segment` matches the `segment`, parses the date/time
    information from the segment and returns the updated copy of the `match`.

    :param segment: to match
    :param pattern_segment: how to match
    :param match: what we matched so far
    :return: updated copy of the `match`, or None if segment could not be matched
    """
    # pylint: disable=too-many-locals
    # pylint: disable=too-many-return-statements
    # pylint: disable=too-many-branches
    # pylint: disable=too-many-statements
    if match is None:
        return None

    regex_mtch = pattern_segment.regex.match(segment)
    if regex_mtch is None:
        return None

    match1 = copy.copy(match)

    for group_i, directive in pattern_segment.group_map.items():
        if directive == '%d' or directive == '%-d':
            day = int(regex_mtch.group(group_i))

            if match1.day is not None:
                if day != match1.day:
                    return None

                # the same day already match1ed.
            else:
                match1.day = day

        elif directive == '%m' or directive == '%-m':
            month = int(regex_mtch.group(group_i))

            if match1.month is not None:
                if month != match1.month:
                    return None

                # the same month already match1ed.
            else:
                match1.month = month

        elif directive == '%y':
            year = 2000 + int(regex_mtch.group(group_i))

            if match1.year is not None:
                if year != match1.year:
                    return None

                # the same year already match1ed.
            else:
                match1.year = year

        elif directive == '%Y':
            year = int(regex_mtch.group(group_i))

            if match1.year is not None:
                if year != match1.year:
                    return None

                # the same year already match1ed.
            else:
                match1.year = year

        elif directive == '%H' or directive == '%-H':
            hour = int(regex_mtch.group(group_i))

            if match1.hour is not None:
                if hour != match1.hour:
                    return None

                # the same hour already match1ed.
            else:
                match1.hour = hour

        elif directive == '%M' or directive == '%-M':
            minute = int(regex_mtch.group(group_i))

            if match1.minute is not None:
                if minute != match1.minute:
                    return None

                # the same minute already match1ed.
            else:
                match1.minute = minute

        elif directive == '%S' or directive == '%-S':
            second = int(regex_mtch.group(group_i))

            if match1.second is not None:
                if second != match1.second:
                    return None

                # the same second already match1ed.
            else:
                match1.second = second

        elif directive == '%f':
            microsecond = int(regex_mtch.group(group_i))

            if match1.microsecond is not None:
                if microsecond != match1.microsecond:
                    return None

                # the same microsecond already match1ed.
            else:
                match1.microsecond = microsecond

        else:
            raise NotImplementedError("Unhandled directive {!r} in pattern: {}".format(
                directive, pattern_segment.regex.pattern))

    if match1.year is not None and match1.month is not None and \
            match1.year != match.year and match1.month != match.month:
        _, days_in_month = calendar.monthrange(match1.year, match1.month)
        if match1.day > days_in_month:
            return None

    return match1


class Matcher:
    """ matches the given path against a compiled pattern. """

    def __init__(self, pattern: str) -> None:
        self.pattern = pattern
        self.pattern_segments = parse_pattern(pattern)

    def match(self, path: Union[str, pathlib.Path]) -> Optional[Match]:
        """
        :return: the match if `path` could be matched, None otherwise
        """
        # pylint: disable=too-many-branches

        if isinstance(path, str):
            pth = path
        elif isinstance(path, pathlib.Path):
            pth = path.as_posix()
        else:
            raise ValueError("Unexpected path type: {}".format(type(path)))

        if pth == '':
            raise ValueError("Can not match empty path: {}".format(path))

        if pth == '/':
            raise ValueError("Can not match root: {}".format(path))

        if pth.endswith('/'):
            raise ValueError("Unexpected trailing slash ('/'): {}".format(path))

        if (pth.startswith('/') and not self.pattern.startswith('/')):
            raise ValueError("Can not match absolute path against relative path pattern {}: {}".format(
                self.pattern, path))

        if (not pth.startswith('/') and self.pattern.startswith('/')):
            raise ValueError("Can not match relative path against absolute path pattern {}: {}".format(
                self.pattern, path))

        segments = pth.split(os.sep)  # type: List[str]
        segments = [segment for segment in segments if segment != '' and segment != '.']

        for segment in segments:
            if segment == '..':
                raise ValueError("Parent directory ('..') not allowed in a path: {}".format(path))

        if len(segments) != len(self.pattern_segments):
            return None

        mtch = Match()
        for segment, patseg in zip(segments, self.pattern_segments):
            mtch = match_segment(segment=segment, pattern_segment=patseg, match=mtch)
            if mtch is None:
                return None

        return mtch
