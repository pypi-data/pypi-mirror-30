#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Command line utility to parse/report on apache log files.
See: https://github.com/bedge/sqalp/blob/master/README.rst
"""
from __future__ import division, print_function, absolute_import

import argparse
import logging
import re
import sys
from collections import OrderedDict
import json
from typing import Dict

from user_agents import parse
import apache_log_parser
import sqlalchemy
from sqlalchemy import create_engine, Column, String, Integer, DateTime, func
from sqlalchemy.orm import sessionmaker
from tabulate import tabulate, tabulate_formats

__version__ = 'unknown'
from sqalp import __version__

__author__ = "Bruce Edge"
__copyright__ = "Bruce Edge"
__license__ = "mit"

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
_logger = logging.getLogger('sqalp')

# https://regex101.com/r/7xVnXr/11
# Custom regex in case we can't use apache_log_parser
# Not Used - for reference only
custom_format = re.compile(
    r'(?P<ip>\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\b\s*'
    r'(?P<logname>\S+)\s*'
    r'(?P<user>\S+)\s*'
    r'\[(?P<date>\d{2}/\w{3}/\d{4}):(?P<time>\d{2}:\d{2}:\d{2})\s'
    r'(?P<tz>-\d{4})\]\s\"'
    r'(?P<verb>(\w+))\s'
    r'(?P<request>\S*)\s'
    r'(?P<proto>HTTP/1.0)\"\s'
    r'(?P<status>\d+)\b\s*'
    r'(?P<size>\d+)\b\s'
    r'\"(?P<referer>[^\"]+)\"\s'
    r'\"(?P<agent>[^\"]+)\"',
    re.I | re.X)


class LogMsg(Base):
    """
    SqlAlchemy object based on response dict from apache_log_parser.
    Ignored elements are commented below, but left for reference.
    They can be added by uncommenting and providing a data type.
    """
    __tablename__ = 'logs'
    id: int = Column(Integer, primary_key=True)

    # Elements mapped directly from apache_log_parser output
    remote_host: str = Column(String())
    remote_logname: str = Column(String())
    remote_user: str = Column(String())
    # request_first_line
    request_header_referer: str = Column(String())
    request_header_user_agent: str = Column(String())
    request_http_ver: str = Column(String())
    request_method: str = Column(String())
    request_url: str = Column(String())
    # request_url_fragment
    request_url_hostname: str = Column(String(), nullable=True)
    request_url_netloc: str = Column(String(), nullable=True)
    request_url_password: str = Column(String(), nullable=True)
    request_url_path: str = Column(String())
    request_url_port: str = Column(String(), nullable=True)
    request_url_query: str = Column(String(), nullable=True)
    # request_url_query_dict
    # request_url_query_list
    # request_url_query_simple_dict
    # request_url_scheme
    request_url_username: str = Column(String(), nullable=True)
    response_bytes_clf: int = Column(Integer)
    status: int = Column(Integer)
    # time_received
    time_received_datetimeobj: DateTime = Column(DateTime)
    # time_received_isoformat
    # time_received_tz_datetimeobj
    # time_received_tz_isoformat
    # time_received_utc_datetimeobj
    # time_received_utc_isoformat

    # Additional elements added for convenience.
    # Use string here to avoid SQL 'must use datetime' restrictions
    time_received_date: str = Column(String)
    # These are parsed out separately to take advantage of UA package
    user_agent: str = Column(String)
    operating_system: str = Column(String)

    def __init__(self, os_approx, **kwargs):
        keep_kwargs = {k: v for k, v in kwargs.items() if k in logmsg_columns}
        date_str = kwargs['time_received_datetimeobj'].strftime('%Y-%m-%d')
        ua = parse(kwargs['request_header_user_agent'])
        user_agent = ua.browser.family
        operating_system = ua.os.family
        if os_approx:
            operating_system = operating_system.split()[0]
        super(LogMsg, self).__init__(
            **keep_kwargs, **{'time_received_date': date_str,
                              'user_agent': user_agent,
                              'operating_system': operating_system})

    def __repr__(self):
        return f'<LogMsg(remote_host={self.remote_host}, ' \
               f'ua={self.request_header_user_agent}, ' \
               f'status={self.status}, ' \
               f'len={self.response_bytes_clf}>'


# Use this to filter out unwanted dict elements
logmsg_columns = [_ for _ in LogMsg.__dict__.keys() if not _.startswith('_')]

# Well known log formats for apache logs
known_formats = {
    "common": "%h %l %u %t \"%r\" %>s %b",
    "combined": "%h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-agent}i\""
}


def file_import(session, input, parser, os_approx):
    # type: (Session, TextIO, Callable, bool) -> Tuple[int, int]
    """
    Read in log data
    """
    bad_msg_count = 0
    msg_count = 0
    for log_msg in input.readlines():
        try:
            msg_dict: Dict = parser(log_msg)
            lm: LogMsg = LogMsg(os_approx, **msg_dict)
            session.add(lm)
            msg_count += 1
        except (KeyError, ValueError) as ex:
            bad_msg_count += 1
            _logger.info(f'Parse failed: {ex} for log message: {log_msg}.')
    try:
        session.commit()
    except sqlalchemy.exc.OperationalError as ex:
        _logger.error(f'Commit failed: {ex} for {msg_count} messages.')

    _logger.info(f'Unparseable message count: {bad_msg_count}.')
    _logger.debug(f'Messages read: {msg_count}.')
    return msg_count, bad_msg_count


def get_session(loglevel):
    # type: (int) -> Session
    try:
        echo = loglevel >= logging.WARNING
    except TypeError:
        echo = False
    engine = create_engine('sqlite:///:memory:', echo=echo)
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    return session_factory()


def output(data, output_format):
    # type: (OrderedDict, str) -> None
    if output_format == 'json':
        print(json.dumps(data))
    else:
        print(tabulate(data, headers="keys", tablefmt=output_format))


def get_by_date(session):
    # type: (Session) -> OrderedDict
    results = OrderedDict()
    for day in session.query(func.distinct(LogMsg.time_received_date)).all():
        day = day[0]
        day_count = session.query(func.count()).filter(
            LogMsg.time_received_date == day).one()[0]
        results[day] = [day_count]

    _logger.debug(f'results: {results}')
    return results


def get_by_date_by_ua(session):
    # type: (Session) -> OrderedDict
    results = OrderedDict()
    for day in session.query(func.distinct(LogMsg.time_received_date)).all():
        day = day[0]
        results[day] = OrderedDict()
        for ua in session.query(func.distinct(LogMsg.user_agent)).filter(
                LogMsg.time_received_date == day).all():
            ua = ua[0]
            ua_count = session.query(func.count()).filter(
                LogMsg.time_received_date == day).filter(
                LogMsg.user_agent == ua).one()[0]
            results[day][ua] = ua_count
        results[day] = [[_[0], _[1]] for _ in
                        sorted(results[day].items(), key=lambda t: t[1],
                               reverse=True)][:3]
    _logger.debug(f'results: {results}')
    return results


def get_by_date_verb_ratio(session):
    # type: (Session) -> OrderedDict
    results = OrderedDict()
    for day in session.query(func.distinct(LogMsg.time_received_date)).all():
        day: str = day[0]
        day_counter = OrderedDict()
        for method, os, count in session.query(
                LogMsg.request_method, LogMsg.operating_system,
                func.count('*')) \
                .filter(LogMsg.time_received_date == day) \
                .group_by(LogMsg.operating_system,
                          LogMsg.request_method).all():
            try:
                day_counter[os][method]: int = count
            except Exception as ex:
                day_counter[os] = OrderedDict()
                day_counter[os][method] = count

        results[day] = []
        for os in day_counter:
            # results[day][os] = OrderedDict()
            if 'GET' not in day_counter[os].keys():
                os_ratio = 0
            elif 'POST' not in day_counter[os].keys():
                os_ratio = 'NAN'
            else:
                ratio = float(day_counter[os]["GET"]) / day_counter[os]["POST"]
                os_ratio = '{:.4}'.format(ratio)

            results[day].append([os, os_ratio])
    _logger.debug(f'results: {results}')
    return results


def get_parser(parser_string):
    # type: (str) -> Callable
    return apache_log_parser.make_parser(parser_string)


def parse_args(args: argparse.ArgumentParser) -> argparse.Namespace:
    """Parse command line parameters

    Args:
      args ([str]): command line parameters as list of strings

    Returns:

      :obj:`argparse.Namespace`: command line parameters namespace
    """
    parser = argparse.ArgumentParser(
        description='Log file parser')
    parser.add_argument(
        '--version',
        action='version',
        version='sqalp {ver}'.format(ver=__version__))
    parser.add_argument(
        '-i',
        '--input',
        nargs='?',
        help='Files to input, default to stdin',
        type=argparse.FileType('r', encoding='UTF-8'),
        default=sys.stdin)

    input_formats = [_ for _ in known_formats.keys()]
    parser.add_argument(
        '-f',
        '--format',
        help=f'Input format'
             f'see: https://httpd.apache.org/docs/1.3/logs.html#accesslog',
        type=str,
        choices=input_formats,
        required=True)

    parser.add_argument(
        '-c',
        '--count',
        help='Requests per day',
        default=False,
        action='store_true')
    parser.add_argument(
        '-u',
        '--ua_frequency',
        help='User-agent stats by day',
        default=False,
        action='store_true')
    parser.add_argument(
        '-r',
        '--ratio',
        help='Ratio of GET to POST by day by OS',
        default=False,
        action='store_true')

    parser.add_argument(
        '-O',
        '--os_approximate',
        help="Approximate OS to family grouping (Win XP == Win, etc)",
        default=False,
        action='store_true')

    output_formats = tabulate_formats
    output_formats.append("json")
    parser.add_argument(
        '-o',
        '--output_format',
        help=f'table/output formats, one of {output_formats}',
        default='grid',
        choices=output_formats,
        action='store',
        metavar='OUTPUT_FORMAT')

    parser.add_argument(
        '-v',
        '--verbose',
        dest='loglevel',
        help='set loglevel to INFO',
        action='store_const',
        const=logging.INFO)
    parser.add_argument(
        '-vv',
        '--very-verbose',
        dest='loglevel',
        help='set loglevel to DEBUG',
        action='store_const',
        const=logging.DEBUG)
    return parser.parse_args(args)


def setup_logging(loglevel: int) -> None:
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(level=loglevel, stream=sys.stderr,
                        format=logformat, datefmt="%Y-%m-%d %H:%M:%S")


def main(args):
    """Main entry point allowing external calls

    Args:
      args ([str]): command line parameter list
    """
    args = parse_args(args)
    setup_logging(args.loglevel)
    _logger.debug("apl start")
    # Decide on back-end, default to RAM for now...
    session = get_session(args.loglevel)
    parser = get_parser(known_formats[args.format])
    file_import(session, args.input, parser, args.os_approximate)

    if args.count:
        data = get_by_date(session)
    if args.ua_frequency:
        data = get_by_date_by_ua(session)
    if args.ratio:
        data = get_by_date_verb_ratio(session)

    output(data, args.output_format)
    _logger.debug("apl stop")


def run():
    """Entry point for console_scripts
    """
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
