# -*- coding: utf-8 -*-

import sys


if sys.version_info.major == 2:
    int_types = (int, long)
    string_types = (str, unicode, bytes)
else:
    int_types = (int, )
    string_types = (str, bytes)


class Encoder(object):
    code_method = None

    def __init__(self, raw_data, encoding='utf-8'):
        self.method = type(raw_data)
        self.raw_data = raw_data
        self.encoding = encoding

    def encode(self):
        raise NotImplementedError()


class IntegerEncoder(Encoder):
    code_method = int_types

    def encode(self):
        return 'i{}e'.format(self.raw_data)


class StringEncoder(Encoder):
    code_method = string_types

    def encode(self):
        if self.method == unicode:
            self.raw_data.encode(self.encoding)
        return '{}:{}'.format(len(self.raw_data), self.raw_data)


class ListEncoder(Encoder):
    code_method = (list, tuple, set)

    def encode(self):
        return 'l{}e'.format(''.join([encode(data) for data in self.raw_data]))


class DictEncoder(Encoder):
    code_method = (dict, )

    def encode(self):
        self.raw_data = sorted(self.raw_data.items(), key=lambda a: a[0])
        return 'd{}e'.format(''.join([''.join(encode(item) for item in data)
                                      for data in self.raw_data]))


def encode(raw_data, encoding='utf-8'):
    """
    encode data to bencoded data
    :param raw_data:
    :param encoding: utf-8
    :return:
    """
    method = type(raw_data)
    if method in IntegerEncoder.code_method:
        return IntegerEncoder(raw_data, encoding).encode()
    elif method in StringEncoder.code_method:
        return StringEncoder(raw_data, encoding).encode()
    elif method in ListEncoder.code_method:
        return ListEncoder(raw_data, encoding).encode()
    else:
        return DictEncoder(raw_data, encoding).encode()


if __name__ == '__main__':
    print(encode(42), type(encode(42)))
    print(encode('spam'))
    print(encode([42, 'spam']))
    print(encode({'bar': 'spam', 'foo': 42}))
    print(encode({
        'encoding': 'utf-8',
        'announce': ['http://baidu.com', 'http://ele.me'],
        'info': {
            'length': 123,
            'pieces': ['abc', 'def'],
            'name': 'secret star'
        }
    }))
