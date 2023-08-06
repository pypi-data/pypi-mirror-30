#!/usr/bin/env python

from datetime import datetime
import unittest
import warnings

from mock import call, MagicMock  # type: ignore
from pandas import DataFrame  # type: ignore
from pandas.util.testing import (  # type: ignore
    assert_frame_equal, assert_series_equal)
import matplotlib.pyplot  # type: ignore
import numpy as np  # type: ignore
import pandas as pd

from edpanalyst import (PopulationSchema, Population, PopulationModel,
                        PopulationModelExperimental)
import edpanalyst

# The population model metadata you use if you don't care about it in your test
PM = {
    'id': 'pm-17',
    'parent_id': 'p-14',
    'name': 'dontcare',
    'creation_time': 1234,
    'build_progress': {
        'status': 'built'
    },
    'user_metadata': {}
}
WXYZ_SCHEMA = PopulationSchema.from_json({
    'columns': [{
        'name': 'w',
        'stat_type': 'realAdditive'
    }, {
        'name': 'x',
        'stat_type': 'realAdditive'
    }, {
        'name': 'y',
        'stat_type': 'realAdditive'
    }, {
        'name': 'z',
        'stat_type': 'realAdditive'
    }]
})
XYZ_NAME_SCHEMA = PopulationSchema.from_json({
    'identifying_columns': ['name'],
    'columns': [{
        'name': 'name',
        'stat_type': 'void'
    }, {
        'name': 'x',
        'stat_type': 'realAdditive'
    }, {
        'name': 'y',
        'stat_type': 'realAdditive'
    }, {
        'name': 'z',
        'stat_type': 'realAdditive'
    }]
})


class SessionTest(unittest.TestCase):

    def setUp(self):
        warnings.simplefilter('error')
        self._mock_endpoint = MagicMock()
        self._session = edpanalyst.Session(bearer_token='ignored',
                                           endpoint=self._mock_endpoint)

    def test_complains_on_creation(self):
        mock_endpoint = MagicMock()
        mock_endpoint.rpc.population.get.return_value = FakeResponse(
            None, status_code=401)
        with self.assertRaises(ValueError):
            edpanalyst.Session(endpoint=mock_endpoint)


def _pop_with_mocked_backend(desc, schema=None):
    mock_endpoint = MagicMock()
    mock_endpoint.get.return_value = FakeResponse(desc)
    if schema:
        mock_endpoint.schema.get.return_value = FakeResponse(schema.to_json())
    pop = Population(desc['id'], session=None, endpoint=mock_endpoint)
    mock_ses = MagicMock()
    mock_ses.config.edp_url = 'baseurl'
    pop._session = mock_ses
    return pop, mock_endpoint


class TestPopulation(unittest.TestCase):

    def setUp(self):
        warnings.simplefilter('error')

    def test_repr_html(self):
        desc = {'id': 'p-7', 'name': 'MyPop', 'models': [PM]}
        pop, mock_endpoint = _pop_with_mocked_backend(desc, WXYZ_SCHEMA)
        # assertRegexpMatches is deprecated but needed in python2
        warnings.simplefilter('ignore', DeprecationWarning)
        self.assertRegexpMatches(
            pop._repr_html_(),
            'href="baseurl/explorer/population_model/pm-17"')

    def test_latest(self):
        desc = {
            'id':
                'p-7',
            'name':
                'MyPop',
            'models': [
                {
                    'id': 'pm-72',
                    'build_progress': {
                        'status': 'built'
                    },
                    'creation_time': 123
                },
                {
                    'id': 'pm-12',
                    'build_progress': {
                        'status': 'built'
                    },
                    'creation_time': 456
                },
                {
                    'id': 'pm-81',
                    'build_progress': {
                        'status': 'unbuilt'
                    },
                    'creation_time': 789
                },
                {
                    'id': 'pm-19',
                    'build_progress': {
                        'status': 'built'
                    },
                    'creation_time': 0
                },
            ]
        }
        pop, mock_endpoint = _pop_with_mocked_backend(desc, WXYZ_SCHEMA)
        self.assertEqual('pm-12', pop.latest()._pmid)

    def test_latest_with_no_models(self):
        desc = {
            'id': 'p-7',
            'name': 'MyPop',
            'models': [],
        }
        pop, mock_endpoint = _pop_with_mocked_backend(desc, WXYZ_SCHEMA)
        with self.assertRaises(ValueError):
            pop.latest()

    def test_latest_no_wait_with_no_built_models(self):
        desc = {
            'id':
                'p-7',
            'name':
                'MyPop',
            'models': [{
                'id': 'pm-81',
                'build_progress': {
                    'status': 'unbuilt'
                },
                'creation_time': 789
            }]
        }
        pop, mock_endpoint = _pop_with_mocked_backend(desc, WXYZ_SCHEMA)
        with self.assertRaises(ValueError):
            pop.latest(wait=False)


def _popmod_with_mocked_backend(desc, schema=None):
    mock_endpoint = MagicMock()
    mock_endpoint.get.return_value = FakeResponse(desc)
    popmod = PopulationModel(desc['id'], session=None, endpoint=mock_endpoint)
    # Schema requests go through the parent population.
    mock_pop_endpoint = MagicMock()
    if schema:
        mock_pop_endpoint.schema.get.return_value = (FakeResponse(
            schema.to_json()))
    # select on a PopulationModel calls through to the parent Population.
    # mock_endpoint.select.post = mock_pop_endpoint.select.post
    popmod._parent = Population(desc['parent_id'], session=None,
                                endpoint=mock_pop_endpoint)
    return popmod, mock_endpoint, mock_pop_endpoint


class TestPopulationModel(unittest.TestCase):

    def setUp(self):
        warnings.simplefilter('error')

    def test_repr_html(self):
        desc = {
            'id': PM['id'],
            'parent_id': None,
            'name': 'myname',
            'creation_time': 0,
            'build_progress': {
                'status': 'built'
            },
            'user_metadata': {}
        }
        popmod, mock_endpoint, _ = (_popmod_with_mocked_backend(
            desc, WXYZ_SCHEMA))
        mock_client = MagicMock()
        mock_client.config.edp_url = 'baseurl'
        popmod._session = mock_client
        self.assertEqual('<a href="baseurl/explorer/population_model/pm-17" '
                         'target="_blank">Explore myname</a>',
                         popmod._repr_html_())

    def test_experimental_property(self):  # type: () -> None
        popmod, _, _ = _popmod_with_mocked_backend(PM, WXYZ_SCHEMA)
        self.assertIsInstance(popmod.experimental, PopulationModelExperimental)


class TestSelect(unittest.TestCase):

    def setUp(self):
        warnings.simplefilter('error')

    def test_select(self):
        popmod, mock_endpoint, mock_pop_endpoint = (
            _popmod_with_mocked_backend(PM, WXYZ_SCHEMA))

        mock_pop_endpoint.select.post.return_value = FakeResponse({
            'columns': {
                'x': [2, 3, 4, 5, 6],
                'y': [9, 8, 7, 6, 5]
            },
            'rowids': [0, 1, 2, 3, 4]
        })

        expected = DataFrame({
            'x': [2, 3, 4, 5, 6],
            'y': [9, 8, 7, 6, 5]
        }, columns=['x', 'y'], index=[0, 1, 2, 3, 4])
        sel = popmod.select(['x', 'y'])
        assert_frame_equal(sel, expected)

        expected_req = {'target': ['x', 'y']}
        mock_pop_endpoint.select.post.assert_called_once_with(
            json=expected_req)

    def test_select_with_given(self):
        popmod, mock_endpoint, mock_pop_endpoint = (
            _popmod_with_mocked_backend(PM, WXYZ_SCHEMA))

        mock_pop_endpoint.select.post.return_value = FakeResponse({
            'columns': {
                'x': [9, 8, 7, 6, 5],
                'y': [2, 3, 4, 5, 6]
            },
            'rowids': [0, 1, 2, 3, 4]
        })

        expected = DataFrame({
            'y': [2, 3, 4, 5, 6],
            'x': [9, 8, 7, 6, 5]
        }, columns=['y', 'x'], index=[0, 1, 2, 3, 4])
        sel = popmod.select(['y', 'x'], where={'z': 8})
        assert_frame_equal(sel, expected)

        expected_req = {'target': ['y', 'x'], 'where': {'z': 8}}
        mock_pop_endpoint.select.post.assert_called_once_with(
            json=expected_req)

    def test_select_with_index_as_rowids(self):
        popmod, mock_endpoint, mock_pop_endpoint = (
            _popmod_with_mocked_backend(PM, WXYZ_SCHEMA))

        mock_pop_endpoint.select.post.return_value = FakeResponse({
            'columns': {
                'x': [2, 3, 4, 5, 6],
                'y': [9, 8, 7, 6, 5]
            },
            'rowids': [0, 1, 2, 3, 4]
        })

        popmod.select(['x', 'y'], rowids=pd.Index([8, 1]))

        expected_req = {'target': ['x', 'y'], 'rowids': [8, 1]}
        mock_pop_endpoint.select.post.assert_called_once_with(
            json=expected_req)


class TestColumnAssociation(unittest.TestCase):

    def setUp(self):
        warnings.simplefilter('error')

    def test_mutual_information(self):
        popmod, mock_endpoint, _ = _popmod_with_mocked_backend(PM, WXYZ_SCHEMA)

        mock_endpoint.relation.post.return_value = FakeResponse({
            'response_columns': ['x', 'y'],
            'predictor_columns': ['z'],
            'elements': [1, .75]
        })

        expected = DataFrame([('x', 'z', 1), ('y', 'z', .75)],
                             columns=['X', 'Y', 'I']).set_index(['X',
                                                                 'Y'])['I']
        mi = popmod.mutual_information(['x', 'y'], ['z'])
        assert_series_equal(mi, expected)

        expected_req = {
            'response_columns': ['x', 'y'],
            'predictor_columns': ['z'],
            'given': {},
            'statistic': 'mutual information'
        }
        mock_endpoint.relation.post.assert_called_once_with(json=expected_req)

    def test_mutual_information_with_given_values(self):
        popmod, mock_endpoint, _ = _popmod_with_mocked_backend(PM, WXYZ_SCHEMA)

        mock_endpoint.relation.post.return_value = FakeResponse({
            'response_columns': ['w', 'x', 'z'],
            'predictor_columns': ['w', 'x', 'z'],
            'elements': [1, 2, 3, 4, 5, 6, 7, 8, 9]
        })

        popmod.mutual_information(given_values={'y': 19})

        # Drops out 'y' because it's in givens
        expected_req = {
            'response_columns': ['w', 'x', 'z'],
            'predictor_columns': ['w', 'x', 'z'],
            'given': {
                'y': 19
            },
            'statistic': 'mutual information'
        }
        mock_endpoint.relation.post.assert_called_once_with(json=expected_req)

    def test_mutual_information_with_given_columns(self):
        popmod, mock_endpoint, _ = _popmod_with_mocked_backend(PM, WXYZ_SCHEMA)

        mock_endpoint.relation.post.return_value = FakeResponse({
            'response_columns': ['w', 'x', 'z'],
            'predictor_columns': ['w', 'x', 'z'],
            'elements': [1, 2, 3, 4, 5, 6, 7, 8, 9]
        })

        popmod.mutual_information(given_columns=['y'])

        # Drops out 'y' because it's in givens
        expected_req = {
            'response_columns': ['w', 'x', 'z'],
            'predictor_columns': ['w', 'x', 'z'],
            'given': {},
            'given_columns': ['y'],
            'statistic': 'mutual information'
        }
        mock_endpoint.relation.post.assert_called_once_with(json=expected_req)

    def test_mutual_information_with_overlapping_cols(self):
        popmod, mock_endpoint, _ = _popmod_with_mocked_backend(PM, WXYZ_SCHEMA)

        # 'y' is in both columns and givens
        with self.assertRaises(ValueError):
            popmod.mutual_information(response_columns=['x', 'y'],
                                      given_values={
                                          'y': 19,
                                          'z': 13
                                      })

    def test_mutual_information_diffable(self):
        popmod, mock_endpoint, _ = _popmod_with_mocked_backend(PM, WXYZ_SCHEMA)

        mock_endpoint.relation.post.side_effect = [
            FakeResponse({
                'target': ['x', 'y'],
                'elements': [1, .75, .6, 1]
            }),
            FakeResponse({
                'target': ['x', 'y'],
                'elements': [1, .5, .5, 1]
            }),
        ]

        expected = DataFrame([('x', 'x', 0), ('x', 'y', .1), ('y', 'x', .25),
                              ('y', 'y', 0)],
                             columns=['X', 'Y', 'I']).set_index(['X',
                                                                 'Y'])['I']
        mi1 = popmod.mutual_information(['x', 'y'], ['x', 'y'])
        mi2 = popmod.mutual_information(['x', 'y'], ['x', 'y'])
        assert_series_equal(mi1 - mi2, expected)

    def test_classic_dep_prob(self):
        popmod, mock_endpoint, _ = _popmod_with_mocked_backend(PM, WXYZ_SCHEMA)

        mock_endpoint.relation.post.return_value = FakeResponse({
            'response_columns': ['x', 'y'],
            'predictor_columns': ['x'],
            'elements': [1, .75]
        })

        popmod.classic_dep_prob(['x', 'y'], ['x'])

        expected_req = {
            'response_columns': ['x', 'y'],
            'predictor_columns': ['x'],
            'given': {},
            'statistic': 'classic dep prob'
        }
        mock_endpoint.relation.post.assert_called_once_with(json=expected_req)

    def test_column_relevance(self):
        popmod, mock_endpoint, _ = _popmod_with_mocked_backend(PM, WXYZ_SCHEMA)

        mock_endpoint.relation.post.return_value = FakeResponse({
            'response_columns': ['x', 'y'],
            'predictor_columns': ['x', 'y'],
            'elements': [None, .4, .6, None]
        })

        expected = DataFrame([('x', 'x', np.nan), ('x', 'y', .6),
                              ('y', 'x', .4), ('y', 'y', np.nan)],
                             columns=['X', 'Y', 'I']).set_index(['X',
                                                                 'Y'])['I']
        mi = popmod.column_relevance(['x', 'y'], ['x', 'y'])
        assert_series_equal(mi, expected)

        expected_req = {
            'response_columns': ['x', 'y'],
            'predictor_columns': ['x', 'y'],
            'given': {},
            'statistic': 'mutual information',
            'prob_greater_than': .1
        }
        mock_endpoint.relation.post.assert_called_once_with(json=expected_req)

    def test_relevant_columns(self):
        col_objs = [{
            'name': colname,
            'stat_type': 'realAdditive'
        } for colname in ['x', 'a', 'b', 'c']]
        schema = PopulationSchema.from_json({'columns': col_objs})
        popmod, mock_endpoint, _ = _popmod_with_mocked_backend(PM, schema)

        mock_endpoint.relation.post.return_value = FakeResponse({
            'response_columns': ['x'],
            'predictor_columns': ['a', 'b', 'c', 'd'],
            'elements': [.5, .3, .8, .1]
        })

        relevant_cols = popmod.relevant_columns('x', num_cols=3)
        expected = DataFrame([('c', .8), ('a', .5), ('b', .3)],
                             columns=['column', 'depprob'])
        assert_frame_equal(relevant_cols, expected)

        expected_req = {
            'response_columns': ['x'],
            'predictor_columns': ['a', 'b', 'c'],
            'given': {},
            'statistic': 'classic dep prob'
        }
        mock_endpoint.relation.post.assert_called_once_with(json=expected_req)


class TestProbability(unittest.TestCase):

    def setUp(self):
        warnings.simplefilter('error')

    def test_joint_probability(self):
        popmod, mock_endpoint, _ = _popmod_with_mocked_backend(PM, WXYZ_SCHEMA)

        mock_endpoint.logpdf_rows.post.return_value = FakeResponse(
            np.log([.2, .35]))

        results = popmod.joint_probability(
            pd.DataFrame({
                'x': [1, 2],
                'y': [3, 1]
            }), probability_column='pr')

        expected = DataFrame({
            'x': [1, 2],
            'y': [3, 1],
            'pr': [.2, .35]
        }, columns=['x', 'y', 'pr'])
        assert_frame_equal(results, expected)

        expected_req = {'targets': {'x': [1, 2], 'y': [3, 1]}}
        mock_endpoint.logpdf_rows.post.assert_called_once_with(
            json=expected_req)

    def test_joint_probability_with_givens(self):
        popmod, mock_endpoint, _ = _popmod_with_mocked_backend(PM, WXYZ_SCHEMA)

        mock_endpoint.logpdf_rows.post.return_value = FakeResponse(
            np.log([.2, .35]))

        results = popmod.joint_probability(
            pd.DataFrame({
                'x': [1, 2],
                'y': [3, 1]
            }), given={'z': 5}, probability_column='pr')

        expected = DataFrame({
            'x': [1, 2],
            'y': [3, 1],
            'pr': [.2, .35]
        }, columns=['x', 'y', 'pr'])
        assert_frame_equal(results, expected)

        expected_req = {
            'targets': {
                'x': [1, 2],
                'y': [3, 1]
            },
            'given': {
                'z': 5
            }
        }
        mock_endpoint.logpdf_rows.post.assert_called_once_with(
            json=expected_req)


class TestObservedProbability(unittest.TestCase):

    def setUp(self):
        warnings.simplefilter('error')

    def test_row_probability(self):
        popmod, mock_endpoint, mock_pop_endpoint = (
            _popmod_with_mocked_backend(PM, WXYZ_SCHEMA))

        mock_pop_endpoint.select.post.return_value = FakeResponse({
            'columns': {
                'x': [2, 3, 4, 5, 6],
                'y': [9, 8, 7, 6, 5]
            },
            'rowids': [0, 1, 2, 3, 4]
        })
        mock_endpoint.logpdf_observed.post.return_value = FakeResponse(
            np.log([.025, .04, .03, .01, .05]))

        results = popmod.row_probability(['x', 'y'], probability_column='pr')

        expected = DataFrame({
            'x': [2, 3, 4, 5, 6],
            'y': [9, 8, 7, 6, 5],
            'pr': [.025, .04, .03, .01, .05]
        }, columns=['x', 'y', 'pr'], index=[0, 1, 2, 3, 4])
        assert_frame_equal(results, expected)

        mock_pop_endpoint.select.post.assert_called_once_with(
            json={'target': ['x', 'y']})
        # We didn't specify givens so implicitly use all non-target columns
        expected_req = {
            'targets': ['x', 'y'],
            'givens': ['w', 'z'],
            'rowids': 'all'
        }
        mock_endpoint.logpdf_observed.post.assert_called_once_with(
            json=expected_req)

    def test_row_probability_with_givens(self):
        popmod, mock_endpoint, mock_pop_endpoint = (
            _popmod_with_mocked_backend(PM, WXYZ_SCHEMA))

        mock_pop_endpoint.select.post.return_value = FakeResponse({
            'columns': {
                'x': [2, 3, 4, 5, 6],
                'y': [9, 8, 7, 6, 5]
            },
            'rowids': [0, 1, 2, 3, 4]
        })
        mock_endpoint.logpdf_observed.post.return_value = FakeResponse(
            np.log([.025, .04, .03, .01, .05]))

        popmod.row_probability(['x', 'y'], given_columns=['z'])

        expected_req = {
            'targets': ['x', 'y'],
            'givens': ['z'],
            'rowids': 'all'
        }
        mock_endpoint.logpdf_observed.post.assert_called_once_with(
            json=expected_req)

    def test_row_probability_without_target_columns(self):
        popmod, mock_endpoint, _ = _popmod_with_mocked_backend(PM, WXYZ_SCHEMA)

        mock_endpoint.select.post.return_value = FakeResponse({
            'columns': {},
            'rowids': [0, 1, 2, 3, 4]
        })
        mock_endpoint.logpdf_observed.post.return_value = FakeResponse(
            np.log([.025, .04, .03, .01, .05]))

        results = popmod.row_probability(['x', 'y'], given_columns=['z'],
                                         omit_target_columns=True)
        expected = DataFrame({
            'p': [.025, .04, .03, .01, .05]
        }, columns=['p'], index=[0, 1, 2, 3, 4])
        assert_frame_equal(results, expected)

        expected_req = {
            'targets': ['x', 'y'],
            'givens': ['z'],
            'rowids': 'all'
        }
        mock_endpoint.logpdf_observed.post.assert_called_once_with(
            json=expected_req)

    def test_row_probability_with_overlapping_columns(self):
        popmod, mock_endpoint, _ = _popmod_with_mocked_backend(PM, WXYZ_SCHEMA)

        # `y` is in both `targets` and `givens`
        with self.assertRaises(ValueError):
            popmod.row_probability(['x', 'y'], given_columns=['y', 'z'])

    def test_row_probability_with_id_cols(self):
        popmod, mock_endpoint, mock_pop_endpoint = (
            _popmod_with_mocked_backend(PM, XYZ_NAME_SCHEMA))

        mock_pop_endpoint.select.post.side_effect = [
            FakeResponse({
                'columns': {
                    'x': [2, 3, 4, 5, 6],
                    'y': [9, 8, 7, 6, 5]
                },
                'rowids': [0, 1, 2, 3, 4]
            }),
            FakeResponse({
                'columns': {
                    'name': ['a', 'b', 'c', 'd', 'e']
                },
                'rowids': [0, 1, 2, 3, 4]
            })
        ]
        mock_endpoint.logpdf_observed.post.return_value = FakeResponse(
            np.log([.025, .04, .03, .01, .05]))

        results = popmod.row_probability(['x', 'y'], probability_column='pr')

        expected = DataFrame({
            'name': ['a', 'b', 'c', 'd', 'e'],
            'x': [2, 3, 4, 5, 6],
            'y': [9, 8, 7, 6, 5],
            'pr': [.025, .04, .03, .01, .05]
        }, columns=['name', 'x', 'y', 'pr'], index=[0, 1, 2, 3, 4])
        assert_frame_equal(results, expected)

        mock_pop_endpoint.select.post.assert_has_calls([
            call(json={'target': ['x', 'y']}),
            call(json={
                'target': ['name'],
                'rowids': [0, 1, 2, 3, 4]
            })
        ])

        # Make sure we can turn off id columns
        mock_pop_endpoint.reset_mock()
        mock_pop_endpoint.select.post.side_effect = [
            FakeResponse({
                'columns': {
                    'x': [2, 3, 4, 5, 6],
                    'y': [9, 8, 7, 6, 5]
                },
                'rowids': [0, 1, 2, 3, 4]
            })
        ]
        popmod.return_identifying_columns(False)
        popmod.row_probability(['x', 'y'], probability_column='pr')
        mock_pop_endpoint.select.post.assert_called_once_with(
            json={'target': ['x', 'y']})

    def test_row_probability_doesnt_stomp_on_columns(self):
        popmod, mock_endpoint, _ = _popmod_with_mocked_backend(PM, WXYZ_SCHEMA)
        with self.assertRaises(ValueError):
            popmod.row_probability(['x', 'pro'], probability_column='pro')

    def test_element_probability(self):
        popmod, mock_endpoint, mock_pop_endpoint = (
            _popmod_with_mocked_backend(PM, WXYZ_SCHEMA))

        mock_pop_endpoint.select.post.return_value = FakeResponse({
            'columns': {
                'x': [2, 3, 4, 5, 6],
                'y': [9, 8, None, 6, 5]
            },
            'rowids': [0, 1, 2, 3, 4]
        })
        mock_endpoint.logpdf_observed.post.side_effect = [
            FakeResponse(np.log([.025, .04, np.nan, .01, .05])),
            FakeResponse(np.log([.1, .2, .3, .4, .5]))
        ]

        results = popmod.element_probability(['x', 'y'],
                                             probability_suffix='_pr')

        expected = DataFrame({
            'x': [2, 3, 4, 5, 6],
            'x_pr': [.025, .04, None, .01, .05],
            'y': [9, 8, None, 6, 5],
            'y_pr': [.1, .2, .3, .4, .5]
        }, columns=['x', 'x_pr', 'y', 'y_pr'], index=[0, 1, 2, 3, 4])
        assert_frame_equal(results, expected)

        mock_pop_endpoint.select.post.assert_called_once_with(
            json={'target': ['x', 'y']})
        # Make sure there were separate calls for each column
        mock_endpoint.logpdf_observed.post.assert_has_calls([
            call(
                json={
                    'targets': ['x'],
                    'givens': ['w', 'y', 'z'],
                    'rowids': [0, 1, 2, 3, 4]
                }),
            call(
                json={
                    'targets': ['y'],
                    'givens': ['w', 'x', 'z'],
                    'rowids': [0, 1, 2, 3, 4]
                })
        ], any_order=True)

    def test_element_probability_with_givens(self):
        popmod, mock_endpoint, mock_pop_endpoint = (
            _popmod_with_mocked_backend(PM, WXYZ_SCHEMA))

        mock_pop_endpoint.select.post.return_value = FakeResponse({
            'columns': {
                'x': [2, 3, 4, 5, 6],
                'y': [9, 8, None, 6, 5]
            },
            'rowids': [0, 1, 2, 3, 4]
        })
        mock_endpoint.logpdf_observed.post.side_effect = [
            FakeResponse(np.log([.025, .04, np.nan, .01, .05])),
            FakeResponse(np.log([.1, .2, .3, .4, .5]))
        ]

        popmod.element_probability(['x', 'y'], given_columns=['w', 'x', 'z'])

        mock_pop_endpoint.select.post.assert_called_once_with(
            json={'target': ['x', 'y']})
        # Make sure there were separate calls for each column
        mock_endpoint.logpdf_observed.post.assert_has_calls(
            [
                # 'y' is not a given col, so it's not conditioned on
                call(
                    json={
                        'targets': ['x'],
                        'givens': ['w', 'z'],
                        'rowids': [0, 1, 2, 3, 4]
                    }),
                call(
                    json={
                        'targets': ['y'],
                        'givens': ['w', 'x', 'z'],
                        'rowids': [0, 1, 2, 3, 4]
                    })
            ],
            any_order=True)

    def test_element_probability_with_id_cols_and_select(self):
        popmod, mock_endpoint, mock_pop_endpoint = (
            _popmod_with_mocked_backend(PM, XYZ_NAME_SCHEMA))

        # First is the select for the probability, then is the select for the
        # `select` columns.
        mock_pop_endpoint.select.post.side_effect = [
            FakeResponse({
                'columns': {
                    'x': [2, 3, 4, 5, 6],
                    'y': [9, 8, None, 6, 5]
                },
                'rowids': [0, 1, 2, 3, 4]
            }),
            FakeResponse({
                'columns': {
                    'z': [9, 8, 7, 6, 5],
                    'name': ['a', 'b', 'c', 'd', 'e']
                },
                'rowids': [0, 1, 2, 3, 4]
            })
        ]
        mock_endpoint.logpdf_observed.post.side_effect = [
            FakeResponse(np.log([.025, .04, np.nan, .01, .05])),
            FakeResponse(np.log([.1, .2, .3, .4, .5]))
        ]

        results = popmod.element_probability(['x', 'y'], select=['z'],
                                             probability_suffix='_pr')

        expected_data = {
            'name': ['a', 'b', 'c', 'd', 'e'],
            'z': [9, 8, 7, 6, 5],
            'x': [2, 3, 4, 5, 6],
            'x_pr': [.025, .04, None, .01, .05],
            'y': [9, 8, None, 6, 5],
            'y_pr': [.1, .2, .3, .4, .5]
        }
        expected = DataFrame(expected_data,
                             columns=['name', 'z', 'x', 'x_pr', 'y', 'y_pr'],
                             index=[0, 1, 2, 3, 4])  # yapf: disable
        assert_frame_equal(results, expected)

        mock_pop_endpoint.select.post.assert_has_calls([
            call(json={'target': ['x', 'y']}),
            call(json={
                'target': ['name', 'z'],
                'rowids': [0, 1, 2, 3, 4]
            })
        ])
        # Make sure there were separate calls for each column
        mock_endpoint.logpdf_observed.post.assert_has_calls([
            call(json={
                'targets': ['x'],
                'givens': ['y', 'z'],
                'rowids': [0, 1, 2, 3, 4]
            }),
            call(json={
                'targets': ['y'],
                'givens': ['x', 'z'],
                'rowids': [0, 1, 2, 3, 4]
            })
        ], any_order=True)

    def test_element_probability_doesnt_stomp_on_columns(self):
        popmod, mock_endpoint, _ = _popmod_with_mocked_backend(PM, WXYZ_SCHEMA)
        with self.assertRaises(ValueError):
            popmod.element_probability(['x', 'x_mysuffix'],
                                       probability_suffix='_mysuffix')


class TestAddDataColumns(unittest.TestCase):

    def setUp(self):
        warnings.simplefilter('error')

    def test_add_data_columns(self):
        popmod, mock_endpoint, mock_pop_endpoint = (
            _popmod_with_mocked_backend(PM, XYZ_NAME_SCHEMA))

        mock_pop_endpoint.select.post.return_value = FakeResponse({
            'columns': {
                'name': [8, 1],
                'z': [3, 19]
            },
            'rowids': [7, 3]
        })
        df = DataFrame({'foo': [1, 17]}, index=[7, 3])
        expected = DataFrame({
            'foo': [1, 17],
            'name': [8, 1],
            'z': [3, 19]
        }, columns=['name', 'z', 'foo'], index=[7, 3])
        results = popmod.add_data_columns(df, ['z'])
        assert_frame_equal(results, expected)

        mock_pop_endpoint.select.post.assert_called_once_with(
            json={
                'target': ['name', 'z'],
                'rowids': [7, 3]
            })


class TestInfer(unittest.TestCase):

    def setUp(self):
        warnings.simplefilter('error')

    def test_infer(self):
        schema = PopulationSchema.from_json({
            'identifying_columns': ['x', 'z'],
            'columns': [{
                'name': 'x',
                'stat_type': 'realAdditive'
            }, {
                'name': 'y',
                'stat_type': 'realAdditive'
            }, {
                'name': 'z',
                'stat_type': 'realAdditive'
            }]
        })
        popmod, mock_endpoint, mock_pop_endpoint = (
            _popmod_with_mocked_backend(PM, schema))

        mock_pop_endpoint.select.post.return_value = FakeResponse({
            'columns': {
                'z': [5, 4, 3, 2, 1]
            },
            'rowids': [0, 1, 2, 3, 4]
        })
        mock_endpoint.infer_observed.post.return_value = FakeResponse({
            'columns': {
                'x': [0, 6, None, 4, None],
                'y': [None, 7, None, 5, 7]
            },
            'uncertainty': {
                'x': [.3, .3, None, .4, None],
                'y': [None, .1, None, .9, .2]
            },
            'rowids': [0, 1, 2, 3, 4]
        })

        results = popmod.infer(['x', 'y'])
        expected = DataFrame({
            'z': [5, 4, 3, 2, 1],
            'x': [0, 6, None, 4, None],
            'x_conf': [.3, .3, None, .4, None],
            'y': [None, 7, None, 5, 7],
            'y_conf': [None, .1, None, .9, .2]
        }, columns=['z', 'x', 'x_conf', 'y', 'y_conf'], index=[0, 1, 2, 3, 4])
        assert_frame_equal(results, expected)
        mock_pop_endpoint.select.post.assert_called_with(
            json={
                'target': ['z'],
                'rowids': [0, 1, 2, 3, 4]
            })
        mock_endpoint.infer_observed.post.assert_called_with(
            json={
                'target': ['x', 'y'],
                'rowids': 'all',
                'infer_present': False
            })

    def test_infer_doesnt_stomp_on_columns(self):
        popmod, mock_endpoint, _ = _popmod_with_mocked_backend(PM, WXYZ_SCHEMA)
        mock_endpoint.select.post.return_value = FakeResponse({
            'columns': {
                'z': [5, 4, 3, 2, 1]
            },
            'rowids': [0, 1, 2, 3, 4]
        })
        with self.assertRaises(ValueError):
            popmod.infer(['x', 'x_mysuffix'], confidence_suffix='_mysuffix')


class TestSimulate(unittest.TestCase):

    def setUp(self):
        warnings.simplefilter('error')

    def test_implicit_targets(self):
        schema = PopulationSchema.from_json({
            'columns': [{
                'name': 'x',
                'stat_type': 'realAdditive'
            }]
        })
        popmod, mock_endpoint, _ = _popmod_with_mocked_backend(PM, schema)

        mock_endpoint.simulate.post.return_value = FakeResponse([{
            'columns': {
                'x': [4, 7]
            }
        }])

        expected = DataFrame({
            'x': [4, 7],
            'sim': [0, 1],
            'given_row': [0, 0]
        }).set_index(['sim', 'given_row'])
        assert_frame_equal(popmod.simulate(n=2), expected)

        mock_endpoint.simulate.post.assert_called_once_with(
            json={
                'target': ['x'],
                'n': 2,
                'given': {},
            })

    def test_target(self):
        popmod, mock_endpoint, _ = _popmod_with_mocked_backend(PM, WXYZ_SCHEMA)

        mock_endpoint.simulate.post.return_value = FakeResponse([{
            'columns': {
                'z': [4, 7]
            }
        }])

        expected = DataFrame({
            'z': [4, 7],
            'sim': [0, 1],
            'given_row': [0, 0]
        }).set_index(['sim', 'given_row'])
        assert_frame_equal(popmod.simulate(targets=['z'], n=2), expected)

        mock_endpoint.simulate.post.assert_called_once_with(
            json={
                'target': ['z'],
                'given': {},
                'n': 2
            })

    def test_simulate_date_given_date(self):
        schema = PopulationSchema.from_json({
            'columns': [
                {
                    'name': 'a',
                    'stat_type': 'date'
                },
                {
                    'name': 'b',
                    'stat_type': 'date'
                },
            ]
        })
        popmod, mock_endpoint, _ = _popmod_with_mocked_backend(PM, schema)

        epoch = datetime(1970, 1, 1)
        sim_value = datetime(1992, 7, 3)
        given_value = datetime(1971, 1, 2)

        # Set up a mock response.
        sim_days = (sim_value - epoch).days
        mock_resp = {'columns': {'a': [sim_days]}}
        mock_endpoint.simulate.post.return_value = FakeResponse([mock_resp])

        # Check that `simulate` parses the mock response as we expect.
        expected = DataFrame({
            'a': pd.to_datetime([sim_value]),
            'sim': [0],
            'given_row': [0]
        }).set_index(['sim', 'given_row'])
        sample = popmod.simulate(targets=['a'], given={'b': given_value}, n=1)
        assert_frame_equal(sample, expected)

        # Check that the call `simulate` made matches what we expect.
        given_days = (given_value - epoch).days
        expected_req = {'target': ['a'], 'given': {'b': [given_days]}, 'n': 1}
        mock_endpoint.simulate.post.assert_called_once_with(json=expected_req)


class TestPlotting(unittest.TestCase):

    def setUp(self):
        warnings.simplefilter('error')
        warnings.filterwarnings('ignore', message='numpy.dtype size changed')
        matplotlib.pyplot.switch_backend('Agg')

    def test_mutual_information(self):
        popmod, mock_endpoint, _ = _popmod_with_mocked_backend(PM, WXYZ_SCHEMA)

        mock_endpoint.relation.post.return_value = FakeResponse({
            'target': ['x', 'y'],
            'elements': [1, .75, .6, 1]
        })

        # Smoke test to make sure that this plot at least runs
        edpanalyst.heatmap(popmod.mutual_information(['x', 'y'], ['x', 'y']))


class FakeResponse(object):
    """A testing class that mimics a requests.Response."""

    def __init__(self, json, status_code=200):
        self._json = json
        self.status_code = status_code

    def json(self):
        self.raise_for_status()
        return self._json

    def raise_for_status(self):
        if self.status_code != 200:
            raise ValueError('Is this right?')


if __name__ == '__main__':
    unittest.main()
