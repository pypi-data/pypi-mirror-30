# -*- coding: utf-8 -*-
"""analyser for application layer

``jspcap.analyser`` works as a header quater to analyse and
match application layer protocol. Then, call corresponding
modules and functions to extract the attributes.

"""
import textwrap


# Analyser for Application Layer
# Match Protocols and Extract Attributes


from jspcap.exceptions import ProtocolError
from jspcap.utilities import ProtoChain


class Analysis:
    """Analyse report."""
    @property
    def info(self):
        return self._info

    @property
    def name(self):
        if self._ptch is None:
            return 'Unknown'
        else:
            return self._ptch.tuple[0]

    @property
    def protochain(self):
        return self._ptch

    def __init__(info, ptch):
        self._info = info
        self._ptch = ptch

    def __str__(self):
        if self._ptch is None:
            return self._info
        else:
            return f'Analysis({self._ptch.tuple[0]}, info={self._info})'

    def __repr__(self):
        if self._ptch is None:
            return 'Analysis()'
        else:
            return f'Analysis({self._ptch.tuple[0]})'


def analyse(file, length):
    """Analyse application layer packets."""
    flag, http = _analyse_http(file, length)
    if flag:
        return Analysis(http.info, http.protochain)

    data = file.read(*[length]) or None
    return Analysis(data, None)


def _analyse_http(file, length):
    try:
        from jspcap.protocols.application.http import HTTP
        http = HTTP(file, length)
    except ProtocolError:
        return False, None
    return True, http
