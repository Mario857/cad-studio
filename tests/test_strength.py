import numpy as np
import trimesh

from cadstudio.strength import worst_section


def test_cantilever_matches_beam_theory():
    length, b, h, force = 100.0, 10.0, 5.0, 10.0
    mesh = trimesh.creation.box(extents=(length, b, h))
    mesh.apply_translation((length / 2, 0, 0))  # root at x=0, tip at x=L
    peak, axis, _ = worst_section(mesh, np.array([length, 0.0, 0.0]), force, np.array([0.0, 0.0, -1.0]))
    expected = 6 * force * length / (b * h ** 2)
    assert abs(peak - expected) / expected < 0.25, (peak, expected)
    assert abs(axis[0]) > 0.99
