from __future__ import print_function
from io import open
import sys

from setuptools import (
    find_packages,
    setup,
)

try:
    from xpybutil.compat import (
        xinerama,
        xproto,
        randr,
    )
except:
    print('')
    print('xpybutil requires the X Python Binding')
    print('See: http://cgit.freedesktop.org/xcb/xpyb/')
    print('More options: xpyb-ng:', 'https://github.com/dequis/xpyb-ng',
          'and xcffib:', 'https://github.com/tych0/xcffib')
    sys.exit(1)

setup(
    name="xpybutil",
    maintainer="Fenner Macrae",
    maintainer_email="fmacrae.dev@gmail.com",
    version="0.0.1",
    license="WTFPL",
    description="An incomplete xcb-util port plus some extras",
    long_description=open('README', 'r', encoding='utf-8').read(),
    url="http://github.com/fennerm/xpybutil",
    packages=find_packages(),
    package=['xpybutil'],
    keywords='xorg X xcb xpyb xcffib',
    data_files=[('share/doc/xpybutil', ['README', 'COPYING'])]
)
