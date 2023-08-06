"""
tomatyLabel.py
~~~~~~~~

label class for the tomaty application

:copyright: @ 2018
:author: elias julian marko garcia
:license: MIT, see LICENSE
"""
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject, GLib, Gdk


class TomatyTimer():
    def __init__(self):
        """the label object inherents from Gtk.Label and reflects the status
        of the users' tomatoro progression via  """
