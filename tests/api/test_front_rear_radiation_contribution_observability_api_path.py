from __future__ import annotations

import numpy as np

from os_lem.api import run_simulation
from os_lem.assemble import assemble_system
from os_lem.parser import normalize_model
from os_lem.reference_back_loaded_horn import build_back_loaded_horn_model_dict
from os_lem.solve import (
    front_radiation_contribution_spl,
    rear_radiation_contribution_spl,
    solve_frequency_sweep,
)


NO_FRONTEND_CONTRACT_CHANGE = True


def _model_dict() -> dict[str, object]:
    model_dict = build_back_loaded_horn_model_dict()
    model_dict["observations"] = list(model_dict["observations"])
    model_dict["observations"].extend(
        [
            {"id": "spl_front", "type": "spl", "target": "front_rad", "distance": "1 m", "radiation_space": "2pi"},
            {"id": "spl_rear", "type": "spl", "target": "mouth_rad", "distance": "1 m", "radiation_space": "2pi"},
        ]
    )
    return model_dict


def test_run_simulation_supports_explicit_front_and_rear_radiation_contribution_path() -> None:
    model_dict = _model_dict()
    frequencies = np.array([80.0, 160.0, 320.0])

    result = run_simulation(model_dict, frequencies)
    model, warnings = normalize_model(model_dict)
    assert warnings == []
    assert NO_FRONTEND_CONTRACT_CHANGE is True

    system = assemble_system(model)
    sweep = solve_frequency_sweep(model, system, frequencies)
    assert len(system.front_rear_radiation_contribution_observabilities) == 1
    observability = system.front_rear_radiation_contribution_observabilities[0]

    expected_front = front_radiation_contribution_spl(
        sweep,
        system,
        observability,
        1.0,
        radiation_space="2pi",
    )
    expected_rear = rear_radiation_contribution_spl(
        sweep,
        system,
        observability,
        1.0,
        radiation_space="2pi",
    )

    np.testing.assert_allclose(result.series["spl_front"], expected_front, rtol=1e-10, atol=1e-12)
    np.testing.assert_allclose(result.series["spl_rear"], expected_rear, rtol=1e-10, atol=1e-12)
    assert result.units["spl_front"] == "dB"
    assert result.units["spl_rear"] == "dB"
    assert np.all(np.isfinite(result.series["spl_front"]))
    assert np.all(np.isfinite(result.series["spl_rear"]))
    assert not np.allclose(result.series["spl_front"], result.series["spl_rear"])
