# encoding: utf-8

import logging_helper
from uiutil import Position, Label
from uiutil.tk_names import W
from configurationutil.gui import ConfigSelectorFrame
from ... import config
from ...apis import APIS
from ..window import AddEditAPIWindow

logging = logging_helper.setup_logging()


class APIConfigFrame(ConfigSelectorFrame):

    HEADINGS = [
        u'API',
        u'Family',
        u'Host'
    ]

    ADD_EDIT_WINDOW_CLASS = AddEditAPIWindow

    CONFIG_ROOT = config.API_CONFIG

    def __init__(self,
                 *args,
                 **kwargs):
        super(APIConfigFrame, self).__init__(cfg=config.register_api_config,
                                             *args,
                                             **kwargs)

    def draw_records(self):

        apis = APIS()

        select_next_row = True

        for api in sorted(apis):

            if select_next_row:
                self._selected_radio_button.set(api)
                select_next_row = False

            self._radio_list[api] = self.radio_button(frame=self._scroll_frame,
                                                      text=api,
                                                      variable=self._selected_radio_button,
                                                      value=api,
                                                      row=Position.NEXT,
                                                      column=Position.START,
                                                      sticky=W)

            Label(frame=self._scroll_frame,
                  text=apis[api].family,
                  row=Position.CURRENT,
                  column=Position.NEXT,
                  sticky=W)

            Label(frame=self._scroll_frame,
                  text=apis[api].host.key,
                  row=Position.CURRENT,
                  column=Position.NEXT,
                  sticky=W)
