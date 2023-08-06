# encoding: utf-8

import logging_helper
from future.utils import iteritems
from uiutil import Position, Label, TextEntry, Combobox
from uiutil.tk_names import N, E, W, EW
from configurationutil.gui import AddEditConfigFrame, ParamsConfigFrame
from ..._constants import EnvironmentKeysConstant
from ... import config
from ... import Environments, APIS

logging = logging_helper.setup_logging()


class EnvironmentAPIConfigFrame(ParamsConfigFrame):

    def _draw_param(self,
                    key,
                    value):

        self._radio_list[key] = self.radio_button(frame=self._scroll_frame,
                                                  variable=self._selected_radio_button,
                                                  value=key,
                                                  row=Position.NEXT,
                                                  column=Position.START,
                                                  sticky=W)

        apis = APIS()
        families = list(set(api.family for _, api in iteritems(apis)))

        # TODO: add some filtering to combo boxes!
        family_combo = Combobox(frame=self._scroll_frame,
                                value=key,
                                values=[u''] + families,
                                row=Position.CURRENT,
                                column=Position.NEXT,
                                sticky=EW)

        api_combo = Combobox(frame=self._scroll_frame,
                             value=value,
                             values=[u''] + list(apis),
                             row=Position.CURRENT,
                             column=Position.NEXT,
                             sticky=EW)

        self._param_elements[key] = (family_combo, api_combo)


class AddEditEnvironmentFrame(AddEditConfigFrame):

    CONFIG_ROOT = config.ENVIRONMENT_CONFIG
    DEFAULTS_KEY = EnvironmentKeysConstant.apis

    def __init__(self,
                 *args,
                 **kwargs):
        super(AddEditEnvironmentFrame, self).__init__(cfg=config.register_environment_config,
                                                      inheritable_items=sorted(Environments().keys()),
                                                      *args,
                                                      **kwargs)

    def draw_defaults(self):

        Label(text=u'Location:',
              row=Position.NEXT,
              column=Position.START,
              sticky=E)

        self._location = TextEntry(value=self.selected_record.get(EnvironmentKeysConstant.location, u'')
                                   if self.edit else u'',
                                   row=Position.CURRENT,
                                   column=Position.NEXT,
                                   sticky=EW)

        Label(text=u'APIs:',
              row=Position.NEXT,
              column=Position.START,
              sticky=(N, E))

        self._env_apis = self.selected_record.get(self.DEFAULTS_KEY, {}) if self.edit else {}

        self._apis = EnvironmentAPIConfigFrame(params=self._env_apis,
                                               row=Position.CURRENT,
                                               column=Position.NEXT,
                                               sticky=EW)

    def save_other(self,
                   new_host):

        """ prepare any other params for saving. """

        if self._location.value:
            new_host[EnvironmentKeysConstant.location] = self._location.value

        return new_host

    def save_defaults(self):
        self._apis.update_params()

        return self._env_apis
