# encoding: utf-8

import logging_helper
from uiutil import Position, Label
from uiutil.tk_names import W
from configurationutil.gui import ConfigSelectorFrame
from ... import config
from ... import Environments
from ..window import AddEditEnvironmentWindow

logging = logging_helper.setup_logging()


class EnvironmentConfigFrame(ConfigSelectorFrame):

    HEADINGS = [
        u'Environment',
        u'Location'
    ]

    ADD_EDIT_WINDOW_CLASS = AddEditEnvironmentWindow

    CONFIG_ROOT = config.ENVIRONMENT_CONFIG

    def __init__(self,
                 *args,
                 **kwargs):
        super(EnvironmentConfigFrame, self).__init__(cfg=config.register_environment_config,
                                                     *args,
                                                     **kwargs)

    def draw_records(self):

        environments = Environments()

        select_next_row = True

        for env in sorted(environments):

            if select_next_row:
                self._selected_radio_button.set(env)
                select_next_row = False

            self._radio_list[env] = self.radio_button(frame=self._scroll_frame,
                                                      text=env,
                                                      variable=self._selected_radio_button,
                                                      value=env,
                                                      row=Position.NEXT,
                                                      column=Position.START,
                                                      sticky=W)

            try:
                location = environments[env].location

            except AttributeError:
                location = u''

            Label(frame=self._scroll_frame,
                  text=location,
                  row=Position.CURRENT,
                  column=Position.NEXT,
                  sticky=W)
