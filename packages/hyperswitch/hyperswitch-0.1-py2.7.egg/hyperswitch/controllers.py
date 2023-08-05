import pygtk
pygtk.require('2.0')
import gtk

import ewmh
from hyperswitch.filters import CamelHumpFilter
from hyperswitch.windows import ActiveWindowRepository


class PySwitchController(object):
    def __init__(self):
        self._window = PySwitchWindow()
        self._window.connect("delete_event", gtk.main_quit)
        self._window.set_filter_changed_callback(self._filter_changed)

        self._filter = CamelHumpFilter()

        self._ewmh = ewmh.EWMH()
        self._repo = ActiveWindowRepository(self._ewmh)

        self._window_list = gtk.ListStore(object)
        for win in self._repo.load_windows():
            self._window_list.append([win])

        self._window_list = self._window_list.filter_new()
        self._window_list.set_visible_func(self._filter_function)

        self._window.set_window_list(self._window_list)

    def main(self):
        self._window.show()
        gtk.main()

    def _filter_changed(self, new_filter):
        self._filter.filter_string = new_filter
        self._window_list.refilter()

    def _filter_function(self, model, item):
        win = model.get_value(item, 0)
        return self._filter.is_filter_match(win.title)


class PySwitchWindow(gtk.Window):
    def __init__(self):
        gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)

        self.set_position(gtk.WIN_POS_CENTER)
        self.set_size_request(640, 250)
        self.set_border_width(5)

        self.connect('key-press-event', self._key_pressed)

        self._vert_box = gtk.VBox(False, 0)
        self.add(self._vert_box)

        # Entry for filter string        
        self._filter_entry = gtk.Entry()
        self._filter_entry.connect("changed", self._filter_entry_changed, None)
        self._filter_entry.connect("activate", self._launch_current, None)
        self._vert_box.pack_start(self._filter_entry, expand=False)
        self._filter_entry.show()

        # List view for active windows
        self._window_list = gtk.TreeView()
        self._window_list.set_enable_search(False)
        self._window_list.set_headers_visible(False)

        self._title_column = gtk.TreeViewColumn('Title')
        self._window_list.append_column(self._title_column)

        self._title_renderer = gtk.CellRendererText()
        self._title_column.pack_start(self._title_renderer)
        self._title_column.set_cell_data_func(self._title_renderer, self._get_window_title)

        self._window_selection = self._window_list.get_selection()
        self._window_selection.set_mode(gtk.SELECTION_SINGLE)

        self._vert_box.pack_start(self._window_list)
        self._window_list.show()

        self._vert_box.show()

    @staticmethod
    def _get_window_title(column, cell, tree_model, iter, user_data=None):
        win = tree_model.get_value(iter, 0)
        cell.set_property('text', win.title)

    def _filter_entry_changed(self, widget, data=None):
        if self._filter_changed_callback is not None:
            self._filter_changed_callback(widget.get_text())

    def _get_selected(self):
        (model, iter) = self._window_selection.get_selected()

        if iter is None:
            # Default to first item
            iter = model.get_iter_first()

        return iter

    def _launch_current(self, widget, data=None):
        selection = self._get_selected()

        current_win = self._window_list_store.get_value(selection, 0)

        current_win.bring_to_front()
        gtk.main_quit()

    def _select_previous_window(self):
        current_selection = self._get_selected()

        # Convert to path to hack an equivalent for the missing iter_prev function
        current_selection = self._window_list_store.get_path(current_selection)
        prev_window = current_selection
        prev_window = prev_window[0] - 1

        # Select the last item if we are currently at the first item
        if prev_window < 0:
            prev_window = len(self._window_list_store) - 1

        self._window_selection.select_path(prev_window)

    def _select_next_window(self):
        current_selection = self._get_selected()

        next_window = self._window_list_store.iter_next(current_selection)

        if next_window is None:
            next_window = self._window_list_store.get_iter_first()

        self._window_selection.select_iter(next_window)

    def _key_pressed(self, widget, event):
        key = gtk.gdk.keyval_name(event.keyval)

        if key == 'Up':
            self._select_previous_window()
            return True
        elif key == 'Down':
            self._select_next_window()
            return True
        elif key == 'Escape':
            gtk.main_quit()
            return True

    def set_window_list(self, windows):
        """
        Sets the list of windows to display.
        windows should be a TreeModel of Window objects
        """
        self._window_list_store = windows
        self._window_list.set_model(self._window_list_store)

    def set_filter_changed_callback(self, callback):
        self._filter_changed_callback = callback
