"""Internal equivalence for a fixed graph fixture; no external parity claim."""
from copy import deepcopy
import json

import numpy as np
import pytest

from os_lem.acoustic_graph_ir import compile_acoustic_graph_ir_to_model_dict, validate_acoustic_graph_ir
from os_lem.api import run_simulation
from test_poc3_graph_defined_solver_equivalence_smoke import (
    REPO_ROOT, _load_poc3_authority_model, _load_reference_frequency_grid,
)


def _graph():
    return json.loads((REPO_ROOT / 'proof/poc3_blh_benchmark_pass1/graph_explicit.json').read_text())


def _compile(graph):
    result = compile_acoustic_graph_ir_to_model_dict(graph)
    assert result.is_success, result.errors
    return result.model_dict


def test_full_reference_grid_internal_equivalence():
    graph = _graph()
    assert validate_acoustic_graph_ir(graph).warnings == []
    actual_model = _compile(graph)
    reference_model = _load_poc3_authority_model()
    assert len(actual_model['elements']) == len(reference_model['elements'])
    assert not any(e['type'] == 'acoustic_chamber' for e in actual_model['elements'])
    assert [e['segments'] for e in actual_model['elements'] if e['type']=='waveguide_1d'] == [4,36,12]
    # Compare native diagnostic outputs without modifying the compiled model.
    frequency = _load_reference_frequency_grid()
    actual = run_simulation(actual_model, frequency)
    expected = run_simulation(reference_model, frequency)
    np.testing.assert_array_equal(actual.frequencies_hz, expected.frequencies_hz)
    np.testing.assert_allclose(actual.zin_complex_ohm, expected.zin_complex_ohm, rtol=1e-9, atol=1e-10)
    for actual_key, expected_key in [('spl_mouth', 'spl_mouth'), ('spl_total_diagnostic', 'spl_total')]:
        np.testing.assert_allclose(actual.series[actual_key], expected.series[expected_key], rtol=0, atol=1e-8)
    # Identical observation requests also verify excursion and front SPL.
    actual_model['observations'] = deepcopy(reference_model['observations'])
    observed = run_simulation(actual_model, frequency)
    for key in expected.series:
        np.testing.assert_allclose(observed.series[key], expected.series[key], rtol=1e-9, atol=1e-10)


def test_explicit_mass_units_and_voltage_scaling():
    graph = _graph()
    baseline = _compile(graph)
    p = graph['elements'][0]['parameters']
    p['Mms_g'] = p.pop('Mms_kg') * 1000
    p['source_voltage_rms'] *= 2
    changed = _compile(graph)
    assert changed['driver']['Mms'] == pytest.approx(baseline['driver']['Mms'])
    frequency = np.geomspace(20, 1000, 25)
    first = run_simulation(baseline, frequency)
    second = run_simulation(changed, frequency)
    np.testing.assert_allclose(first.zin_complex_ohm, second.zin_complex_ohm, rtol=1e-12, atol=1e-12)
    np.testing.assert_allclose(second.series['spl_mouth']-first.series['spl_mouth'], 20*np.log10(2), rtol=0, atol=1e-10)


@pytest.mark.parametrize('field,value', [('Mms_kg',0),('Mms_kg',float('nan')),('source_voltage_rms',-1),('Mmd_kg',0.001)])
def test_invalid_explicit_driver_is_rejected(field,value):
    graph = _graph()
    graph['elements'][0]['parameters'][field] = value
    assert not compile_acoustic_graph_ir_to_model_dict(graph).is_success


def test_unknown_radiator_model_is_rejected():
    graph = _graph()
    next(e for e in graph['elements'] if e['type']=='radiation_load')['model'] = 'unknown'
    assert not compile_acoustic_graph_ir_to_model_dict(graph).is_success
