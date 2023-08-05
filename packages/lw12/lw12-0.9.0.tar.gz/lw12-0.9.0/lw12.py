#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8:ts=8:et:sw=4:sts=4
#
# Copyright © 2018 Julian Knauer <jpk+lw12dev@goatpr0n.de>
#
# Distributed under terms of the MIT license.

"""

"""

from struct import (pack, unpack, calcsize)
from enum import Enum
import socket
from collections import namedtuple


_LW12_PKT_LEN = 9
_LW12_PKT_FMT = 'c6scc'
_LW12_PKT_PAYLOAD_FMT = 'cccccc'
_LW12_PKT_HEAD = b'\x7e'
_LW12_PKT_TAIL = b'\xef'


class LW12_MODE(Enum):
    LIGHT       = b'\x04'
    EFFECT      = b'\x05'
    COLOR       = b'\x07'
    IGNORE      = b'\xff'


class LW12_CONTROL(Enum):
    RGB         = b'\x05'
    SCAN_CTRL   = b'\x09'
    IGNORE      = b'\xff'


class LW12_LIGHT(Enum):
    BRIGHTNESS  = b'\x01'
    FLASH       = b'\x02'
    SET         = b'\x03'
    POWER       = b'\x04'
    DIM         = b'\x05'   # Unused: To be used with LW12_MODE.EFFECT
    IGNORE      = b'\xff'


class LW12_POWER(Enum):
    ON          = b'\x01'
    OFF         = b'\x00'
    IGNORE      = b'\xff'


class LW12_EFFECT_STATIC(Enum):
    RED         = b'\x80'
    BLUE        = b'\x81'
    GREEN       = b'\x82'
    CYAN        = b'\x83'
    YELLOW      = b'\x84'
    PURPLE      = b'\x85'
    WHITE       = b'\x86'


class LW12_EFFECT_JUMP(Enum):
    TRICOLOR    = b'\x87'
    SEVENCOLOR  = b'\x88'


class LW12_EFFECT_GRADIENT(Enum):
    TRICOLOR    = b'\x89'
    SEVENCOLOR  = b'\x8a'
    RED         = b'\x8b'
    GREEN       = b'\x8c'
    BLUE        = b'\x8d'
    YELLOW      = b'\x8e'
    CYAN        = b'\x8f'
    PURPLE      = b'\x90'
    WHITE       = b'\x91'
    RED_GREEN   = b'\x92'
    RED_BLUE    = b'\x93'
    GREEN_BLUE  = b'\x94'


class LW12_EFFECT_FLASH(Enum):
    SEVENCOLOR  = b'\x95'
    RED         = b'\x96'
    GREEN       = b'\x97'
    BLUE        = b'\x98'
    YELLOW      = b'\x99'
    CYAN        = b'\x9a'
    PURPLE      = b'\x9b'
    WHITE       = b'\x9c'


class Color(object):

    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        return bytes([self._value])

    def __repr__(self):
        return '<lw12.Color: {}>'.format(self.value)


LW12_Packet = namedtuple('Packet', 'head data pad tail')
LW12_Payload = namedtuple('Payload', 'mode option value r g b')

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


class LW12Controller(object):

    def __init__(self, host, port, detect=False):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.host = host
        self.port = port
        self._detect_controllers = detect
        if detect:
            self.socket_receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket_receiver.bind(('', 6000))

    def get_remote_socket(self):
        return (self.host, self.port)

    def send(self, payload, sock=None):
        data = self._compile_packet(payload)
        if payload.option == LW12_CONTROL.SCAN_CTRL:
            pad = b'\xff'
        else:
            pad = b'\x00'
        packet = pack(_LW12_PKT_FMT, _LW12_PKT_HEAD, data, pad, _LW12_PKT_TAIL)
        if len(packet) != 9:
            raise Exception('Invalid data length. Packet malformed')
        try:
            return self.socket.sendto(packet, sock or self.get_remote_socket())
        except OSError as oserr:
            if oserr.errno == 101:
                print('Network is unreachable')

    def read(self):
        if not self._detect_controllers:
            return None
        buffer_, sender = self.socket_receiver.recvfrom(_LW12_PKT_LEN)
        print(buffer_)
        print(sender)


    def _compile_packet(self, payload):
        if len(payload) != 6:
            raise Exception('Invalid payload length. Packet malformed')
        try:
            raw_value = payload.value.value
        except AttributeError:
            raw_value = payload.value
        return pack(_LW12_PKT_PAYLOAD_FMT,
                    payload.mode.value, payload.option.value, raw_value,
                    payload.r.value, payload.g.value, payload.b.value)

    def light_off(self):
        payload = LW12_Payload(r=LW12_LIGHT.IGNORE, g=LW12_LIGHT.IGNORE, b=LW12_LIGHT.IGNORE,
                               mode=LW12_MODE.LIGHT,
                               option=LW12_LIGHT.POWER,
                               value=LW12_POWER.OFF)
        self.send(payload)

    def light_on(self):
        payload = LW12_Payload(r=LW12_LIGHT.IGNORE, g=LW12_LIGHT.IGNORE, b=LW12_LIGHT.IGNORE,
                               mode=LW12_MODE.LIGHT,
                               option=LW12_LIGHT.POWER,
                               value=LW12_POWER.ON)
        self.send(payload)

    def set_effect(self, effect):
        payload = LW12_Payload(r=LW12_LIGHT.SET, g=LW12_LIGHT.IGNORE, b=LW12_LIGHT.IGNORE,
                               mode=LW12_MODE.LIGHT,
                               option=LW12_LIGHT.SET,
                               value=effect)
        self.send(payload)

    def set_light_option(self, option, value):
        # Fail safe handling for integers > 100
        if  0 < value > 100:
            value = int(value / 255 * 100)
        payload = LW12_Payload(r=LW12_LIGHT.IGNORE, g=LW12_LIGHT.IGNORE, b=LW12_LIGHT.IGNORE,
                               mode=LW12_MODE.LIGHT,
                               option=option,
                               value=bytes([value]))
        self.send(payload)

    def set_color(self, red, green, blue):
        payload = LW12_Payload(r=Color(red), g=Color(green), b=Color(blue),
                               mode=LW12_MODE.COLOR,
                               option=LW12_CONTROL.RGB,
                               value=LW12_LIGHT.SET)
        self.send(payload)

    def scan(self, broadcast_addr='255.255.255.255', broadcast_port=5000):
        if not self._detect_controllers:
            return None
        # Fail safe handling for integers > 100
        payload = LW12_Payload(r=LW12_DETECT.IGNORE, g=LW12_DETECT.IGNORE, b=LW12_DETECT.IGNORE,
                               mode=LW12_MODE.DETECT,
                               option=LW12_DETECT.SCAN_CTRL,
                               value=LW12_DETECT.IGNORE)
        self.send(payload, (broadcast_addr, broadcast_port))
        self.read()
