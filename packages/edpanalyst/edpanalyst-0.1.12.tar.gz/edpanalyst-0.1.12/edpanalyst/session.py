from typing import cast, Any, Dict, List, Sequence, Set, Text, Union  # NOQA
import os
import six
import sys
import traceback

from pandas import DataFrame  # type: ignore
import pandas as pd  # type: ignore

from .edpclient import NoSuchGeneratorError
from .edpclient import EdpClient, CallableEndpoint
from .population import Population
from .population_model import PopulationModel
from .population_schema import PopulationSchema  # NOQA


class Session(object):

    def __init__(
            self,
            profile=None,  # type: str
            edp_url=None,  # type: str
            bearer_token=None,  # type: Text
            endpoint=None  # type: CallableEndpoint
    ):  # type: (...) -> None
        self._client = EdpClient(profile=profile, edp_url=edp_url,
                                 bearer_token=bearer_token)
        if endpoint is None:
            url = (self._client.config.edp_url + '/rpc')
            endpoint = CallableEndpoint(url, self._client._session)
        self._endpoint = endpoint
        # Try and list so we raise an error if you're not auth'd
        self.list_populations()

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
            return Population(pid, self._client)
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
            return PopulationModel(pmid, self._client)
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
        pid = self._client.upload_population(data=json_data, schema=schema,
                                             hints=hints, name=name)
        pop = Population(pid=pid, client=self._client)
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
        url = '%s/rpc/population/upload_raw_data' % (
            self._client.config.edp_url,)
        with open(path, 'rb') as f:
            resp = self._client._session.post(url, files={name: (name, f)})
        resp.raise_for_status()
        pid = resp.json()['id']
        pop = Population(pid=pid, client=self._client)
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
