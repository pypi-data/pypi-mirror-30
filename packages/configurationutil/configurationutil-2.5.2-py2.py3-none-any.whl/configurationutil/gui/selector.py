# encoding: utf-8

import logging_helper
from future.utils import with_metaclass
from abc import abstractmethod, ABCMeta
from uiutil import BaseScrollFrame, BaseFrame, Position, Separator, Label, Button
from uiutil.tk_names import StringVar, askquestion, E, W, S, NSEW
from ..configuration import Configuration

logging = logging_helper.setup_logging()


class ConfigSelectorFrame(with_metaclass(ABCMeta, BaseFrame)):

    BUTTON_WIDTH = 15
    HEADINGS = []

    ADD_EDIT_WINDOW_CLASS = None

    CONFIG_ROOT = None

    def __init__(self,
                 cfg=Configuration,
                 *args,
                 **kwargs):

        BaseFrame.__init__(self,
                           *args,
                           **kwargs)

        self._cfg = cfg()

        self._selected_radio_button = StringVar(self.parent)
        self._radio_list = {}

        self._build_headings_frame()

        Separator(row=Position.NEXT,
                  column=Position.START)

        self._build_records_frame()

        Separator(row=Position.NEXT,
                  column=Position.START)

        self._build_button_frame()

        self.nice_grid()

    def _build_headings_frame(self):

        self.headings_frame = BaseFrame(row=Position.START,
                                        column=Position.START,
                                        sticky=NSEW)

        for heading in self.HEADINGS:
            Label(frame=self.headings_frame,
                  text=heading,
                  column=Position.START if heading == self.HEADINGS[0] else Position.NEXT,
                  row=Position.CURRENT,
                  sticky=W)

        Separator(frame=self.headings_frame,
                  row=Position.NEXT,
                  column=Position.START,
                  columnspan=len(self.HEADINGS))

        self.headings_frame.nice_grid_columns()

    def _build_records_frame(self):

        self._scroll_frame = BaseScrollFrame(parent=self,
                                             canvas_height=120,
                                             canvas_width=220)
        self._scroll_frame.grid(row=1,
                                column=0,
                                sticky=NSEW)

        self.draw_records()

        self._scroll_frame.nice_grid_columns()

    @abstractmethod
    def draw_records(self):

        """ Draw the config records.

        Please use self._scroll_frame as the parent frame for UI elements.

        """

        pass

    def _build_button_frame(self):

        self.button_frame = BaseFrame(row=Position.NEXT,
                                      column=Position.START,
                                      sticky=(E, W, S))

        Button(frame=self.button_frame,
               name=u'_delete_record_button',
               text=u'Delete',
               width=self.BUTTON_WIDTH,
               command=self._delete,
               row=Position.START,
               column=Position.START)

        Button(frame=self.button_frame,
               name=u'_add_record_button',
               text=u'Add',
               width=self.BUTTON_WIDTH,
               command=self._add,
               row=Position.CURRENT,
               column=Position.NEXT)

        Button(frame=self.button_frame,
               name=u'_edit_record_button',
               text=u'Edit',
               width=self.BUTTON_WIDTH,
               command=self._edit,
               row=Position.CURRENT,
               column=Position.NEXT)

        self.button_frame.nice_grid()

    def _add(self):
        window = self.ADD_EDIT_WINDOW_CLASS(fixed=True,
                                            parent_geometry=self.parent.winfo_toplevel().winfo_geometry())

        window.transient()
        window.grab_set()
        self.parent.wait_window(window)

        self._scroll_frame.destroy()
        self._build_records_frame()
        self.nice_grid()

        self.parent.master.update_geometry()

    def _edit(self):
        window = self.ADD_EDIT_WINDOW_CLASS(selected_record=self._selected_radio_button.get(),
                                            edit=True,
                                            fixed=True,
                                            parent_geometry=self.parent.winfo_toplevel().winfo_geometry())

        window.transient()
        window.grab_set()
        self.parent.wait_window(window)

        self._scroll_frame.destroy()
        self._build_records_frame()
        self.nice_grid()

        self.parent.master.update_geometry()

    def _delete(self):
        selected = self._selected_radio_button.get()

        result = askquestion(u"Delete Record",
                             u"Are you sure you want to delete {r}?".format(r=selected),
                             icon=u'warning',
                             parent=self)

        if result == u'yes':
            key = u'{cfg}.{int}'.format(cfg=self.CONFIG_ROOT,
                                        int=selected)

            del self._cfg[key]

            self._scroll_frame.destroy()
            self._build_records_frame()
            self.nice_grid()

            self.parent.master.update_geometry()
