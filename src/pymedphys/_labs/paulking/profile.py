# Copyright (C) 2019 Paul King, Simon Biggs

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version (the "AGPL-3.0+").

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License and the additional terms for more
# details.

# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

# ADDITIONAL TERMS are also included as allowed by Section 7 of the GNU
# Affero General Public License. These additional terms are Sections 1, 5,
# 6, 7, 8, and 9 from the Apache License, Version 2.0 (the "Apache-2.0")
# where all references to the definition "License" are instead defined to
# mean the AGPL-3.0+.

# You should have received a copy of the Apache-2.0 along with this
# program. If not, see <http://www.apache.org/licenses/LICENSE-2.0>.


# from copy import deepcopy
from typing import Callable
import copy

import numpy as np
from scipy import interpolate
# import matplotlib.pyplot as plt

# import xarray as xr

from ...libutils import get_imports
from ...xarray import XArrayComposition

# from .._level1.coreobjects import _PyMedPhysBase
IMPORTS = get_imports(globals())


NumpyFunction = Callable[[np.ndarray], np.ndarray]

#
# pylint: disable = C0103, C0121


# class DoseBase():
#     def __init__(self, data, coords=None, dims=None):
#         self._xarray = xr.DataArray(data, coords, dims, name='dose')

#     @property
#     def data(self) -> np.ndarray:
#         return self._xarray.data  # type: ignore

#     @data.setter
#     def data(self, array) -> None:
#         array = np.array(array)
#         self._xarray.data = array

#     def to_xarray(self):
#         return deepcopy(self._xarray)

#     def to_pandas(self):
#         return self.to_xarray().to_pandas()

#     def to_dict(self):
#         return self.to_xarray().to_dict()

#     def deepcopy(self):
#         return deepcopy(self)


# class Dose1D(DoseBase):
#     def __init__(self, x, data):
#         coords = [('x', x)]
#         super().__init__(data, coords)

#     @property
#     def x(self) -> np.ndarray:
#         return self._xarray.x.data  # type: ignore

#     @x.setter
#     def x(self, array) -> None:
#         array = np.array(array)
#         if len(np.shape(array)) != 1:
#             raise ValueError("`x` must be of one dimension.")

#         self._xarray.x.data = array

#     @property
#     def interp(self) -> NumpyFunction:
#         return interpolate.interp1d(self.x, self.data)  # type: ignore

#     def shift(self, applied_shift, inplace=False):
#         if inplace:
#             adjusted_object = self
#         else:
#             adjusted_object = self.deepcopy()

#         adjusted_object.x = adjusted_object.x + applied_shift

#         if not inplace:
#             return adjusted_object

#     def plot(self):
#         return plt.plot(self.x, self.data, 'o-')

#     def interactive(self):
#         pass

# class DoseProfile(Dose1D):
#     def __init__(self, x, data, metadata={}):
#         self.metadata = metadata
#         super().__init__(x, data)


class Profile():
    def __init__(self, x=[], data=[], metadata={}):
        self.x = np.array(x)
        self.data = np.array(data)
        self.metadata = metadata
        if len(self.x) < 2:
            self.interp = None
        else:
            self.interp = interpolate.interp1d(self.x, self.data)

    def __len__(self):
        assert len(self.x) == len(self.data)
        return len(self.x)

    def __eq__(self, other):
        if np.array_equal(self.x, other.x) and \
           np.array_equal(self.data, other.data) and \
           self.metadata == other.metadata:
            return True
        else:
            return False

    def __copy__(self):
        return copy.deepcopy(self)

    def __str__(self):
        beginning = str(self.__str__).split('of ')[-1].split(' at')[0]
        middle = ' of length {}'.format(len(self))
        ending = '>'
        result = beginning + middle + ending
        return(result)

    def from_lists(self, x, data, metadata={}):
        self.x = np.array(x)
        self.data = np.array(data)
        self.__init__(x=x, data=data, metadata=metadata)
        return(Profile(x=x, data=data, metadata=metadata))

    def from_tuples(self, list_of_tuples, metadata={}):
        """ Load a list of (x,data) tuples.

        Overwrites any existing dose profile data and metadata.

        Arguments
        ---------
        list_of_tuples : list
            List of (float x, float data) tuples.

        Keyword Arguments
        -----------------
        metadata : dict, optional
            Dictionary of key-value pairs that describe the profile

        Returns
        -------
        array_like

        """
        x = list(list(zip(*list_of_tuples))[0])
        data = list(list(zip(*list_of_tuples))[1])
        self.__init__(x=x, data=data, metadata=metadata)
        return Profile(x=x, data=data, metadata=metadata)

    def from_snc_profiler(self):
        """ """
        pass

    def get_dose(self, x) -> float:
        """ Profile dose value at distance.

        Return value based on interpolation of source data.

        Argument
        -----------------
        x : float
            End points for incluion, default to source profile end-points

        Returns
        -------
        float

         """
        try:
            return self.interp(x)
        except ValueError:
            return np.nan

    def segment(self, start=-np.inf, stop=np.inf):
        """ Part of dose profile between begin and end.

        Resulting profile is comprised of those points in the source
        profile whose distance values are not-less-than start and
        not-greater-than stop.

        Keyword Arguments
        -----------------
        start, stop : float, optional
            Result end points, default to source end-points

        Returns
        -------
        Profile

        """
        try:
            start = max(start, min(self.x))  # default & limit to curve ends
            stop = min(stop, max(self.x))
            new_x = self.x[np.logical_and(self.x >= start, self.x <= stop)]
            new_data = self.interp(new_x)
        except ValueError:
            new_x = []
            new_data = []
        self.__init__(new_x, new_data)
        return Profile(new_x, new_data)

    def resample(self, step):
        """ Resample a dose profile at a specified increment.

        Resulting profile has stepsize of the indicated step based on
        linear interpolation over the points of the source profile.

        Arguments
        -----------------
        step : float
            Sampling increment

        Returns
        -------
        Profile

        """

        new_x = np.arange(self.x[0], self.x[-1], step)
        new_data = self.interp(new_x)
        self.__init__(new_x, new_data, self.metadata)
        return Profile(new_x, new_data, self.metadata)

    def normalise_dose(self, x=0.0, data=1.0):
        """ Renormalise to specified dose at distance.

        Source profile values multiplied by scaling factor to yield the specified dose at
        the specified distance. If distance is not specified, the central axis value is
        used. If dose is not specified, then normalization is to unity. With neither
        specified, resulting curve is the conventional off-center-ratio.

        Keywork Arguments
        -----------------
        x : float
        data : float

        Returns
        -------
        DoseProfile

        """
        norm_factor = data / self.get_dose(x)
        new_x = self.x
        new_data = norm_factor * self.data
        metadata = self.metadata
        self.__init__(new_x, new_data, self.metadata)
        return Profile(new_x, new_data)

    def normalize_dose(self, x=0.0, data=1.0):
        """ US Eng -> UK Eng """
        return self.normalise_dose(x=x, data=data)

    def edges(self, step):
        """ Edges of a profile, as a tuple.

        Return left and right edges of a profile, identified
        as the points of greatest positive and greatest negative
        gradient.

        Arguments
        -----------------
        step : float
            Precision of result

        Returns
        -------
        tuple

        """
        resampled = self.resample(step)
        dydx = list(np.gradient(self.data, self.x))
        lt_edge = self.x[dydx.index(max(dydx))]
        rt_edge = self.x[dydx.index(min(dydx))]
        return (lt_edge, rt_edge)

    def normalise_distance(self):
        pass

    def normalize_distance(self):
        pass

    def umbra(self):
        pass

    def centre(self):
        pass

    def shift_to_centre(self):
        pass

    def flatness(self):
        pass

    def symmetry(self):
        pass

    def symmetrise(self):
        pass

    def interactive(self):
        pass


class DoseDepth():
    pass


# # PRIVATE FUNCTIONS ======================================

# def _make_dose_vals(dist_vals, dose_func):
#     """ Return list of dose-vals at distance-vals with generating function. """
#     dose_vals = []
#     for dist in dist_vals:
#         try:
#             dose_vals.append(float(dose_func(dist)))
#         except ValueError:   # ZERO OUTSIDE DOSE_FUNC'S DOMAIN
#             dose_vals.append(0.0)
#     return dose_vals


# def _find_umbra(dose_prof):
#     """ Return a list of distances over the central 80% a dose profile. """
#     e = edges(dose_prof)
#     dist_strt = 0.8 * e[0]
#     dist_stop = 0.8 * e[-1]
#     umbra = [d for d in dose_prof if d[0] >= dist_strt and d[0] <= dist_stop]
#     return umbra


# def _find_dists(dose_prof, dose):
#     """
#     Return a list of distances where a dose-profile has value of dose.

#     """

#     x = _get_dist_vals(dose_prof)
#     y = _get_dose_vals(dose_prof)
#     dists = []
#     for i in range(1, len(x)):
#         val = None
#         if y[i] != y[i-1]:
#             if (y[i]-dose)*(y[i-1]-dose) < 0:
#                 val = (x[i]-((y[i]-dose)/(y[i]-y[i-1]))*(x[i]-x[i-1]))
#         elif y[i] == dose:
#             val = x[i]
#         if val and (val not in dists):
#             dists.append(val)
#     return dists


# def _shift_dose_prof(dose_prof, dist):
#     """
#     Return a dose-profile whose distances are shifted by a specified distance.
#     """
#     dist_vals = np.add(_get_dist_vals(dose_prof), dist)
#     dose_vals = list(list(zip(*dose_prof))[1])
#     dose_vals = _get_dose_vals(dose_prof)
#     return list(zip(dist_vals, dose_vals))


# # PUBLIC FUNCTIONS ==========================================

# def pulse(centre=0.0, center=None, width=10.0,
#           dist_strt=-20.0, dist_stop=20.0, dist_step=0.1):
#     """
#     Return a pulse shaped dose-profile; specified centre, width, and domain.
#     """
#     if center:  # US Eng -> UK Eng
#         centre = center

#     def pulse(centre, width, dist):
#         if abs(dist) > (centre + width/2.0):
#             return 0.0
#         if abs(dist) < (centre + width/2.0):
#             return 1.0
#         return 0.5

#     dist_vals = np.arange(dist_strt, dist_stop + dist_step, dist_step)
#     dose_vals = _make_dose_vals(dist_vals, partial(pulse, centre, width))
#     dose_prof = list(zip(dist_vals, dose_vals))
#     return dose_prof


# def overlay(dose_prof_moves, dose_prof_fixed, dist_step=0.1):
#     """
#     Return as a float, the misalignment between two dose-profiles, i.e. the
#     distance by which one would need to move to align to the other.

#     """

#     dist_vals_moves = _get_dist_vals(dose_prof_moves)

#     dist_vals_fixed = _get_dist_vals(dose_prof_fixed)
#     dose_vals_fixed = _get_dose_vals(dose_prof_fixed)

#     # POSSIBLE OFFSETS --------------------------
#     step = 0.5 * min(min(np.diff(dist_vals_moves)),
#                      min(np.diff(dist_vals_fixed)))
#     strt = max(min(dist_vals_moves), min(dist_vals_fixed))
#     stop = min(max(dist_vals_moves), max(dist_vals_fixed)) + step
#     possible_offsets = np.arange(strt, stop, step)
#     # --------------------------------------------

#     dose_func_fixed = interpolate.interp1d(dist_vals_fixed, dose_vals_fixed)

#     # DISTANCE VALUES OF FIXED CURVE ------------------------
#     strt = 3 * min(min(dist_vals_moves), min(dist_vals_fixed))
#     stop = 3 * max(max(dist_vals_moves), max(dist_vals_fixed)) + dist_step
#     dist_vals_fixed = np.arange(strt, stop, dist_step)
#     # -------------------------------------------------------

#     dose_vals_fixed = _make_dose_vals(dist_vals_fixed, dose_func_fixed)

#     # EVALUATE FIT AT ALL CANDIDATE SHIFT POSITIONS -----------
#     best_fit_qual = 0
#     best_offset = -np.inf
#     for offset in possible_offsets:
#         moved_profile = _shift_dose_prof(dose_prof_moves, offset)
#         moved_dist_vals = _get_dist_vals(moved_profile)
#         moved_dose_vals = _get_dose_vals(moved_profile)
#         dose_func_moves = interpolate.interp1d(moved_dist_vals,
#                                                moved_dose_vals)
#         fit_qual = np.correlate(
#             dose_vals_fixed,
#             _make_dose_vals(dist_vals_fixed, dose_func_moves))
#         if max(fit_qual) > best_fit_qual:
#             best_fit_qual = max(fit_qual)
#             best_offset = offset
#     # ----------------------------------------------------------

#     return best_offset


# def normalise_distance(dose_prof):
#     """
#     Return a dose-profile which is  rescaled to 2X/W distance
#     so as to force the beam edges to distances of +/-1.

#         | (1) Milan & Bentley, BJR Feb-74, The Storage and manipulation
#               of radiation dose data in a small digital computer
#         | (2) Heintz, King, & Childs, May-95, User Manual,
#               Prowess 3000 CT Treatment Planning
#     """

#     x = _get_dist_vals(dose_prof)
#     d = _get_dose_vals(dose_prof)

#     lt_edge, rt_edge = edges(dose_prof)
#     cax = (lt_edge + rt_edge)/2.0

#     result = []
#     for i, dist in enumerate(x):
#         if dist < cax:
#             result.append((dist/lt_edge, d[i]))
#         elif dist == cax:
#             result.append((0.0, d[i]))
#         elif dist > cax:
#             result.append((dist/rt_edge, d[i]))
#     return result


# def normalize_distance(dose_prof):
#     """ US Eng -> UK Eng """
#     return normalise_distance(dose_prof)


# def recentre(dose_prof):
#     """
#     Return a translated dose-profile in which the central-axis,
#     midway between the edges, is defined as zero distance.
#     Also, recenter().

#     """

#     dist_vals = _get_dist_vals(dose_prof)
#     dose_vals = _get_dose_vals(dose_prof)
#     cax = np.mean(edges(dose_prof))

#     cent_prof = []
#     for i, dist in enumerate(dist_vals):
#         cent_prof.append((dist - cax, dose_vals[i]))
#     return cent_prof


# def recenter(dose_prof):
#     """ US Eng -> UK Eng """
#     return recentre(dose_prof)


# def flatness(dose_prof):
#     """
#     Return float flatness of a dose-profile.
#     """
#     dose = _get_dose_vals(_find_umbra(dose_prof))
#     flat = (max(dose)-min(dose))/np.average(dose)
#     return flat


# def symmetry(dose_prof):
#     """
#     Return float symmetry of a dose-profile.
#     """
#     dose = _get_dose_vals(_find_umbra(dose_prof))
#     avg_dose = np.average(dose)
#     dose_rev = dose[::-1]
#     asymmetry = max(np.abs(np.subtract(dose, dose_rev)/avg_dose))
#     return asymmetry


# def symmetrise(dose_prof, dist_step=0.1):
#     """
#     Return a symmetric dose-profile, averaging dose values over
#     locations across the CAX, and resampled. Also, symmetrize()

#     """
#     dist_vals = _get_dist_vals(dose_prof)

#     strt = -min(-dist_vals[0], dist_vals[-1])
#     stop = min(-dist_vals[0], dist_vals[-1])

#     dose_prof = resample(dose_prof, dist_strt=strt,
#                          dist_stop=stop, dist_step=dist_step)

#     rev = dose_prof[::-1]

#     result = [(dose_prof[i][0], (dose_prof[i][1]+rev[i][1])/2.0)
#               for i, _ in enumerate(dose_prof)]

#     return result


# def symmetrize(dose_prof, dist_step=0.1):
#     """ US Eng -> UK Eng """
#     return symmetrise(dose_prof, dist_step)


# def is_wedged(dose_prof):
#     """ Return True iff dose-profile has significant gradient in the umbra. """
#     wedginess = np.average(np.diff(_get_dose_vals(_find_umbra(dose_prof))))
#     if wedginess > 0.05:  # 'magic number'
#         return True
#     else:
#         return False
