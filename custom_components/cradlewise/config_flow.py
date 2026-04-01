"""Config flow for Cradlewise."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from pycradlewise import (
    CradlewiseAuth,
    CradlewiseAuthError,
    CradlewiseClient,
    get_app_config,
)

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult

from .const import CONF_EMAIL, CONF_PASSWORD, DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_EMAIL): str,
        vol.Required(CONF_PASSWORD): str,
    }
)


class CradlewiseConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Cradlewise."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                app_config = await get_app_config()
            except Exception:
                _LOGGER.exception("Failed to fetch Cradlewise app config")
                errors["base"] = "cannot_connect"
                return self.async_show_form(
                    step_id="user",
                    data_schema=STEP_USER_DATA_SCHEMA,
                    errors=errors,
                )

            auth = CradlewiseAuth(
                email=user_input[CONF_EMAIL],
                password=user_input[CONF_PASSWORD],
                app_config=app_config,
            )
            client = CradlewiseClient(auth)

            try:
                await auth.authenticate()
                cradles = await client.discover_cradles()
            except CradlewiseAuthError:
                errors["base"] = "invalid_auth"
            except Exception:
                _LOGGER.exception("Unexpected error during setup")
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(user_input[CONF_EMAIL].lower())
                self._abort_if_unique_id_configured()

                cradle_count = len(cradles)
                title = f"Cradlewise ({cradle_count} crib{'s' if cradle_count != 1 else ''})"

                return self.async_create_entry(title=title, data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
