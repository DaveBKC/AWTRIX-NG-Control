"""Config and per-device HTTP options."""
import re
import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN, CONF_PREFIX, CONF_NAME

class AwtrixControlFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION=1
    async def async_step_user(self,user_input=None):
        errors={}
        if user_input is not None:
            prefix=user_input[CONF_PREFIX].strip().strip('/')
            if not re.fullmatch(r'[A-Za-z0-9_-]+',prefix): errors[CONF_PREFIX]='invalid_prefix'
            else:
                await self.async_set_unique_id(prefix.lower()); self._abort_if_unique_id_configured()
                return self.async_create_entry(title=user_input[CONF_NAME].strip(),data={CONF_NAME:user_input[CONF_NAME].strip(),CONF_PREFIX:prefix},options={'host':user_input.get('host','').strip()})
        return self.async_show_form(step_id='user',data_schema=vol.Schema({vol.Required(CONF_NAME,default='Ulanzi TC002'):str,vol.Required(CONF_PREFIX,default='tc002'):str,vol.Optional('host',default=''):str}),errors=errors)
    @staticmethod
    def async_get_options_flow(config_entry): return AwtrixOptionsFlow()

class AwtrixOptionsFlow(config_entries.OptionsFlow):
    async def async_step_init(self,user_input=None):
        if user_input is not None: return self.async_create_entry(title='',data={'host':user_input.get('host','').strip()})
        return self.async_show_form(step_id='init',data_schema=vol.Schema({vol.Optional('host',default=self.config_entry.options.get('host','')):str}))
