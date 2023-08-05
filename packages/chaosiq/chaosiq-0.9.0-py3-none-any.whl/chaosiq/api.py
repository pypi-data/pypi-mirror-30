# -*- coding: utf-8 -*-
import json
import os.path
from typing import Any, Dict

from logzero import logger
import requests

from chaosiq.config import get_token
from chaosiq.exceptions import ConfigurationTokenMissing

__all__ = ["call_chaosiq_api"]

CHAOSIQ_API_URL = "https://cloud.chaosiq.io/api"


def call_chaosiq_api(path: str, payload: Dict[str, Any],
                     config: Dict[str, Any],
                     expected_status: int=200) -> requests.Response:
    """
    Perform a call against chaosiq.

    Probably do not bet on this function from outside this package, it will
    likely evolve.
    """
    try:
        token = get_token(config)
    except ConfigurationTokenMissing as err:
        logger.warn(str(err))
        return

    headers = {
        "Accept": "application/json",
        "Authorization": "Bearer {t}".format(t=token),
        "Connection": "close"
    }

    url = "{u}{p}".format(u=CHAOSIQ_API_URL, p=path)
    if "chaosiq" not in payload:
        payload["chaosiq"] = {}
    payload["chaosiq"]["workspace"] = config.get("workspace", "personal")
    try:
        r = requests.post(
            url, json=payload, headers=headers, timeout=(2, 10), verify=False)
    except requests.exceptions.SSLError as s:
        logger.warn(
            "Failed to talk over TLS with the ChaosIQ service")
    except requests.ConnectTimeout as c:
        logger.warn(
            "Failed to contact the ChaosIQ API service. Try again soon!")
    except requests.ConnectionError as e:
        logger.warn(
            "The ChaosIQ API service looks busy. Try again soon!")
    except requests.ReadTimeout as t:
        logger.warn(
            "The ChaosIQ API service took long to respond. Try again soon!")
    except requests.HTTPError as x:
        logger.debug(str(x))
        logger.error(
            "Something went wrong. Please contact ChaosIQ.")
    else:
        if r.status_code != expected_status:
            logger.debug(r.text)
            return

        return r
