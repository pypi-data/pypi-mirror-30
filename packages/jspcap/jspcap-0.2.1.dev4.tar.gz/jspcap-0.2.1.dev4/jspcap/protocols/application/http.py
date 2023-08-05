# -*- coding: utf-8 -*-
"""hypertext transfer protocol

``jspcap.protocols.application.http`` contains ``HTTP``
only, which implements extractor for Hypertext Transfer
Protocol (HTTP), whose structure is described as below.

METHOD URL HTTP/VERSION\r\n :==: REQUEST LINE
<key> : <value>\r\n         :==: REQUEST HEADER
............  (Elipsis)     :==: REQUEST HEADER
\r\n                        :==: REQUEST SEPERATOR
<body>                      :==: REQUEST BODY (optional)

HTTP/VERSION CODE DESP \r\n :==: RESPONSE LINE
<key> : <value>\r\n         :==: RESPONSE HEADER
............  (Elipsis)     :==: RESPONSE HEADER
\r\n                        :==: RESPONSE SEPERATOR
<body>                      :==: RESPONSE BODY (optional)

"""
import re


# Hypertext Transfer Protocol
# Analyser for HTTP request & response


from jspcap.exceptions import UnsupportedCall, ProtocolError
from jspcap.utilities import Info
from jspcap.protocols.application.application import Application


__all__ = ['HTTP']


# utility regular expressions
_RE_METHOD = re.compile(r'GET|HEAD|POST|PUT|DELETE|CONNECT|OPTIONS|TRACE')
_RE_VERSION = re.compile(r'HTTP/(?P<version>\d\.\d)')
_RE_STATUS = re.compile(r'\d{3}')


class HTPP(Application):
    """This class implements Hypertext Transfer Protocol.

    Properties:
        * name -- str, name of corresponding procotol
        * info -- Info, info dict of current instance
        * layer -- str, `Application`
        * protocol -- str, name of next layer protocol
        * protochain -- ProtoChain, protocol chain of current instance
        * uri -- str, Referer request-header field
        * host -- str, Host request-header field
        * type -- str, Content-Type entity-header field
        * body -- bytes, request/response body

    Methods:
        * read_http -- read Hypertext Transfer Protocol (HTTP)

    Attributes:
        * _file -- BytesIO, bytes to be extracted
        * _info -- Info, info dict of current instance
        * _protos -- ProtoChain, protocol chain of current instance

    Utilities:
        * _read_protos -- read next layer protocol type
        * _read_fileng -- read file buffer
        * _read_unpack -- read bytes and unpack to integers
        * _read_binary -- read bytes and convert into binaries

    """
    ##########################################################################
    # Properties.
    ##########################################################################

    @property
    def name(self):
        """Name of current protocol."""
        return 'Hypertext Transfer Protocol'

    @property
    def length(self):
        """Deprecated."""
        raise UnsupportedCall(f"'{self.__class__.__name__}' object has no attribute 'length'")

    ##########################################################################
    # Methods.
    ##########################################################################

    def read_http(self, length):
        """Read Hypertext Transfer Protocol (HTTP).

        Structure of HTTP packet [RFC 7230]:
            HTTP-message    :==:    start-line
                                    *( header-field CRLF )
                                    CRLF
                                    [ message-body ]

        """
        packet = self._file.read(length)
        try:
            header, body = packet.split(b'\r\n\r\n', 1)
        except ValueError:
            raise ProtocolError(f'{self.__class__.__name__}: invalid format')

        header_unpacked, http_receipt = self._read_http_header(header)
        body_unpacked = self._read_http_body(body)

        http = dict(
            receipt = http_receipt,
            header = header_unpacked,
            body = body_unpacked,
        )

        return http

    ##########################################################################
    # Data models.
    ##########################################################################

    def __init__(self, _file, length=None):
        self._file = _file
        self._info = Info(self.read_http(length))

    def __len__(self):
        raise UnsupportedCall(f"object of type '{self.__class__.__name__}' has no len()")

    def __length_hint__(self):
        pass

    ##########################################################################
    # Utilities.
    ##########################################################################

    def _read_http_header(self, header):
        """Read HTTP header.

        Structure of HTTP header [RFC 7230]:
            start-line      :==:    request-line / status-line
            request-line    :==:    method SP request-target SP HTTP-version CRLF
            status-line     :==:    HTTP-version SP status-code SP reason-phrase CRLF
            header-field    :==:    field-name ":" OWS field-value OWS

        """
        try:
            startline, headerfield = header.split(b'\r\n', 1)
            para1, para2, para3 = startline.split(b' ')
            fields = headerfield.split(b'\r\n')
            list_ = [ field.split(b':') for field in fields ]
        except ValueError:
            raise ProtocolError(f'{self.__class__.__name__}: invalid format')

        match1 = re.match(_RE_METHOD, para1)
        match2 = re.match(_RE_VERSION, para3)
        match3 = re.match(_RE_VERSION, para1)
        match4 = re.match(_RE_STATUS, para2)
        if match1 and match2:
            receipt = 'request'
            header = dict(
                request = dict(
                    method = para1,
                    target = para2,
                    version = match2.group('version'),
                ),
            )
        elif match3 and match4:
            receipt = 'response'
            header = dict(
                response = dict(
                    version = match3.group('version'),
                    status = para2,
                    phrase = para3,
                ),
            )
        else:
            raise ProtocolError(f'{self.__class__.__name__}: invalid format')

        try:
            for (key, value) in list_:
                if key in ('request', 'response'):
                    key = f'{key}_field'
                header[key] = value
        except ValueError:
            raise ProtocolError(f'{self.__class__.__name__}: invalid format')

        return header, receipt

    def _read_http_body(self, body):
        """Read HTTP body."""
        return body
