from __future__ import division

from typing import Any, Dict, Iterable, Iterator, List, Optional, Tuple  # NOQA
import datetime
import re
import six

from natsort import humansorted  # type: ignore
import numpy as np  # type: ignore
import pandas as pd  # type: ignore # NOQA

from .population_schema import PopulationSchema, ColumnDefinition

# How small a number of values guarantees categorical
_CATEGORICAL_THRESHOLD = 20

# We're not going to do anything reasonable with humongous cardinality
# categoricals right now, and it suggests a coding issue rather than a real
# categorical.
# TODO(asilvers): Maybe allow ordered categoricals of larger cardinality
_MAX_CATEGORICAL_CARDINALITY = 500

# How many values should cover what fraction of the space to accept
# categorical?
_CATEGORICAL_COVERAGE_COUNT = 20
_CATEGORICAL_COVERAGE_RATIO = 0.1

_ZIP_RE = re.compile('^[0-9]{5}$')

# See also `_populate_values_for_date` in value_vector.py.
_DATE_FORMATS = ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%d.%m.%Y']


class HintValueError(ValueError):
    pass


def guess_schema(df):  # type: (pd.DataFrame) -> PopulationSchema
    """Guesses a schema for a data frame."""
    coldefs = {col: _guess_given_vals(col, df[col]) for col in df.columns}
    return PopulationSchema(coldefs, order=df.columns)


def _guess_given_vals(col_name, data):
    # type: (str, pd.Series) -> ColumnDefinition
    """Returns a guess as to the definition of a column given its data.

    These heuristics are utterly unprincipled and simply seem to work well on a
    minimal set of test datasets. They should be improved as failures crop up.
    """
    if len(data.dropna()) == 0:
        return ColumnDefinition(col_name, 'void', 'Column is empty')

    try:
        unique_vals = data.dropna().unique()
    except TypeError:
        # If the values are non-hashable, give up.
        return ColumnDefinition(col_name, 'void', 'Column is not scalars')

    cardinality = len(unique_vals)
    if cardinality == 1:
        return ColumnDefinition(col_name, 'void', 'Column is constant')

    if _consistent_dates(unique_vals):
        return ColumnDefinition(col_name, 'date')

    # Use categorical for anything with less than 20 values, even numbers.
    if cardinality < _CATEGORICAL_THRESHOLD:
        return _make_categorical_column(
            col_name, unique_vals, 'Only %d distinct values' % cardinality)

    non_num_vals = [v for v in unique_vals if not _numbery(v)]
    if len(non_num_vals) == 0:
        numeric_vals = data.astype(float)
        stat_type, reason = _guess_real_stat_type_and_reason(numeric_vals)
        precision = _guess_precision(numeric_vals)
        return ColumnDefinition(col_name, stat_type,
                                'Contains only numbers (%d of them, %s)' %
                                (cardinality, reason), precision=precision)

    if cardinality == len(data.dropna()):
        return ColumnDefinition(col_name, 'void',
                                'Non-numeric and all values unique')

    counts = data.dropna().value_counts()
    coverage = counts[:_CATEGORICAL_COVERAGE_COUNT].sum() / len(data.dropna())
    if (coverage > _CATEGORICAL_COVERAGE_RATIO and
            cardinality < _MAX_CATEGORICAL_CARDINALITY):
        reason = ('{} distinct values, {} non-numeric, '
                  'first {} cover {:.2%} of the space').format(
                      cardinality, len(non_num_vals),
                      _CATEGORICAL_COVERAGE_COUNT, coverage)
        return _make_categorical_column(col_name, unique_vals, reason)

    # Ignore anything with more than too many distinct non-numeric values and
    # poor coverage.
    nonnum_str = ", ".join(non_num_vals[:3])
    if len(non_num_vals) > 3:
        nonnum_str += ", ..."
    return ColumnDefinition(col_name, 'void',
                            '%d distinct values. %d are non-numeric (%s)' %
                            (cardinality, len(non_num_vals), nonnum_str))


def make_column_from_hint(col_name, data, hint, display_name=None):
    # type: (str, pd.Series, Dict[str, str], str) -> ColumnDefinition
    if 'stat_type' not in hint:
        raise HintValueError(
            'hint %s for column %s does not contain stat_type' % (hint,
                                                                  col_name))

    if hint['stat_type'] == 'void':
        return ColumnDefinition(col_name, 'void', 'Hinted',
                                display_name=display_name)

    elif hint['stat_type'] == 'categorical':
        return _make_categorical_column(col_name,
                                        data.dropna().unique(), 'Hinted',
                                        display_name=display_name)

    elif hint['stat_type'] in ('real', 'realAdditive', 'realMultiplicative',
                               'magnitude'):
        try:
            data = data.astype(float)
        except ValueError:
            # Provide a more explicit error message
            raise HintValueError('Numeric hint %s for column %s, but column '
                                 'contains non-numeric values' % (hint,
                                                                  col_name))

        if hint['stat_type'] == 'realMultiplicative' and (data <= 0).any():
            raise HintValueError(
                'Hinted realMultiplicative, but column contains '
                'non-positive values: %s' % hint)

        if hint['stat_type'] == 'magnitude' and (data < 0).any():
            raise HintValueError(
                'Hinted magnitude, but column contains negative '
                'values: %s' % hint)

        if hint['stat_type'] == 'real':
            stat_type, _ = _guess_real_stat_type_and_reason(data)
        else:
            stat_type = hint['stat_type']

        return ColumnDefinition(col_name, stat_type, 'Hinted',
                                precision=_guess_precision(data),
                                display_name=display_name)
    else:
        raise HintValueError('invalid stat_type hint %s for column %s' %
                             (hint, col_name))


def _make_categorical_column(col_name, unique_vals, reason, display_name=None):
    """Make a categorical column. This will be an ordered categorical if
    we can reasonably guess the order."""
    # TODO(asilvers): Categoricals have to be strings, but auto-converting
    # still allows ambiguity in representations of floats. This probably
    # doesn't get solved until guess is done on the server.
    inferred_cat_values = humansorted(unique_vals.astype(six.text_type))
    # If it looks like zipcodes, it's not ordered.
    if 'zip' in col_name.lower() and all(
            _ZIP_RE.match(v) for v in inferred_cat_values):
        return ColumnDefinition(col_name, 'categorical', reason,
                                values=inferred_cat_values,
                                display_name=display_name)
    # asilvers@ says "this file is called guess.py", and oh boy is this
    # regex a guess. Right now it should just be things that start with numbers
    # or ranges (like 1-3).
    ordery_regex = re.compile('^\d+\.?\d*(-\d+)?($| )')
    if all(re.search(ordery_regex, str(v)) for v in inferred_cat_values):
        return ColumnDefinition(col_name, 'orderedCategorical', reason,
                                values=inferred_cat_values,
                                display_name=display_name)
    # ekbartus@ says "this is lazy shortcutting for a specific case"
    elif set(unique_vals) == {'Agree', 'Somewhat Agree', 'Disagree'}:
        return ColumnDefinition(col_name, 'orderedCategorical', reason,
                                values=['Agree', 'Somewhat Agree',
                                        'Disagree'], display_name=display_name)
    else:
        return ColumnDefinition(col_name, 'categorical', reason,
                                values=inferred_cat_values,
                                display_name=display_name)


def _guess_real_stat_type_and_reason(data):
    # type: (pd.Series) -> Tuple[str, str]
    """Guesses a stat type for `data`."""
    vals = data.dropna().sort_values()
    if (vals < 0).any():
        # In theory there are cases where we want to guess magnitude here,
        # where both the positive and negative halves look log-scaled, but punt
        # on that for now.
        return 'realAdditive', 'not all values are positive'
    if (vals > 0).all():
        # If they're all positive, it makes no sense to be a magnitude
        loggy, reason = _looks_loggy(vals)
        return ('realMultiplicative' if loggy else 'realAdditive'), reason
    else:
        # If they're all non-negative but include 0s, it can't be
        # realMultiplicative, but it might make sense to be a magnitude if the
        # non-zeros look log-scale.
        pos_vals = vals[vals > 0]
        loggy, reason = _looks_loggy(pos_vals)
        return ('magnitude' if loggy else 'realAdditive'), reason


def _looks_loggy(vals):  # type: (List[float]) -> Tuple[bool, str]
    # Compute the correlation of the column's values and their logs with
    # uniform quantiles.
    quantiles = np.linspace(1, len(vals), num=len(vals)) / (len(vals) + 1)
    quantiles_cor = np.corrcoef(quantiles, vals)[0, 1]
    log_quantiles_cor = np.corrcoef(quantiles, np.log(vals))[0, 1]
    if np.isnan(quantiles_cor) or np.isnan(log_quantiles_cor):
        # Should never happen, since we're guaranteed two distinct values.
        raise ValueError('could not infer type for %r' % (vals,))
    # If both uniform and log-uniform quantiles match the distribution of the
    # values well, return realAdditive. Otherwise, pick realMultiplicative if
    # log-uniform quantiles match better, and realAdditive if uniform quantiles
    # match better.
    reason = 'uniform cor. %.3f, log-uniform cor. %.3f' % (quantiles_cor,
                                                           log_quantiles_cor)
    # If uniform matches really well, go with it, even if log-uniform matches a
    # little better.
    if quantiles_cor > 0.95:
        return False, reason

    # Go with uniform unless log-uniform beats it by at least a small amount.
    return (log_quantiles_cor > (quantiles_cor + .01)), reason


def _guess_precision(vals):  # type: (np.ndarray) -> Tuple[int, int]
    """Returns a (n, d) tuple such that `vals` are measured to only n/d.

    For example, if all values are multiples of 1000, returns (1000, 1).
    Returns None if it looks like `vals` use all of the bits available.
    Currently only guesses decimal precision.
    """
    abs_max = np.max(np.abs(vals))
    # Try units of 1,000,000 down to 0.000001, counting down so that we take
    # the coarsest one possible.
    for places in range(-6, 7):
        # If places is 2, `max_normalized_err` is 0.7 on `vals` of
        # [0.01, 0.027, 0.04].
        z = vals * 10**places
        max_normalized_err = np.max(np.abs(np.round(z) - z))
        # If we have at least six places of accuracy, we've found a precision.
        # Except, check `abs_max` so we don't accept either 1e-30 as being even
        # units of 1e-6 since it rounds to zero with 30 places of accuracy, and
        # we don't accept 1e+30 even though it's an exact multiple of 1e+6.
        if (max_normalized_err < 1e-6 and
                10**(-places) <= abs_max < 10**(9 - places)):
            if places < 0:
                return (10**-places, 1)
            else:
                return (1, 10**places)
    return None


def _numbery(val):
    """Returns True if a value looks like a number."""
    try:
        float(val)
        return True
    except (ValueError, TypeError):
        return False


def _parses_as_date(val, fmt):  # type: (Any, str) -> bool
    try:
        datetime.datetime.strptime(val, fmt)
        return True
    except (TypeError, ValueError):
        return False


def _is_numpy_date(v):  # type: (Any) -> bool
    day_type = np.dtype('<M8[D]')
    return isinstance(v, np.datetime64) and not (v - v.astype(day_type))


def _consistent_dates(values):  # type: (Any) -> bool
    """Returns true if `val` is a date or can be parsed as one."""
    if all(isinstance(v, datetime.date) for v in values):
        try:
            return all(v.hour == 0 and v.minute == 0 and v.second == 0
                       for v in values)
        except AttributeError:
            # `pd.Timestamp` and `datetime.datetime` subclass `datetime.date`,
            # but are not "dates." So, if the `hour`, `minute`, or `second`
            # attribute is missing, we know we have a real date.
            return True
    if all(_is_numpy_date(v) for v in values):
        return True
    else:
        # If we can parse the dates unambiguously, then we can treat this as a
        # date.
        matches = [
            fmt for fmt in _DATE_FORMATS if all(
                _parses_as_date(v, fmt) for v in values)
        ]
        return len(matches) == 1
