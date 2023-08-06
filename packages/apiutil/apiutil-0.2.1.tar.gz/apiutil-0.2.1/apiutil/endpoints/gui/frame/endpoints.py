# encoding: utf-8

import logging_helper
from uiutil import Position, Label
from uiutil.tk_names import W
from configurationutil.gui import ConfigSelectorFrame
from ... import config
from ...endpoints import Endpoints
from ..window import AddEditEndpointWindow

logging = logging_helper.setup_logging()


class EndpointConfigFrame(ConfigSelectorFrame):

    HEADINGS = [
        u'Endpoint',
        u'Path'
    ]

    ADD_EDIT_WINDOW_CLASS = AddEditEndpointWindow

    CONFIG_ROOT = config.ENDPOINT_CONFIG

    def __init__(self,
                 *args,
                 **kwargs):
        super(EndpointConfigFrame, self).__init__(cfg=config.register_endpoint_config,
                                                  *args,
                                                  **kwargs)

    def draw_records(self):

        endpoints = Endpoints()

        select_next_row = True

        for endpoint in sorted(endpoints):

            if select_next_row:
                self._selected_radio_button.set(endpoint)
                select_next_row = False

            self._radio_list[endpoint] = self.radio_button(frame=self._scroll_frame,
                                                           text=endpoint,
                                                           variable=self._selected_radio_button,
                                                           value=endpoint,
                                                           row=Position.NEXT,
                                                           column=Position.START,
                                                           sticky=W)

            Label(frame=self._scroll_frame,
                  text=endpoints[endpoint].path,
                  row=Position.CURRENT,
                  column=Position.NEXT,
                  sticky=W)
