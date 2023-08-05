# encoding: utf-8

import logging_helper
from uiutil import Position, Label
from uiutil.tk_names import W
from configurationutil.gui import ConfigSelectorFrame
from ... import config
from ...hosts import Hosts
from ..window import AddEditHostWindow

logging = logging_helper.setup_logging()


class HostConfigFrame(ConfigSelectorFrame):

    HEADINGS = [
        u'Host',
        u'Domain',
        u'Port'
    ]

    ADD_EDIT_WINDOW_CLASS = AddEditHostWindow

    CONFIG_ROOT = config.HOST_CONFIG

    def __init__(self,
                 *args,
                 **kwargs):
        super(HostConfigFrame, self).__init__(cfg=config.register_host_config,
                                              *args,
                                              **kwargs)

    def draw_records(self):

        hosts = Hosts()

        select_next_row = True

        for host in sorted(hosts):

            if select_next_row:
                self._selected_radio_button.set(host)
                select_next_row = False

            self._radio_list[host] = self.radio_button(frame=self._scroll_frame,
                                                       text=host,
                                                       variable=self._selected_radio_button,
                                                       value=host,
                                                       row=Position.NEXT,
                                                       column=Position.START,
                                                       sticky=W)

            Label(frame=self._scroll_frame,
                  text=hosts[host].domain,
                  row=Position.CURRENT,
                  column=Position.NEXT,
                  sticky=W)

            Label(frame=self._scroll_frame,
                  text=hosts[host].port,
                  row=Position.CURRENT,
                  column=Position.NEXT,
                  sticky=W)
