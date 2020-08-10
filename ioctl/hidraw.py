# SPDX-License-Identifier: MIT

import array
import ctypes
import fcntl
import os

from typing import BinaryIO, List, Tuple

import ioctl


class HidrawReportDescriptor(ctypes.Structure):
    HID_MAX_DESCRIPTOR_SIZE = 4096
    _fields_ = [
        ('size', ctypes.c_uint),
        ('value', ctypes.c_ubyte * HID_MAX_DESCRIPTOR_SIZE),
    ]


class HidrawDevinfo(ctypes.Structure):
    _fields_ = [
        ('bustype', ctypes.c_uint),
        ('vendor', ctypes.c_ushort),
        ('product', ctypes.c_ushort),
    ]


class Hidraw(object):
    '''
    Represents a hidraw node

    See linux/hidraw.h
    '''
    HIDIOCGRDESCSIZE = 0x01
    HIDIOCGRDESC = 0x02
    HIDIOCGRAWINFO = 0x03
    HIDIOCGRAWNAME = 0x04
    HIDIOCGRAWPHYS = 0x05
    HIDIOCSFEATURE = 0x06
    HIDIOCGFEATURE = 0x07
    HIDIOCGRAWUNIQ = 0x08

    HID_NAME_SIZE = 1024

    def __init__(self, path: str) -> None:
        self._path = path
        self._fd = open(path, 'rb+')
        fcntl.fcntl(self._fd, fcntl.F_SETFL, os.O_NONBLOCK)

    def __str__(self) -> str:
        return f'Hidraw({self.path})'

    @property
    def path(self) -> str:
        '''
        Node path
        '''
        return self._path

    @property
    def fd(self) -> BinaryIO:
        '''
        Node file descriptor
        '''
        return self._fd

    @property
    def report_descriptor_size(self) -> int:
        '''
        Size of the report descriptor of the hidraw node
        '''
        return ctypes.c_uint.from_buffer(
            ioctl.IOCTL.IOR(
                'H', self.HIDIOCGRDESCSIZE, ctypes.sizeof(ctypes.c_uint)
            ).perform(self._fd)
        ).value

    @property
    def report_descriptor(self) -> List[int]:
        '''
        Report descriptor of the hidraw node
        '''
        # fcntl.ioctl does not support such big buffer sizes when using the default buffer so we need to provide our own buffer
        buf = array.array(
            'B', self.report_descriptor_size.to_bytes(4, 'little') +
            HidrawReportDescriptor.HID_MAX_DESCRIPTOR_SIZE * b'\x00'
        )

        ioctl.IOCTL.IOR(
            'H', self.HIDIOCGRDESC, ctypes.sizeof(HidrawReportDescriptor)
        ).perform(self._fd, buf=buf)

        ret = HidrawReportDescriptor.from_buffer(buf)
        return list(ret.value)[:ret.size]

    @property
    def info(self) -> Tuple[int, int, int]:
        '''
        Device info of the hidraw node
        '''
        dev_info = HidrawDevinfo.from_buffer(
            ioctl.IOCTL.IOR(
                'H', self.HIDIOCGRAWINFO, ctypes.sizeof(HidrawDevinfo)
            ).perform(self._fd)
        )

        return dev_info.bustype, dev_info.vendor, dev_info.product

    @property
    def name(self) -> str:
        '''
        HID name of the hidraw node
        '''
        return ioctl.IOCTL.IOR(
            'H', self.HIDIOCGRAWNAME, self.HID_NAME_SIZE
        ).perform(self._fd).decode('utf-8').strip('\x00')

    @property
    def phys(self) -> str:
        '''
        HID physical name of the hidraw node
        '''
        return ioctl.IOCTL.IOR(
            'H', self.HIDIOCGRAWPHYS, self.HID_NAME_SIZE
        ).perform(self._fd).decode('utf-8').strip('\x00')

    @property
    def uniq(self) -> str:
        '''
        HID unique identifier of the hidraw node
        '''
        return ioctl.IOCTL.IOR(
            'H', self.HIDIOCGRAWUNIQ, self.HID_NAME_SIZE
        ).perform(self._fd).decode('utf-8').strip('\x00')

    # TODO: HIDIOCSFEATURE, HIDIOCGFEATURE
