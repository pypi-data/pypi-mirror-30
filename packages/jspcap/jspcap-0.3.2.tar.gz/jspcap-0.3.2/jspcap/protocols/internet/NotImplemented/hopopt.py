# -*- coding: utf-8 -*-
"""IPv6 Hop-by-Hop Options

``jspcap.protocols.internet.hopopt`` contains ``HOPOPT``
only, which implements extractor for IPv6 Hop-by-Hop
Options header (HOPOPT), whose structure is described
as below.

+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|  Next Header  |  Hdr Ext Len  |                               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+                               +
|                                                               |
.                                                               .
.                            Options                            .
.                                                               .
|                                                               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

"""
# IPv6 Hop-by-Hop Option
# Analyser for HOPOPT header


from jspcap.utilities import Info
from jspcap.protocols.protocol import Protocol


__all__ = ['HOPOPT']


class HOPOPT(Protocol):
    """This class implements IPv6 Hop-by-Hop Options.

    Properties:
        * name -- str, name of corresponding procotol
        * info -- Info, info dict of current instance
        * alias -- str, acronym of corresponding procotol
        * layer -- str, `Internet`
        * length -- int, header length of corresponding protocol
        * protocol -- str, name of next layer protocol
        * protochain -- ProtoChain, protocol chain of current instance

    Methods:
        * read_hopopt -- read IPv6 Hop-by-Hop Options (HOPOPT)

    Attributes:
        * _file -- BytesIO, bytes to be extracted
        * _info -- Info, info dict of current instance
        * _protos -- ProtoChain, protocol chain of current instance

    Utilities:
        * _read_protos -- read next layer protocol type
        * _read_fileng -- read file buffer
        * _read_unpack -- read bytes and unpack to integers
        * _read_binary -- read bytes and convert into binaries
        * _decode_next_layer -- decode next layer protocol type
        * _import_next_layer -- import next layer protocol extractor

    """
