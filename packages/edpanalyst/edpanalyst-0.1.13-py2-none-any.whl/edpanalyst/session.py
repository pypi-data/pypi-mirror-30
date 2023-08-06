from typing import Any, Dict, List, Text  # NOQA
import os
import requests
import six
import sys
import traceback

from pandas import DataFrame  # type: ignore
import pandas as pd  # type: ignore

from .config import _config
from .api import CallableEndpoint, NoSuchGeneratorError
from .population import Population
from .population_model import PopulationModel
from .population_schema import PopulationSchema  # NOQA


class Session(object):
    """Provides a Python API to the Empirical Data Platform."""

    def __init__(
            self,
            profile=None,  # type: str
            edp_url=None,  # type: str
            bearer_token=None,  # type: Text
            endpoint=None  # type: CallableEndpoint
    ):  # type: (...) -> None
        """Create an EDP session.

        This class is thread-safe if requests.Session is thread-safe. It very
        much seems that it should be, but the requests developers are hesitant
        to declare it so. See
        https://github.com/kennethreitz/requests/issues/1871
        https://github.com/kennethreitz/requests/issues/2766 and
        http://stackoverflow.com/questions/18188044/is-the-session-object-from-python-requests-library-thread-safe
        Nevertheless, we're treating it as thread-safe until we discover
        otherwise.

        Args:
            profile: The name of a profile to use. If not provided, the
                EDP_PROfILE environment variable is checked, and if not set
                then the "default" profile is used.
            bearer_token: The JWT to be used for authentication soon. If not
                provided, the EDP_BEARER_TOKEN environment variable is checked,
                and if not set the value from the selected profile is used.
            edp_url: An endpoint to connect to. If not set, the EDP_URL
                environment variable is checked, and if not set, the value from
                the selected profile is used, and if not set then a default of
                "https://betaplatform.empirical.com" is used.
        """
        self.config = _config(profile_name=profile, edp_url=edp_url,
                              bearer_token=bearer_token)
        self._session = requests.Session()
        if self.config.bearer_token:
            self._session.headers.update({
                'Authorization': 'Bearer ' + self.config.bearer_token
            })
        if endpoint is None:
            endpoint = CallableEndpoint(self.config.edp_url, self._session)
        self._endpoint = endpoint.rpc
        self._auth_endpoint = endpoint.auth
        # Try and list so we raise an error if you're not auth'd
        self.list_populations()

    def get_username(self):  # type: () -> str
        """Get the authenticated user's email address."""
        return self._auth_endpoint.username.get().text

    def list(self, keyword=None):
        pops = self._endpoint.population.get().json()
        models = [m for pop in pops for m in pop['models']]
        models_df = DataFrame({
            'id': [pm['id'] for pm in models],
            'name': [pm['name'] for pm in models],
            'parent_id': [pm.get('parent_id') for pm in models],
            'creation_time': [
                pd.to_datetime(pm['creation_time'], unit='s') for pm in models
            ],
            'status': [pm['build_progress']['status'] for pm in models],
        }, columns=['id', 'name', 'parent_id', 'creation_time', 'status'])
        return _filtered(models_df, keyword)

    def list_populations(self, keyword=None):
        pops = self._endpoint.population.get().json()
        pops_df = DataFrame({
            'id': [pop['id'] for pop in pops],
            'name': [pop['name'] for pop in pops],
            'creation_time': [
                pd.to_datetime(pop['creation_time'], unit='s') for pop in pops
            ],
            'num_models': [len(pop['models']) for pop in pops]
        }, columns=['id', 'name', 'creation_time', 'num_models'])
        return _filtered(pops_df, keyword)

    def population(self, pid):  # type: (str) -> Population
        """Returns the Population corresponding to `pid`."""
        try:
            return Population(pid, self)
        except NoSuchGeneratorError:
            if pid.startswith('pm-'):
                raise NoSuchGeneratorError(
                    'You used a Population Model ID, '
                    'calling a population requires the Population ID.')
            else:
                raise NoSuchGeneratorError('Unknown Population ID')

    def popmod(self, pmid):  # type: (str) -> PopulationModel
        """Returns the PopulationModel corresponding to `pmid`."""
        try:
            return PopulationModel(pmid, self)
        except NoSuchGeneratorError:
            if pmid.startswith('p-'):
                raise NoSuchGeneratorError(
                    'You used a Population ID, '
                    'calling a population model requires the '
                    'Population Model ID.')
            else:
                raise NoSuchGeneratorError('Unknown Population Model ID')

    def upload(
            self,
            data,  # type: DataFrame
            name,  # type: str
            schema=None,  # type: PopulationSchema
            hints=None,  # type: Dict[str, Any]
            autobuild=True,  # type: bool
            random_seed=None,  # type: int
            this_is_a_lot_of_data_but_i_know_what_im_doing=False  # type: bool
    ):  # type: (...) -> Population
        """Create a population in EDP from uploaded data.

        Args:
            data: The data to create a population from.
            name: The name of the newly created population.
            schema: The schema describing the data. If not provided the server
                will attempt to guess one for you.
            hints: Provide hints to the guesser if not providing a schema.
            autobuild: If true, a number of model builds will be started
                automatically after creating the population
            random_seed: A random seed to make the build deterministic. Only
                meaningful with autobuild=True.
        """
        if len(data) == 0:
            raise ValueError('`data` must not be empty')
        if name is None:
            raise ValueError('`name` must not be None')
        # TODO(asilvers): We require you to upload strings for categoricals so
        # that there's no ambiguity as to the representation as there could be
        # if they were floats. But this auto-conversion doesn't really solve
        # that issue, it just hides it from you. These issues go away when we
        # upload raw data and do assembly server-side, since presumably at that
        # point you're uploading strings anyway (e.g. CSV from a file).
        # TODO(asilvers): Also consider not doing this for numeric columns.
        if schema and hints:
            raise ValueError('At most one of `schema` and `hints` '
                             'can be provided.')
        stringed_df = data.copy()
        for col in data.columns:
            stringed_df[col] = stringed_df[col].astype(six.text_type)
        nulled_df = stringed_df.where(pd.notnull(data), None)
        json_data = nulled_df.to_dict(orient='list')

        # Grab an arbitrary row's length. If the row lengths are inconsistent
        # the server will yell at us.
        num_rows = len(list(json_data.values())[0])
        post_data = {
            'name': name,
            'data': {
                'num_rows': num_rows,
                'columns': json_data
            },
        }  # type: Dict[str, Any]
        if schema:
            post_data['schema'] = schema.to_json()
        if hints:
            post_data['hints'] = hints
        if this_is_a_lot_of_data_but_i_know_what_im_doing:
            post_data['this_is_a_lot_of_data_but_i_know_what_im_doing'] = True

        pid = self._endpoint.population.post(json=post_data).json()['id']
        pop = Population(pid=pid, session=self)
        if autobuild:
            pop.build_model(name=name + ' (auto)', iterations=500,
                            ensemble_size=32, max_seconds=300,
                            random_seed=random_seed)
        return pop

    def upload_file(
            self,
            path,  # type: str
            name=None,  # type: str
            autobuild=True,  # type: bool
            random_seed=None,  # type: int
    ):  # type: (...) -> Population
        name = name if name is not None else os.path.basename(path)
        url = '%s/rpc/population/upload_raw_data' % (self.config.edp_url,)
        with open(path, 'rb') as f:
            resp = self._session.post(url, files={name: (name, f)})
        resp.raise_for_status()
        pid = resp.json()['id']
        pop = Population(pid=pid, session=self)
        if autobuild:
            pop.build_model(name=name + ' (auto)', iterations=500,
                            ensemble_size=32, max_seconds=300,
                            random_seed=random_seed)
        return pop

    def send_feedback(self, message, send_traceback=True):
        # type: (str, bool) -> None
        """Report feedback to Empirical's support team.

        Sends `message` along with the most recent exception (unless
        `send_traceback` is False).
        """
        req = {'message': message}
        if send_traceback and hasattr(sys, 'last_traceback'):
            req['traceback'] = ''.join(traceback.format_tb(sys.last_traceback))
        self._endpoint.feedback.post(json=req)


def _filtered(items, keyword):
    """Filter a data frame of population / population models."""
    if not keyword:
        return items

    idx = []
    for r in range(items.shape[0]):
        if (items.name[r].lower().find(keyword.lower()) != -1):
            idx.append(r)
    return items.loc[idx]
