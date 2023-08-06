from typing import Any, Dict, List, NamedTuple, Optional  # NOQA
from typing import Text
import os

from configparser import RawConfigParser  # type: ignore

from .population_schema import PopulationSchema  # NOQA

_Config = NamedTuple('_Config', [('edp_url', str), ('bearer_token', Text)])
"""Authentication configuration from ~/.edp_auth or config._config"""


def _config(profile_name=None, edp_url=None, bearer_token=None):
    # type: (str, str, Text) -> _Config
    """Returns a `_Config`, looking up fields in a variety of places.

    Usually, values will come from the "default" profile in ~/.edp_auth,
    which can be overridden by either `profile_name` or, if that is unset,
    `EDP_PROFILE` in the environment.

    You can override individual `_Config` fields by passing arguments to
    this constructor, which passes them to this function.
    """
    profile_name = profile_name or os.environ.get('EDP_PROFILE', 'default')
    config = _read_edp_auth(profile_name)
    edp_url = (edp_url or os.environ.get('EDP_URL') or config.get('edp_url') or
               'https://betaplatform.empirical.com')
    bearer_token = (bearer_token or os.environ.get('EDP_BEARER_TOKEN') or
                    config.get('bearer_token'))
    if not bearer_token:
        raise ValueError('No bearer_token was found in %r section of %r or '
                         'the EDP_BEARER_TOKEN environment variable, nor '
                         'passed to constructor.' % (profile_name,
                                                     _config_path()))
    return _Config(edp_url=edp_url, bearer_token=bearer_token)


def _read_edp_auth(profile_name):  # type: (str) -> Dict[str, Any]
    """Returns the named section of ~/.edp_auth or {} if not found."""
    config_path = _config_path()
    if not os.path.isfile(config_path):
        return {}
    config = RawConfigParser()
    with open(config_path, 'rt') as cf:
        config.read_file(cf)
    if profile_name not in config.sections():
        return {}
    return dict(config.items(profile_name))


def _config_path():  # type: () -> str
    """Return the path to the configuration file based on os and environment.
    """
    default = os.path.expanduser(os.path.join('~', '.edp_auth'))
    return os.environ.get('EDP_CONFIG_FILE', default)
