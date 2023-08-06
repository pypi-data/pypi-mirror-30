# -*- coding: utf-8 -*-

import re


class Decoder(object):
    regex_text = None

    def __init__(self, raw_data):
        self.raw_data = raw_data
        self.data = None

    def decode(self):
        raise NotImplementedError()


class IntegerDecoder(Decoder):

    regex_text = r'i([-]?[\d]+)e'

    def decode(self):
        value = re.match(self.regex_text, self.raw_data).group(1)
        self.raw_data = self.raw_data[1:]
        self.raw_data = self.raw_data.lstrip(value)
        self.raw_data = self.raw_data[1:]
        self.data = int(value)
        return self.raw_data, self.data


class StringDecoder(Decoder):

    regex_text = r'([\d]+):([\S]+)'

    def decode(self):
        length = re.match(self.regex_text, self.raw_data).group(1)
        self.raw_data = self.raw_data.lstrip(length)
        self.raw_data = self.raw_data.lstrip(':')
        self.data = self.raw_data[:int(length)]
        self.raw_data = self.raw_data[int(length):]
        return self.raw_data, self.data


class ListDecoder(Decoder):

    regex_text = r'l([\S]+)e'

    def __init__(self, raw_data):
        super(ListDecoder, self).__init__(raw_data)
        self.data = []

    def decode_item(self, raw_data):
        raw_data, value = decode(raw_data)
        self.data.append(value)
        return raw_data

    def decode(self):
        self.raw_data = self.raw_data[1:]
        while not self.raw_data.startswith('e'):
            self.raw_data = self.decode_item(self.raw_data)
        self.raw_data = self.raw_data[1:]
        return self.raw_data, self.data


class DictDecoder(Decoder):

    regex_text = r'd([\S]+)e'

    def __init__(self, raw_data):
        super(DictDecoder, self).__init__(raw_data)
        self.data = {}

    def decode_item(self, raw_data):
        raw_data, key = StringDecoder(raw_data).decode()
        raw_data, value = decode(raw_data)
        self.data[key] = value
        return raw_data

    def decode(self):
        self.raw_data = self.raw_data[1:]
        while not self.raw_data.startswith('e'):
            self.raw_data = self.decode_item(self.raw_data)
        self.raw_data = self.raw_data[1:]
        return self.raw_data, self.data


def decode(raw_data):
    """
    decode string(raw_data) to tuple(raw_data_left, data_decoded)
    :param raw_data:
    :return:
    """
    if raw_data.startswith('d'):
        raw_data, data = DictDecoder(raw_data).decode()
    elif raw_data.startswith('l'):
        raw_data, data = ListDecoder(raw_data).decode()
    elif raw_data.startswith('i'):
        raw_data, data = IntegerDecoder(raw_data).decode()
    else:
        raw_data, data = StringDecoder(raw_data).decode()
    return raw_data, data


if __name__ == '__main__':
    print(decode('de'))
    print(decode('i42e'))
    print(decode('i42ee'))
    print(decode('4:spam'))
    print(decode('li42e4:spame'))
    print(decode('d3:bar4:spam3:fooi42ee'))
    print(decode('d8:intervali900e5:peersld2:ip14:10.173.197.1844:porti51387eed2:ip12:10.170.28.604:porti6881eed2:ip13:10.170.47.2134:porti17155eed2:ip13:10.170.17.2424:porti64510eed2:ip12:10.170.1.2474:porti27299eed2:ip13:10.170.72.2354:porti51413eed2:ip11:10.170.67.34:porti38106eeee'))  # noqa
    print(decode('d8:announcel16:http://baidu.com13:http://ele.mee8:encoding5:utf-84:infod6:lengthi123e4:name11:secret star6:piecesl3:abc3:defeee'))  # noqa
