#!/usr/bin/env python
import sys

import ioctl.hidraw


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f'usage: {sys.argv[0]} /dev/hidrawX')
        exit(1)

    d = ioctl.hidraw.Hidraw(sys.argv[1])

    print(f'Name: {d.name}')
    print(f'Device Info: {", ".join(hex(value) for value in d.info)}')
    print(f'Physical Name: {d.phys}')
    print(f'Unique Name: {d.uniq or "None"}')
    print(f'Report Descriptor Size: {d.report_descriptor_size}')
    print(f'Report Descriptor: {d.report_descriptor}')
