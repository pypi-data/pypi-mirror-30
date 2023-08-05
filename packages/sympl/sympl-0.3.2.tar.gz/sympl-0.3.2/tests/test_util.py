import unittest

import numpy as np
import pytest
from sympl import (
    Prognostic, ensure_no_shared_keys, SharedKeyError, DataArray,
    combine_dimensions, set_direction_names, Implicit, Diagnostic,
    TendencyInDiagnosticsWrapper)
from sympl._core.util import (
    update_dict_by_adding_another, get_component_aliases)


def same_list(list1, list2):
    return (len(list1) == len(list2) and all(
        [item in list2 for item in list1] + [item in list1 for item in list2]))


class MockPrognostic(Prognostic):

    def __init__(self):
        self._num_updates = 0

    def __call__(self, state):
        self._num_updates += 1
        return {}, {'num_updates': self._num_updates}


class MockImplicit(Implicit):

    def __init__(self):
        self._a = 1

    def __call__(self, state):
        return self._a


class MockDiagnostic(Diagnostic):

    def __init__(self):
        self._a = 1

    def __call__(self, state):
        return self._a


def test_update_dict_by_adding_another_adds_shared_arrays():
    old_a = np.array([1., 1.])
    dict1 = {'a': old_a}
    dict2 = {'a': np.array([2., 3.]), 'b': np.array([0., 1.])}
    update_dict_by_adding_another(dict1, dict2)
    assert 'b' in dict1.keys()
    assert dict1['a'] is old_a
    assert np.all(dict1['a'] == np.array([3., 4.]))
    assert np.all(dict2['a'] == np.array([2., 3.]))
    assert np.all(dict2['b'] == np.array([0., 1.]))
    assert len(dict1.keys()) == 2
    assert len(dict2.keys()) == 2


def test_update_dict_by_adding_another_adds_shared_arrays_reversed():
    old_a = np.array([1., 1.])
    dict1 = {'a': np.array([2., 3.])}
    dict2 = {'a': old_a, 'b': np.array([0., 1.])}
    update_dict_by_adding_another(dict2, dict1)
    assert 'b' not in dict1.keys()
    assert dict2['a'] is old_a
    assert np.all(dict2['a'] == np.array([3., 4.]))
    assert np.all(dict1['a'] == np.array([2., 3.]))
    assert np.all(dict2['b'] == np.array([0., 1.]))
    assert len(dict1.keys()) == 1
    assert len(dict2.keys()) == 2


class DummyPrognostic(Prognostic):
    input_properties = {'temperature': {'alias': 'T'}}
    diagnostic_properties = {'pressure': {'alias': 'P'}}
    tendency_properties = {'temperature': {}}

    def __init__(self):
        self._a = 1

    def __call__(self, state):
        return self._a


def test_get_component_aliases_with_no_args():
    aliases = get_component_aliases()
    assert type(aliases) == dict
    assert len(aliases.keys()) == 0


def test_get_component_aliases_with_single_component_arg():
    components = [MockPrognostic(), MockImplicit(), MockDiagnostic(),
                  TendencyInDiagnosticsWrapper(DummyPrognostic(), 'dummy')]
    for c, comp in enumerate(components):
        aliases = get_component_aliases(comp)
        assert type(aliases) == dict
        if c == 3:
            assert len(aliases.keys()) == 2
            for k in ['T', 'P']:
                assert k in list(aliases.values())
        else:
            assert len(aliases.keys()) == 0


def test_get_component_aliases_with_two_component_args():
    components = [MockDiagnostic(), MockImplicit(), MockDiagnostic(),
                  TendencyInDiagnosticsWrapper(DummyPrognostic(), 'dummy')]
    for comp in components[:3]:
        aliases = get_component_aliases(comp, components[-1])
        assert type(aliases) == dict
        assert len(aliases.keys()) == 2
        for k in ['T', 'P']:
            assert k in list(aliases.values())


class DummyProg1(Prognostic):
    input_properties = {'temperature': {'alias': 'T'}}
    tendency_properties = {'temperature': {'alias': 'TEMP'}}

    def __init__(self):
        self._a = 1

    def __call__(self, state):
        return self._a


class DummyProg2(Prognostic):
    input_properties = {'temperature': {'alias': 't'}}

    def __init__(self):
        self._a = 1

    def __call__(self, state):
        return self._a


class DummyProg3(Prognostic):
    input_properties = {'temperature': {}}
    diagnostic_properties = {'pressure': {}}
    tendency_properties = {'temperature': {}}

    def __init__(self):
        self._a = 1

    def __call__(self, state):
        return self._a


def test_get_component_aliases_with_different_values():
    # two different aliases in the same Component:
    aliases = get_component_aliases(DummyProg1())
    assert len(aliases.keys()) == 1
    assert aliases['temperature'] == 'TEMP'
    # two different aliases in different Components:
    aliases = get_component_aliases(DummyProg1(), DummyProg2())
    assert len(aliases.keys()) == 1
    assert aliases['temperature'] == 't'
    # NO aliases in component
    aliases = get_component_aliases(DummyProg3)
    assert len(aliases.keys()) == 0


def test_ensure_no_shared_keys_empty_dicts():
    ensure_no_shared_keys({}, {})


def test_ensure_no_shared_keys_one_empty_dict():
    ensure_no_shared_keys({'a': 1, 'b': 2}, {})
    ensure_no_shared_keys({}, {'a': 1, 'b': 2})


def test_ensure_no_shared_keys_with_no_shared_keys():
    ensure_no_shared_keys({'a': 1, 'b': 2}, {'c': 2, 'd': 1})
    ensure_no_shared_keys({'c': 2, 'd': 1}, {'a': 1, 'b': 2})


def test_ensure_no_shared_keys_with_shared_keys():
    try:
        ensure_no_shared_keys({'a': 1, 'b': 2}, {'e': 2, 'a': 1})
    except SharedKeyError:
        pass
    except Exception as err:
        raise err
    else:
        raise AssertionError(
            'No exception raised but expected SharedKeyError.')


class CombineDimensionsTests(unittest.TestCase):

    def setUp(self):
        self.array_1d = DataArray(np.zeros((2,)), dims=['lon'])
        self.array_2d = DataArray(np.zeros((2, 2)), dims=['lat', 'lon'])
        self.array_3d = DataArray(np.zeros((2, 2, 2)),
                                  dims=['lon', 'lat', 'interface_levels'])
        set_direction_names(
            x=['lon'], y=['lat'], z=['mid_levels', 'interface_levels'])

    def tearDown(self):
        set_direction_names(x=[], y=[], z=[])

    def test_combine_dimensions_2d_and_3d(self):
        dims = combine_dimensions(
            [self.array_2d, self.array_3d], out_dims=('x', 'y', 'z'))
        assert same_list(dims, ['lon', 'lat', 'interface_levels'])

    def test_combine_dimensions_2d_and_3d_z_y_x(self):
        dims = combine_dimensions(
            [self.array_2d, self.array_3d], out_dims=('z', 'y', 'x'))
        assert same_list(dims, ['interface_levels', 'lat', 'lon'])

    def combine_dimensions_1d_shared(self):
        dims = combine_dimensions(
            [self.array_1d, self.array_1d], out_dims=['x'])
        assert same_list(dims, ['lon'])

    def combine_dimensions_1d_not_shared(self):
        array_1d_x = DataArray(np.zeros((2,)), dims=['lon'])
        array_1d_y = DataArray(np.zeros((2,)), dims=['lat'])
        dims = combine_dimensions([array_1d_x, array_1d_y], out_dims=['x', 'y'])
        assert same_list(dims, ['lon', 'lat'])

    def combine_dimensions_1d_wrong_direction(self):
        try:
            combine_dimensions(
                [self.array_1d, self.array_1d], out_dims=['z'])
        except ValueError:
            pass
        except Exception as err:
            raise err
        else:
            raise AssertionError('No exception raised but expected ValueError.')

    def combine_dimensions_1d_and_2d_extra_direction(self):
        try:
            combine_dimensions(
                [self.array_1d, self.array_2d], out_dims=['y'])
        except ValueError:
            pass
        except Exception as err:
            raise err
        else:
            raise AssertionError('No exception raised but expected ValueError.')


if __name__ == '__main__':
    pytest.main([__file__])
