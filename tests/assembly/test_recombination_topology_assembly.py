from __future__ import annotations

from os_lem.assemble import assemble_system
from os_lem.model import Driver, NormalizedModel, RadiatorElement, Waveguide1DElement


def _driver() -> Driver:
    return Driver(
        id="drv1",
        Re=6.0,
        Le=0.0,
        Bl=7.0,
        Mms=0.02,
        Cms=1.0e-3,
        Rms=1.0,
        Sd=0.013,
        node_front="front",
        node_rear="rear",
        source_voltage_rms=2.83,
    )


def test_assemble_system_collects_recombination_topology_with_shared_exit() -> None:
    model = NormalizedModel(
        driver=_driver(),
        waveguides=[
            Waveguide1DElement(
                id="path_main",
                node_a="rear",
                node_b="merge",
                length_m=0.48,
                area_start_m2=0.0090,
                area_end_m2=0.0085,
                profile="conical",
                segments=6,
            ),
            Waveguide1DElement(
                id="path_tap",
                node_a="rear",
                node_b="merge",
                length_m=0.29,
                area_start_m2=0.0045,
                area_end_m2=0.0040,
                profile="conical",
                segments=4,
            ),
            Waveguide1DElement(
                id="shared_exit",
                node_a="merge",
                node_b="mouth",
                length_m=0.34,
                area_start_m2=0.0125,
                area_end_m2=0.0150,
                profile="conical",
                segments=5,
            ),
        ],
        radiators=[RadiatorElement(id="mouth_rad", node="mouth", model="flanged_piston", area_m2=0.0150)],
        node_order=["front", "rear", "merge", "mouth"],
    )

    assembled = assemble_system(model)

    assert len(assembled.parallel_branch_bundles) == 1
    assert len(assembled.acoustic_junctions) == 1
    assert len(assembled.recombination_topologies) == 1

    topology = assembled.recombination_topologies[0]
    assert topology.split_node_name == "rear"
    assert topology.merge_node_name == "merge"
    assert topology.upstream_bundle_element_ids == ("path_main", "path_tap")
    assert topology.upstream_bundle_element_kinds == ("waveguide_1d", "waveguide_1d")
    assert topology.shared_exit_element_id == "shared_exit"
    assert topology.shared_exit_element_kind == "waveguide_1d"
    assert topology.mouth_node_name == "mouth"
    assert topology.mouth_radiator_id == "mouth_rad"
