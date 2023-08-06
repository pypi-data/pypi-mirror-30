from collections import defaultdict
from six.moves.urllib.parse import quote
from typing import Any, Dict, List, Set, Union, TYPE_CHECKING  # NOQA
import datetime
import re
import six
import time
import warnings

from pandas import DataFrame  # type: ignore
# This is imported from `future` so its type checking is wonky
import html  # type: ignore
import numpy as np  # type: ignore
import pandas as pd  # type: ignore

from .api import Visibility
from .api import CallableEndpoint  # NOQA
from .population_model import PopulationModel
from .population_schema import PopulationSchema  # NOQA
from .rowids import rowids_from_arg

if TYPE_CHECKING:  # avoid an import cycle
    from .session import Session  # NOQA

# Always refetch a population's schema if this duration has elapsed since the
# last fetch, to pick up changes made outside the edpanalyst session.
SCHEMA_INVALIDATION_SECS = 30

EPOCH = datetime.datetime(1970, 1, 1)
DAY_TYPE = np.dtype('<M8[D]')


def _date_to_days(v, col_name):  # type: (Any, str) -> int
    """Converts a date-like object or str, `v`, to days since the epoch."""
    if isinstance(v, str):
        try:
            v = datetime.datetime.strptime(v, '%Y-%m-%d')
        except ValueError:
            raise ValueError('value %r in column %r is not an ISO 8601 date' %
                             (v, col_name))
    elif isinstance(v, np.datetime64) and not (v - v.astype(DAY_TYPE)):
        return v.astype(DAY_TYPE).astype(int)
    elif (not isinstance(v, pd.Timestamp) and
          not isinstance(v, datetime.datetime) and
          not isinstance(v, datetime.date)):
        raise ValueError('value %r in column %r is not convertible to a date' %
                         (v, col_name))
    return (datetime.datetime(v.year, v.month, v.day) - EPOCH).days


class AmbiguityWarning(UserWarning):
    pass


class Population(object):

    def __init__(
            self,
            pid,  # type: str
            session,  # type: Session
            endpoint=None,  # type: CallableEndpoint
            time_fn=time.time):  # type: (...) -> None
        self._pid = pid
        self._session = session
        if endpoint is None:
            endpoint = self._session._endpoint.population.sub_url(self._pid)
        self._endpoint = endpoint
        self.name  # Cause an error if this population doesn't exist
        self._schema = None  # type: PopulationSchema
        self._schema_fetch_time = None  # type: float
        self._time_fn = time_fn

    # Map column names to their display names.
    def _col_display_name_map(self):  # type: () -> Dict[str, str]
        return {
            col_def.name: col_def.display_name or col_def.name
            for col_def in self.schema
        }

    # Map from column name to a map from that column's categorical values
    # to their display values.
    def _display_value_map(self):  # type: () -> Dict[str, Dict[str, str]]
        return {
            col_def.name:
            {v.value: v.display_value or v.value
             for v in col_def.values}
            for col_def in self.schema
            if col_def.stat_type in ['categorical', 'orderedCategorical']
        }

    def __str__(self):  # type: () -> str
        return ('Population(id=%r, name=%r)' % (self._pid, self.name))

    def __repr__(self):  # type: () -> str
        return str(self)

    def _repr_html_(self):  # type: () -> str
        return (('<span>%s</span><br>' %
                 (html.escape(self.name),)) + '<span>Models:</span>'
                '<ul>' + ''.join([('<li>' + m._repr_html_() + '</li>')
                                  for m in self.models]) + '</ul>')

    def rename(self, name):  # type: (str) -> None
        """Rename this population. Equivalent to `pop.name = name`."""
        self._endpoint.rename.post(json=name)

    def _metadata(self):  # type: () -> Dict[str, Any]
        # TODO(asilvers): Half of this metadata (e.g. creation_time) doesn't
        # ever change, so making a call for each access is unnecessary and
        # wasteful. But if it's causing problems we probably have bigger
        # problems. Think about this at some point.
        return self._endpoint.get().json()

    @property
    def id(self):  # type: () -> str
        return self._pid

    @property
    def name(self):  # type: () -> str
        """Get or set the population's name."""
        return self._metadata()['name']

    @name.setter
    def name(self, name):
        self.rename(name)

    @property
    def description(self):  # type: () -> str
        """Get or set the population's description."""
        return self._metadata()['description']

    @description.setter
    def description(self, desc):
        self._endpoint.description.post(json=('' if desc is None else desc))

    @property
    def creation_time(self):  # type: () -> float
        return self._metadata()['creation_time']

    @property
    def user_metadata(self):  # type: () -> Dict[str, str]
        return self._metadata()['user_metadata']

    @property
    def models(self):  # type: () -> List[PopulationModel]
        return [
            PopulationModel(model['id'], self._session)
            for model in self._metadata()['models']
        ]

    @property
    def schema(self):  # type: () -> PopulationSchema
        if self._schema is None or self._time_fn(
        ) - self._schema_fetch_time > SCHEMA_INVALIDATION_SECS:
            resp = self._endpoint.schema.get()
            self._schema = PopulationSchema.from_json(resp.json())
            self._schema_fetch_time = self._time_fn()

        return self._schema

    def visibility(self):  # type: () -> Visibility
        """Fetches visibility for this population."""
        resp = self._endpoint.visibility.get()
        return Visibility.from_json(resp.json())

    def delete(self):  # type: () -> None
        """Delete this population.

        This Population object will become invalid after deletion.
        """
        self._endpoint.delete()

    def make_public(self):  # type: () -> Visibility
        """Make this population public.

        Returns the ACL for the population after the modification.
        """
        req = {'public': True}
        resp = self._endpoint.visibility.patch(json=req)
        return Visibility.from_json(resp.json())

    def add_reader(self, reader,
                   send_email=False):  # type: (str, bool) -> Visibility
        """Add `reader` to this population's reader list.

        Args:
            reader: The email of the user who should have read access to the
                population.
            send_email: Whether to send an email to the new reader.

        Returns the ACL for this model after the modification.
        """
        req = {'readers': [reader], 'send_email': send_email}
        resp = self._endpoint.visibility.patch(json=req)
        return Visibility.from_json(resp.json())

    def add_reader_domain(self, domain):  # type): (str) -> Visibility
        """Give all users on `domain` read access to this population.

        Args:
            domain: The domain to grant read access to. Must begin with '@'.

        Returns the ACL for this model after the modification.
        """
        req = {'reader_domain': domain}
        resp = self._endpoint.visibility.patch(json=req)
        return Visibility.from_json(resp.json())

    def remove_reader(self, reader):  # type: (str) -> Visibility
        """Remove `reader` from this population's reader list.

        Args:
            reader: The email of the user whose read access to remove.

        Returns the ACL for this model after the modification. If the given
        user does not already have read access, this method will return
        successfully but have no effect.
        """
        req = {'remove_readers': [reader]}
        resp = self._endpoint.visibility.patch(json=req)
        return Visibility.from_json(resp.json())

    def remove_reader_domain(self, domain):  # type: (str) -> Visibility
        """Remove domain-wide read access from `domain`.

        Users in `domain` whose emails were individually added will not have
        their read access removed.

        Args:
            reader: The domain to remove read access from. Must begin with '@'.

        Returns the ACL for this model after the modification. If the given
        domain does not already have read access, this method will return
        successfully but have no effect.
        """
        req = {'remove_reader_domain': domain}
        resp = self._endpoint.visibility.patch(json=req)
        return Visibility.from_json(resp.json())

    def _find_latest(self, models):
        """Return the latest built model, or None if none exist."""
        if len(models) == 0:
            # If no models are being built then it's probably silly to wait
            raise ValueError('This population has no models')

        built = [m for m in models if m['build_progress']['status'] == 'built']
        if len(built) > 0:
            # TODO(asilvers): This is actually looking at models' creation
            # times, not how recently they finished building. That's probably
            # not quite right.
            latest = max(built, key=lambda m: m['creation_time'])
            return PopulationModel(latest['id'], self._session)
        else:
            return None

    # This method is a bit vestigial now that we're lazily building everything.
    # It should almost always return instantly.
    def latest(self, wait=60):  # type: (int) -> PopulationModel
        """Returns this population's most recently built model.

        This will wait up to `wait` seconds for a model to finish building.

        Raises `ValueError` if `wait` is 0 (or falsey) and this model has no
        already-built models, or if `wait` seconds have elapsed and no models
        have finished.
        """
        timeout_time = time.time() + wait
        while True:
            models = self._metadata()['models']
            latest = self._find_latest(models)
            if latest:
                return latest
            if time.time() > timeout_time:
                break
            time.sleep(1)
        # Don't mention timeouts if we didn't wait
        if not wait:
            raise ValueError('This population has no built models')
        raise ValueError('Timed out waiting for models to finish building')

    def build_model(
            self,
            name=None,  # type: str
            ensemble_size=16,  # type: int
            iterations=100,  # type: int
            max_seconds=None,  # type: int
            builder='lazy',  # type: str
            random_seed=None,  # type: int
    ):  # type: (...) -> PopulationModel
        """Build a model from this population.

        Args:
            name: The name of the newly built model
            ensemble_size: How many sub-models to build in the model ensemble.
            iterations: The number of iterations to build for
            max_seconds: If set, the model build will attempt to take no longer
                than this many seconds to build. This is not a hard limit.
            builder: Which builder to use.
            random_seed: A random seed to make the build deterministic.
        """
        name = name or self.name
        req = {
            'name': name,
            'build_def': {
                'num_models': ensemble_size,
                'builder': builder,
                'duration': {
                    'iterations': iterations
                }
            }
        }  # type: Dict[str, Any]
        if random_seed is not None:
            req['build_def']['random_seed'] = random_seed
        if max_seconds is not None:
            req['build_def']['duration']['max_seconds'] = max_seconds
        resp = self._endpoint.build.post(json=req)
        return PopulationModel(resp.json()['id'], self._session)

    def clone_data(self, name=None, schema=None, hints=None):
        # type(str, PopulationSchema, Dict) -> None
        """Create a new population with the same data as this one, and possibly
        a new schema.
        """
        req = {}
        if name:
            req['name'] = name
        if schema:
            req['schema'] = schema
        if hints:
            req['hints'] = hints

        resp = self._endpoint.clone_data.post(json=req)
        return Population(resp.json()['id'], self._session)

    def set_column_display_name(self, column,
                                display_name):  # type(str, str) -> None
        """Sets the display name for a column.

        Passing None or an empty string removes a previously set display name.
        """
        display_name = display_name or ''
        # URL path components need to be escaped twice in order for embedded
        # slashes to be handled correctly.
        endpoint = self._endpoint.column.sub_url(quote(column)).display_name
        endpoint.post(json=display_name)
        # Clear cached schema so we pick up the new value.
        self._schema = None

    def set_column_description(self, column,
                               description):  # type(str, str) -> None
        """Sets the description for a column.

        Passing None or an empty string removes a previously set description.
        """
        description = description or ''
        endpoint = self._endpoint.column.sub_url(quote(column)).description
        endpoint.post(json=description)
        self._schema = None

    def set_categorical_display_value(
            self, column, categorical_value,
            display_value):  # type(str, str, str) -> None
        """Sets the display value for a value of a categorical column.

        Passing None or an empty string removes a previously set display value.
        """
        display_value = display_value or ''
        col_endpoint = self._endpoint.column.sub_url(quote(column))
        val_endpoint = col_endpoint.values.sub_url(quote(categorical_value))
        val_endpoint.display_value.post(json=display_value)
        self._schema = None

    def set_categorical_value_description(
            self, column, categorical_value,
            description):  # type(str, str, str) -> None
        """Sets the description for a value of a categorical column.

        Passing None or an empty string removes a previously set description.
        """
        description = description or ''
        col_endpoint = self._endpoint.column.sub_url(quote(column))
        val_endpoint = col_endpoint.values.sub_url(quote(categorical_value))
        val_endpoint.description.post(json=description)
        self._schema = None

    def column_groups(self):  # type () -> Dict[str, Set[str]]
        """Returns a dict describing the population's column groups.

        Column groups are defined by including an identifier starting with a
        '#' character in the descriptions of all columns in the group. The
        keys of the returned dict are the group identifiers and the values
        are sets of column names in that group.
        """
        s = self.schema
        groups = defaultdict(set)  # type: Dict[str, Set[str]]
        group_id_regex = re.compile(r'#\w+')
        for col in s.columns():
            desc = s[col].description
            if desc:
                for group_id in group_id_regex.findall(desc):
                    groups[group_id].add(col)
        return groups

    def select(
            self,
            targets=None,  # type: List[str]
            where=None,  # type: Dict[str, Union[str, int, float]]
            rowids=None,  # type: List[int]
            limit=None,  # type: int
            random_seed=None,  # type: int
            use_display_names=False  # type: bool
    ):  # type: (...) -> DataFrame
        """Return a subset of a population's data.

        The response DataFrame's index corresponds to the population's rowids.

        Args:
            targets: The list of columns to select. If not specified, returns
                all modeled columns.
            where: Limit the results to those rows where the values of the
                specified columns match the values in `where`. If not
                specified, `select` returns all rows.
            rowids: The rowids to restrict results to. If not specified
                returns all rows.
            limit: Return at most `limit` rows. If this would otherwise return
                more than that, the rows to return are chosen randomly.
            random_seed: Optional random seed between 0 and 2**32; only
                meaningful if `limit` is specified.
        """
        targets = self._columns_from_arg(targets)
        req = {'target': targets}  # type: Dict[str, Any]
        if rowids is not None:
            req['rowids'] = rowids_from_arg(rowids)
        if where:
            req['where'] = where
        if limit is not None:
            req['limit'] = int(limit)
        if random_seed is not None:
            req['random_seed'] = random_seed
        resp = self._endpoint.select.post(json=req)
        respjson = resp.json()
        data = {
            t: self._deserialize_column(t, respjson['columns'][t])
            for t in respjson['columns']
        }
        df = DataFrame(data, columns=targets, index=respjson['rowids'])
        if use_display_names:
            df = self._apply_display_names(df)
        return df

    # Modify `df` to use columns' and categorical values' display names.
    def _apply_display_names(self, df):
        # Replace categorical column values with their display values.
        # We could just `df.replace` except for
        # https://github.com/pandas-dev/pandas/issues/5338
        dvm = self._display_value_map()
        for col in df.columns:
            if col in dvm:
                df[col].replace(dvm[col], inplace=True)
        # Rename the columns to their display names
        df.rename(columns=self._col_display_name_map(), inplace=True)
        return df

    def add_derived_column(self, column, dependencies, script, stat_type,
                           categorical_values=None):
        """Define a derived column whose value is computed from other columns.

        Args:
            column: Name of the derived column. This may be an existing derived
                column, in which case it will be updated. It may not be an
                existing non-derived column.
            dependencies: List of columns whose values may be used in the
                computation of the derived column.
            script: Lua source code to compute the value of the derived column.
            stat_type: Stat type of the derived column.
            categorical_values: For categorical derived columns, the possible
                string values the column may have.
        """
        endpoint = self._endpoint.derived_column.sub_url(quote(column))
        req = {
            'value_script': script,
            'stat_type': stat_type,
            'dependencies': dependencies,
            'categorical_values': categorical_values or [],
        }
        endpoint.post(json=req)
        self._schema = None

    def remove_derived_column(self, column):
        """Remove a previously defined derived column.

        Args:
            column: Name of the derived column to remove.
        """
        endpoint = self._endpoint.derived_column.sub_url(quote(column))
        endpoint.delete()
        self._schema = None

    def _columns_from_arg(self, columns):
        """Given a columns argument, return a list of column names. Handles
        None and non-list sequences, and expands column group identifiers."""
        self._check_column_list(columns)
        if columns is None:
            return list(self._modeled_columns())
        # Check if there are possible column group identifiers.
        if not any(c.startswith('#') for c in columns):
            return list(columns)
        # Expand column group identifiers to the corresponding column names.
        column_groups = self.column_groups()
        all_columns = self.schema.columns()
        expanded_columns = []  # type: List[str]
        for c in columns:
            if c in column_groups:
                if c in all_columns:
                    warnings.warn(
                        '"%s" is both a column name and a column group '
                        'identifier. Using the single column' % (c,),
                        AmbiguityWarning)
                    expanded_columns.append(c)
                else:
                    expanded_columns.extend(column_groups[c])
            else:
                expanded_columns.append(c)
        return list(expanded_columns)

    def _check_column_list(self, columns):
        """Make sure someone didn't accidentally pass a string as a list."""
        if isinstance(columns, six.string_types):
            raise ValueError('`columns` takes a sequence, not a single string')
        return columns

    def _modeled_columns(self):
        return [
            cname for cname in self.schema.columns()
            if self.schema[cname].stat_type != 'void'
        ]

    def _serializable_value(self, v, col_name):  # type: (Any, str) -> Any
        """Converts a data frame element to one that can be JSON-serialized."""
        desc = self.schema[col_name]
        if v is None:
            return None
        elif desc.stat_type == 'date':
            return _date_to_days(v, col_name)
        else:
            return v

    def _serializable_value_dict(self, d):
        # type: (Dict[str, Any]) -> Dict[str, Any]
        """Converts a key-value dict to one that can be JSON-serialized.

        `d` is a dict of the sort usually passed as `given_values`. The
        returned dict is the same, but with all the values who are not directly
        representable in JSON replaced with ones that are. Right now, that
        means dates are converted to days since the epoch.
        """
        self._check_column_list(d.keys())
        r = {}
        for c, v in six.iteritems(d):
            r[c] = self._serializable_value(v, c)
        return r

    def _serializable_column_dict(self, d):
        # type: (Dict[str, List[Any]]) -> Dict[str, List[Any]]
        """Converts a key-to-list dict to one that can be JSON-serialized.

        Similar to `_serializable_value_dict`, but `d` is a map to lists of
        values, not values. This can be applied to the return value of
        `DataFrame.to_dict(orient='list')`.
        """
        self._check_column_list(d.keys())
        r = {}
        for c in d:
            r[c] = [self._serializable_value(v, c) for v in d[c]]
        return r

    def _deserialize_column(self, col_name, values):
        # type: (str, List[Any]) -> List[Any]
        """Converts a column returned in JSON to a Python representation.

        This is the inverse of what `_serializable_column_dict` does to each
        column.
        """
        if self.schema[col_name].stat_type == 'date':
            return pd.to_datetime(values, unit='D')  # "D" means "days"
        else:
            return values
