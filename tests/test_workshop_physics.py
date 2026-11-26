"""Independent checks for the tuning-workshop acoustic extensions."""
from pathlib import Path
from copy import deepcopy
import numpy as np
import pytest
import yaml
from os_lem.api import run_simulation
from os_lem.parser import normalize_model
from os_lem.elements.waveguide_1d import uniform_segment_admittance, propagation_and_impedance
from os_lem.model import Waveguide1DElement
from os_lem.solve import _waveguide_equivalent_admittance_matrix, _waveguide_full_admittance_matrix
from os_lem.constants import RHO0, C0


def model():
    m=yaml.safe_load((Path(__file__).parents[1]/'examples/frontend_contract_v1/conical_line_minimal.yaml').read_text())
    m['observations']=[o for o in m['observations'] if o['type']!='line_profile']
    return m


@pytest.mark.parametrize('sigma',[0,500,10000])
def test_uniform_porous_line_matches_analytic_two_port(sigma):
    line=Waveguide1DElement('line','a','b',1.6,.0132,.0132,'conical',flow_resistivity=sigma,segments=64,loss=.03)
    for f in [10,50,210,1000]:
        actual=_waveguide_equivalent_admittance_matrix(2*np.pi*f,line)
        expected=uniform_segment_admittance(2*np.pi*f,1.6,.0132,.03,sigma)
        np.testing.assert_allclose(actual,expected,rtol=2e-9,atol=1e-14)


def test_banded_reduction_matches_dense_for_taper():
    line=Waveguide1DElement('line','a','b',2,.01,.025,'conical',flow_resistivity=500,segments=64,loss=.1)
    for f in [10,73,500,1000]:
        full=_waveguide_full_admittance_matrix(2*np.pi*f,line)
        ends=[0,64];inside=list(range(1,64))
        expected=full[np.ix_(ends,ends)]-full[np.ix_(ends,inside)]@np.linalg.solve(full[np.ix_(inside,inside)],full[np.ix_(inside,ends)])
        np.testing.assert_allclose(_waveguide_equivalent_admittance_matrix(2*np.pi*f,line),expected,rtol=1e-9,atol=1e-14)


def test_miki_si_reference_and_passivity():
    # At f/sigma=1, Miki Eqs 30–34 reduce to these constants.
    w=2*np.pi*1000
    gamma,zc=propagation_and_impedance(w,.01,0,1000)
    np.testing.assert_allclose(zc/(RHO0*C0/.01),1.070-.107j)
    np.testing.assert_allclose(gamma/(w/C0),.160+1.109j)
    for f in np.geomspace(10,10000,30):
        y=uniform_segment_admittance(2*np.pi*f,.3,.01,0,10000)
        assert min(np.linalg.eigvalsh((y+y.conj().T)/2))>=-1e-12


def test_series_resistance_adds_without_changing_driver_ts():
    m=model();f=np.geomspace(10,1000,50)
    base=run_simulation(m,f);m['driver']['series_resistance_ohm']=2
    with_r=run_simulation(m,f)
    assert base.model.driver.Bl==with_r.model.driver.Bl
    np.testing.assert_allclose(with_r.zin_complex_ohm-base.zin_complex_ohm,2,atol=1e-12)
    assert np.max(abs(with_r.sweep.cone_velocity))<np.max(abs(base.sweep.cone_velocity))


def test_group_delay_acoustic_spl_not_db_angle_and_distance():
    m=model();m['observations']=[{'id':'near','type':'spl','target':'mouth_rad','distance':'1 m'}, {'id':'far','type':'spl','target':'mouth_rad','distance':'2 m'}, {'id':'gd1','type':'group_delay','target':'near'},{'id':'gd2','type':'group_delay','target':'far'}]
    r=run_simulation(m,np.geomspace(20,1000,600))
    assert np.max(abs(r.series['gd1']))>1e-4
    # Kernel far-field contract compensates flight time: distance scales magnitude only.
    np.testing.assert_allclose(r.series['gd2'],r.series['gd1'],atol=1e-11)
    np.testing.assert_allclose(r.series['far']-r.series['near'],-20*np.log10(2),atol=1e-10)


def test_zero_resistivity_legacy_and_invalid_material():
    m=model();f=np.geomspace(20,1000,50);base=run_simulation(m,f)
    line=next(e for e in m['elements'] if e['type']=='waveguide_1d');line['flow_resistivity']=0
    np.testing.assert_array_equal(run_simulation(m,f).series['mouth_spl'],base.series['mouth_spl'])
    for bad in [-1,float('inf'),float('nan')]:
        line['flow_resistivity']=bad
        with pytest.raises(Exception):normalize_model(m)
    line['flow_resistivity']=10000
    filled=run_simulation(m,f)
    assert any('extrapolation' in warning for warning in filled.warnings)
    assert not np.allclose(filled.series['mouth_spl'],base.series['mouth_spl'])
