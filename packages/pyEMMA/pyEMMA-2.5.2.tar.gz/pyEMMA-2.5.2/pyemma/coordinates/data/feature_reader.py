# This file is part of PyEMMA.
#
# Copyright (c) 2015, 2014 Computational Molecular Biology Group, Freie Universitaet Berlin (GER)
#
# PyEMMA is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from __future__ import absolute_import

import mdtraj
import numpy as np

from pyemma._base.serialization.serialization import SerializableMixIn
from pyemma.coordinates.data._base.datasource import DataSourceIterator, DataSource
from pyemma.coordinates.data._base.random_accessible import RandomAccessStrategy
from pyemma.coordinates.data.featurization.featurizer import MDFeaturizer
from pyemma.coordinates.data.util.traj_info_cache import TrajInfo
from pyemma.coordinates.util import patches
from pyemma.util.annotators import deprecated, fix_docs

__author__ = 'noe, marscher'
__all__ = ['FeatureReader']


@fix_docs
class FeatureReader(DataSource, SerializableMixIn):
    """
    Reads features from MD data.

    To select a feature, access the :attr:`featurizer` and call a feature
    selecting method (e.g) distances.

    Parameters
    ----------
    trajectories: list of strings
        paths to trajectory files

    topologyfile: string
        path to topology file (e.g. pdb)

    chunksize: int
        how many frames to process in one batch.

    featurizer: MDFeaturizer
        a preconstructed featurizer

    Examples
    --------
    >>> from pyemma.datasets import get_bpti_test_data
    >>> from pyemma.util.contexts import settings

    Iterator access:

    >>> reader = FeatureReader(get_bpti_test_data()['trajs'], get_bpti_test_data()['top'])

    Optionally set a chunksize

    >>> reader.chunksize = 300

    Store chunks by their trajectory index

    >>> chunks = {i : [] for i in range(reader.number_of_trajectories())}
    >>> for itraj, X in reader:
    ...     chunks[itraj].append(X)


    Calculate some distances of protein during feature reading:

    >>> reader.featurizer.add_distances([[0, 3], [10, 15]])
    >>> with settings(show_progress_bars=False):
    ...    X = reader.get_output()

    """
    SUPPORTED_RANDOM_ACCESS_FORMATS = (".h5", ".dcd", ".binpos", ".nc", ".xtc", ".trr")
    __serialize_version = 0

    def __init__(self, trajectories, topologyfile=None, chunksize=1000, featurizer=None):
        assert (topologyfile is not None) or (featurizer is not None), \
            "Needs either a topology file or a featurizer for instantiation"

        super(FeatureReader, self).__init__(chunksize=chunksize)
        self._is_reader = True
        self.topfile = topologyfile
        self.filenames = trajectories
        self._return_traj_obj = False

        self._is_random_accessible = all(
            (f.endswith(FeatureReader.SUPPORTED_RANDOM_ACCESS_FORMATS)
             for f in self.filenames)
        )
        # check we have at least mdtraj-1.6.1 to efficiently seek xtc, trr formats
        if any(f.endswith('.xtc') or f.endswith('.trr') for f in trajectories):
            from distutils.version import LooseVersion
            xtc_trr_random_accessible = True if LooseVersion(mdtraj.version.version) >= LooseVersion('1.6.1') else False
            self._is_random_accessible &= xtc_trr_random_accessible

        self._ra_cuboid = FeatureReaderCuboidRandomAccessStrategy(self, 3)
        self._ra_jagged = FeatureReaderJaggedRandomAccessStrategy(self, 3)
        self._ra_linear_strategy = FeatureReaderLinearRandomAccessStrategy(self, 2)
        self._ra_linear_itraj_strategy = FeatureReaderLinearItrajRandomAccessStrategy(self, 3)

        # featurizer
        if topologyfile and featurizer:
            self.logger.warning("Both a topology file and a featurizer were given as arguments. "
                                 "Only featurizer gets respected in this case.")
        if not featurizer:
            self.featurizer = MDFeaturizer(topologyfile)
        else:
            self.featurizer = featurizer
            self.topfile = featurizer.topologyfile

        # Check that the topology and the files in the filelist can actually work together
        self._assert_toptraj_consistency()

    @property
    @deprecated('Please use "filenames" property.')
    def trajfiles(self):
        return self.filenames

    def _get_traj_info(self, filename):
        with mdtraj.open(filename, mode='r') as fh:
            length = len(fh)
            frame = fh.read(1)[0]
            ndim = np.shape(frame)[1]
            offsets = fh.offsets if hasattr(fh, 'offsets') else []

        return TrajInfo(ndim, length, offsets)

    def _create_iterator(self, skip=0, chunk=0, stride=1, return_trajindex=True, cols=None):
        return FeatureReaderIterator(self, skip=skip, chunk=chunk, stride=stride,
                                     return_trajindex=return_trajindex, cols=cols)

    def describe(self):
        """
        Returns a description of this transformer

        :return:
        """
        return ["Feature reader with following features"] + self.featurizer.describe()

    def dimension(self):
        """
        Returns the number of output dimensions

        :return:
        """
        if len(self.featurizer.active_features) == 0:
            # special case: Cartesian coordinates
            return self.featurizer.topology.n_atoms * 3
        else:
            # general case
            return self.featurizer.dimension()

    def _assert_toptraj_consistency(self):
        r""" Check if the topology and the filenames of the reader have the same n_atoms"""
        top = self.featurizer.topology
        traj = mdtraj.load_frame(self.filenames[0], index=0, top=top)
        desired_n_atoms = top.n_atoms
        assert traj.xyz.shape[1] == desired_n_atoms, "Mismatch in the number of atoms between the topology" \
                                                     " and the first trajectory file, %u vs %u" % \
                                                     (desired_n_atoms, traj.xyz.shape[1])

    def __reduce__(self):
        # serialize only the constructor arguments.
        return FeatureReader, (self.filenames, None, self.chunksize, self.featurizer)


class FeatureReaderCuboidRandomAccessStrategy(RandomAccessStrategy):
    def _handle_slice(self, idx):
        idx = np.index_exp[idx]
        itrajs, frames, dims = None, None, None
        if isinstance(idx, (list, tuple)):
            if len(idx) == 1:
                itrajs, frames, dims = idx[0], slice(None, None, None), slice(None, None, None)
            if len(idx) == 2:
                itrajs, frames, dims = idx[0], idx[1], slice(None, None, None)
            if len(idx) == 3:
                itrajs, frames, dims = idx[0], idx[1], idx[2]
            if len(idx) > 3 or len(idx) == 0:
                raise IndexError("invalid slice by %s" % idx)
        return self._get_itraj_random_accessible(itrajs, frames, dims)

    def _get_itraj_random_accessible(self, itrajs, frames, dims):
        itrajs = self._get_indices(itrajs, self._source.ntraj)
        frames = self._get_indices(frames, min(self._source.trajectory_lengths(1, 0)[itrajs]))
        dims = self._get_indices(dims, self._source.ndim)

        ntrajs = len(itrajs)
        nframes = len(frames)
        ndims = len(dims)

        frames_orig = frames.argsort().argsort()
        frames_sorted = np.sort(frames)

        itraj_orig = itrajs.argsort().argsort()
        itraj_sorted = np.sort(itrajs)
        itrajs_unique, itrajs_count = np.unique(itraj_sorted, return_counts=True)

        if max(dims) > self._source.ndim:
            raise IndexError("Data only has %s dimensions, wanted to slice by dimension %s."
                             % (self._source.ndim, max(dims)))

        ra_indices = np.empty((len(itrajs_unique) * nframes, 2), dtype=int)
        for idx, itraj in enumerate(itrajs_unique):
            ra_indices[idx * nframes: (idx + 1) * nframes, 0] = itraj * np.ones(nframes, dtype=int)
            ra_indices[idx * nframes: (idx + 1) * nframes, 1] = frames_sorted

        data = np.empty((ntrajs, nframes, ndims))

        count = 0
        for X in self._source.iterator(stride=ra_indices, lag=0, chunk=0, return_trajindex=False):
            for _ in range(0, itrajs_count[itraj_orig[count]]):
                data[itraj_orig[count], :, :] = X[frames_orig][:, dims]
                count += 1

        return data


class FeatureReaderJaggedRandomAccessStrategy(FeatureReaderCuboidRandomAccessStrategy):
    def _get_itraj_random_accessible(self, itrajs, frames, dims):
        itrajs = self._get_indices(itrajs, self._source.ntraj)
        return [self._source._ra_cuboid[itraj, frames, dims][0] for itraj in itrajs]


class FeatureReaderLinearItrajRandomAccessStrategy(FeatureReaderCuboidRandomAccessStrategy):
    def _get_itraj_random_accessible(self, itrajs, frames, dims):
        itrajs = self._get_indices(itrajs, self._source.ntraj)
        frames = self._get_indices(frames, sum(self._source.trajectory_lengths()[itrajs]))
        dims = self._get_indices(dims, self._source.ndim)

        nframes = len(frames)
        ndims = len(dims)

        if max(dims) > self._source.ndim:
            raise IndexError("Data only has %s dimensions, wanted to slice by dimension %s."
                             % (self._source.ndim, max(dims)))

        cumsum = np.cumsum(self._source.trajectory_lengths()[itrajs])

        from pyemma.coordinates.clustering import UniformTimeClustering
        ra = np.array([self._map_to_absolute_traj_idx(UniformTimeClustering._idx_to_traj_idx(x, cumsum), itrajs)
                       for x in frames])

        indices = np.lexsort((ra[:, 1], ra[:, 0]))
        ra = ra[indices]

        data = np.empty((nframes, ndims), dtype=self._source.output_type())

        curr = 0
        for X in self._source.iterator(stride=ra, lag=0, chunk=0, return_trajindex=False):
            L = len(X)
            data[indices[curr:curr + L]] = X
            curr += L

        return data

    def _map_to_absolute_traj_idx(self, cumsum_idx, itrajs):
        return itrajs[cumsum_idx[0]], cumsum_idx[1]


class FeatureReaderLinearRandomAccessStrategy(RandomAccessStrategy):
    def _handle_slice(self, idx):
        idx = np.index_exp[idx]
        frames, dims = None, None
        if isinstance(idx, (tuple, list)):
            if len(idx) == 1:
                frames, dims = idx[0], slice(None, None, None)
            if len(idx) == 2:
                frames, dims = idx[0], idx[1]
            if len(idx) > 2:
                raise IndexError("Slice was more than two-dimensional, not supported.")

        cumsum = np.cumsum(self._source.trajectory_lengths())
        frames = self._get_indices(frames, cumsum[-1])
        dims = self._get_indices(dims, self._source.ndim)

        nframes = len(frames)
        ndims = len(dims)

        frames_order = frames.argsort().argsort()
        frames_sorted = np.sort(frames)

        from pyemma.coordinates.clustering import UniformTimeClustering
        ra_stride = np.array([UniformTimeClustering._idx_to_traj_idx(x, cumsum) for x in frames_sorted])
        data = np.empty((nframes, ndims), dtype=self._source.output_type())

        offset = 0
        for X in self._source.iterator(stride=ra_stride, lag=0, chunk=0, return_trajindex=False):
            L = len(X)
            data[offset:offset + L, :] = X[:, dims]
            offset += L
        return data[frames_order]


class FeatureReaderIterator(DataSourceIterator):
    def __init__(self, data_source, skip=0, chunk=0, stride=1, return_trajindex=False, cols=None):
        # TODO: optimize cols access (eg. omit features, before calculating em
        super(FeatureReaderIterator, self).__init__(
                data_source, skip=skip, chunk=chunk, stride=stride,
                return_trajindex=return_trajindex,
                cols=cols
        )
        # set chunksize prior selecting the first file, to ensure we have a sane value for mditer...
        self.chunksize = chunk
        self._selected_itraj = -1

    @property
    def chunksize(self):
        return self.state.chunk

    @chunksize.setter
    def chunksize(self, value):
        self.state.chunk = value
        if hasattr(self, '_mditer'):
            self._mditer.chunksize = value

    @property
    def skip(self):
        return self.state.skip

    @skip.setter
    def skip(self, value):
        self.state.skip = value
        if hasattr(self, '_mditer'):
            self._mditer._skip = value

    def close(self):
        if hasattr(self, '_mditer') and self._mditer is not None:
            self._mditer.close()

    def _select_file(self, itraj):
        if itraj != self._selected_itraj:
            self.close()
            self._t = 0
            self._itraj = itraj
            self._selected_itraj = itraj
            self._create_mditer()

    def _next_chunk(self):
        """
        gets the next chunk. If lag > 0, we open another iterator with same chunk
        size and advance it by one, as soon as this method is called with a lag > 0.

        :return: a feature mapped vector X, or (X, Y) if lag > 0
        """
        if not hasattr(self, '_mditer') or self._mditer is None:
            self._select_file(self._itraj)
        try:
            chunk = next(self._mditer)
        except StopIteration as si:
            """ in case the underlying mdtraj iterator raises StopIteration (eg. seek failed),
                we have to return an empty iterable, so that LaggedIterator will continue to process.
            """
            if si.args and "too short" in si.args[0] and self._itraj < self._data_source.ntraj - 1:
                self._itraj += 1
                self._select_file(self._itraj)
                return ()
            else:
                raise

        shape = chunk.xyz.shape

        self._t += shape[0]

        if self._t >= self.trajectory_length() and self._itraj < len(self._data_source.filenames) - 1:
            self._itraj += 1
            self._select_file(self._itraj)

        if not self.uniform_stride:
            traj_len = self.ra_trajectory_length(self._itraj)
        else:
            traj_len = self.trajectory_length()
        if self._t >= traj_len and self._itraj == len(self._data_source.filenames) - 1:
            self.close()

        # 3 cases:
        # --------
        # 1. raw mdtraj.Trajectory objects
        # 2. plain reshaped coordinates (done by featurizer)
        # 3. extracted features
        if self._data_source._return_traj_obj:
            res = chunk
        else:
            # map data
            res = self._data_source.featurizer.transform(chunk)
        return res

    def _create_mditer(self):
        if not self.uniform_stride:
            while self._itraj not in self.traj_keys and self._itraj < self.number_of_trajectories():
                self._itraj += 1
            if self._itraj < self._data_source.ntraj:
                self._mditer = self._create_patched_iter(
                        self._data_source.filenames[self._itraj], stride=self.ra_indices_for_traj(self._itraj)
                )
        else:
            self._mditer = self._create_patched_iter(
                    self._data_source.filenames[self._itraj], skip=self.skip, stride=self.stride
            )
        self._closed = False

    def _create_patched_iter(self, filename, skip=0, stride=1, atom_indices=None):
        if self.is_uniform_stride(self.stride):
            flen = self._data_source.trajectory_length(itraj=self._itraj, stride=self.stride, skip=self.skip)
        else:
            flen = self.ra_trajectory_length(self._itraj)
        return patches.iterload(filename, flen, chunk=self.chunksize, top=self._data_source.featurizer.topology,
                                skip=skip, stride=stride, atom_indices=atom_indices)

