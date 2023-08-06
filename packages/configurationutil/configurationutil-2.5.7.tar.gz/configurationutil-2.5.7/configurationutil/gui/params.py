# encoding: utf-8

import logging_helper
from copy import deepcopy
from uiutil import BaseScrollFrame, BaseFrame, Position, Separator, Label, Button, TextEntry, ChildWindow
from uiutil.tk_names import StringVar, askquestion, E, W, S, NSEW, EW

logging = logging_helper.setup_logging()


class ParamsConfigFrame(BaseFrame):

    BUTTON_WIDTH = 2
    KEY_ENTRY_WIDTH = 15
    VALUE_ENTRY_WIDTH = 30
    HEADINGS = [
        u'Key',
        u'Value'
    ]

    def __init__(self,
                 params=None,
                 *args,
                 **kwargs):

        BaseFrame.__init__(self,
                           *args,
                           **kwargs)

        self._params = {} if params is None else params

        self._selected_radio_button = StringVar(self.parent)
        self._radio_list = {}

        self._param_elements = {}

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
                                             canvas_width=460)
        self._scroll_frame.grid(row=1,
                                column=0,
                                sticky=NSEW)

        self.draw_records()

        self._scroll_frame.nice_grid_columns()

    def draw_records(self):

        select_next_row = True

        for param in sorted(self._params):
            if select_next_row:
                self._selected_radio_button.set(param)
                select_next_row = False

            self._draw_param(param, self._params[param])

        self._draw_param(u'', u'')

    def _draw_param(self,
                    key,
                    value):

        self._radio_list[key] = self.radio_button(frame=self._scroll_frame,
                                                  variable=self._selected_radio_button,
                                                  value=key,
                                                  row=Position.NEXT,
                                                  column=Position.START,
                                                  sticky=W)

        key_entry = TextEntry(frame=self._scroll_frame,
                              value=key,
                              width=self.KEY_ENTRY_WIDTH,
                              row=Position.CURRENT,
                              column=Position.NEXT,
                              sticky=EW)

        value_entry = TextEntry(frame=self._scroll_frame,
                                value=value,
                                width=self.VALUE_ENTRY_WIDTH,
                                row=Position.CURRENT,
                                column=Position.NEXT,
                                sticky=EW)

        self._param_elements[key] = (key_entry, value_entry)

    def _build_button_frame(self):

        self.button_frame = BaseFrame(row=Position.NEXT,
                                      column=Position.START,
                                      sticky=(E, S))

        Button(frame=self.button_frame,
               name=u'_delete_record_button',
               text=u'-',
               width=self.BUTTON_WIDTH,
               command=self._delete,
               row=Position.START,
               column=Position.START)

        Button(frame=self.button_frame,
               name=u'_add_record_button',
               text=u'+',
               width=self.BUTTON_WIDTH,
               command=self._add,
               row=Position.CURRENT,
               column=Position.NEXT)

        self.button_frame.nice_grid()

    def _add(self):

        self.update_params()

        self._scroll_frame.destroy()
        self._build_records_frame()
        self.nice_grid()

        self.update_geometry()

    def _delete(self):
        selected = self._selected_radio_button.get()

        if selected:

            result = askquestion(u"Delete Record",
                                 u"Are you sure you want to delete {r}?".format(r=selected),
                                 icon=u'warning',
                                 parent=self)

            if result == u'yes':
                del self._params[selected]
                del self._param_elements[selected]

                self.update_params()

                self._scroll_frame.destroy()
                self._build_records_frame()
                self.nice_grid()

                self.update_geometry()

    def update_params(self):

        for param in self._param_elements:
            param_key = self._param_elements[param][0]
            param_value = self._param_elements[param][1]

            if param_key.value:
                self._params[param_key.value] = param_value.value


class ParamsConfigWindow(ChildWindow):

    def __init__(self,
                 params=None,
                 *args,
                 **kwargs):

        self.params = params

        super(ParamsConfigWindow, self).__init__(*args,
                                                 **kwargs)

    def _draw_widgets(self):
        self.title(u"Edit Params")

        self.config = ParamsConfigFrame(params=self.params,
                                        sticky=NSEW)

    def close(self):
        self.config.update_params()


class ParamsConfigButton(Button):

    def __init__(self,
                 frame,
                 params,
                 tooltip=True,
                 *args,
                 **kwargs):

        """ Custom button used for editing passed in params

        :param params: dict containing params to be configured.
        :param tooltip: True to enable tooltip display of current params.
        :param args: Do not pass positional arguments.
        :param kwargs:
        """

        self._params = params
        self._enable_tooltip = tooltip
        self._frame = frame

        kwargs[u'command'] = self._edit_params

        if u'text' not in kwargs:
            kwargs[u'text'] = u'Edit Params'

        if self._enable_tooltip:
            kwargs[u'tooltip'] = self._tooltip_kwargs

        super(Button, self).__init__(*args,
                                     **kwargs)

    def _edit_params(self):

        params = deepcopy(self._params)

        window = ParamsConfigWindow(params=params,
                                    fixed=True,
                                    parent_geometry=self._frame.winfo_toplevel().winfo_geometry())

        window.transient()
        window.grab_set()
        self._frame.wait_window(window)

        self._params = params

        if self._enable_tooltip:
            self.tooltip.text = self._tooltip_kwargs

    @property
    def _tooltip_kwargs(self):

        if len(self._params) > 1:
            string = u'{\n'

            for param in sorted(self._params):
                string += u' {k}: {v}\n'.format(k=param,
                                                v=self._params[param])

            string += u'}'

        elif len(self._params) == 1:
            string = str(self._params)

        else:
            string = u'No parameters configured'

        return {
            u'text': string,
            u'justify': u'left'
        }

    @property
    def params(self):
        return self._params
