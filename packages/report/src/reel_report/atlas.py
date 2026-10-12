"""Destrieux atlas on fsaverage5, in TRIBE v2's vertex order (left hemisphere first)."""

from __future__ import annotations

import warnings
from collections.abc import Iterable
from dataclasses import dataclass
from functools import lru_cache

import numpy as np

N_VERTICES_PER_HEMI = 10242
EXCLUDED_LABELS = ("Unknown", "Medial_wall")


@dataclass(frozen=True)
class Atlas:
    labels: np.ndarray  # (2 * N_VERTICES_PER_HEMI,) label index per vertex
    names: tuple[str, ...]

    def mask(self, regions: Iterable[str]) -> np.ndarray:
        regions = list(regions)
        missing = sorted(set(regions) - set(self.names))
        if missing:
            raise KeyError(f"Regions not in Destrieux atlas: {missing}")
        return np.isin(self.labels, [self.names.index(r) for r in regions])

    @property
    def cortex_mask(self) -> np.ndarray:
        excluded = [self.names.index(n) for n in EXCLUDED_LABELS if n in self.names]
        return ~np.isin(self.labels, excluded)


@lru_cache(maxsize=1)
def load_destrieux() -> Atlas:
    """Downloads once via nilearn (cached in ~/nilearn_data), then loads from disk."""
    from nilearn import datasets

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")  # nilearn warns that "Unknown" has no vertices
        atlas = datasets.fetch_atlas_surf_destrieux(verbose=0)
    names = tuple(n.decode() if isinstance(n, bytes) else str(n) for n in atlas.labels)
    labels = np.concatenate([atlas.map_left, atlas.map_right]).astype(np.int32)
    return Atlas(labels=labels, names=names)
