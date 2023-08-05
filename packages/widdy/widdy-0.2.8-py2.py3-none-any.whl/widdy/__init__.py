from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
# expose all widgets and important types in main module
from widdy.widgets import App, Frame, Handlers, Header, KeyFunc, LineBox, Menu, MenuItem, Pal, Text  # noqa
from widdy.styles import Style                                                                       # noqa

