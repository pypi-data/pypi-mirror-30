# -*- coding: utf-8 -*-

# Copyright © 2017, Institut Pasteur
#   Contributor: François Laurent

# This file is part of the TRamWAy software available at
# "https://github.com/DecBayComp/TRamWAy" and is distributed under
# the terms of the CeCILL license as circulated at the following URL
# "http://www.cecill.info/licenses.en.html".

# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license and that you accept its terms.


from .base import *
from warnings import warn
from math import pi, log
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from collections import OrderedDict


setup = {'name': 'smooth.d',
	'provides': 'd',
	'arguments': OrderedDict((
		('localization_error',	('-e', dict(type=float, default=0.03, help='localization error'))),
		('diffusivity_prior',	('-d', dict(type=float, default=0.05, help='prior on the diffusivity'))),
		('jeffreys_prior',	('-j', dict(action='store_true', help="Jeffreys' prior"))),
		('min_diffusivity',	dict(type=float, help='minimum diffusivity value allowed')))),
	'cell_sampling': 'group'}


def smooth_d_neg_posterior(diffusivity, cells, squared_localization_error, diffusivity_prior, \
		jeffreys_prior, dt_mean, min_diffusivity):
	"""
	Adapted from InferenceMAP's *dDDPosterior* procedure::

		for (int a = 0; a < NUMBER_OF_ZONES; a++) {
			ZONES[a].gradDx = dvGradDx(DD,a);
			ZONES[a].gradDy = dvGradDy(DD,a);
			ZONES[a].priorActive = true;
		}

		for (int z = 0; z < NUMBER_OF_ZONES; z++) {
			const double gradDx = ZONES[z].gradDx;
			const double gradDy = ZONES[z].gradDy;
			const double D = DD[z];

			for (int j = 0; j < ZONES[z].translocations; j++) {
				const double dt = ZONES[z].dt[j];
				const double dx = ZONES[z].dx[j];
				const double dy = ZONES[z].dy[j];
				const double Dnoise = LOCALIZATION_ERROR*LOCALIZATION_ERROR/dt;

				result += - log(4.0*PI*(D + Dnoise)*dt) - ( dx*dx + dy*dy)/(4.0*(D+Dnoise)*dt);
			}

			if (ZONES[z].priorActive == true) {
				result -= D_PRIOR*(gradDx*gradDx*ZONES[z].areaX + gradDy*gradDy*ZONES[z].areaY);
				if (JEFFREYS_PRIOR == 1) {
					result += 2.0*log(D) - 2.0*log(D*ZONES[z].dtMean + LOCALIZATION_ERROR*LOCALIZATION_ERROR);
				}
			}
		}

		return -result;

	"""
	if min_diffusivity is not None:
		observed_min = np.min(diffusivity)
		if observed_min < min_diffusivity and not np.isclose(observed_min, min_diffusivity):
			warn(DiffusivityWarning(observed_min, min_diffusivity))
	noise_dt = squared_localization_error
	result = 0.
	for j, i in enumerate(cells):
		cell = cells[i]
		n = len(cell)
		# posterior calculations
		if cell.cache['dr2'] is None:
			cell.cache['dr2'] = np.sum(cell.dr * cell.dr, axis=1) # dx**2 + dy**2 + ..
		D_dt = 4. * (diffusivity[j] * cell.dt + noise_dt) # 4*(D+Dnoise)*dt
		result += n * log(pi) + np.sum(np.log(D_dt)) # sum(log(4*pi*Dtot*dt))
		result += np.sum(cell.cache['dr2'] / D_dt) # sum((dx**2+dy**2+..)/(4*Dtot*dt))
		# prior
		if diffusivity_prior:
			# gradient of diffusivity
			gradD = cells.grad(i, diffusivity)
			if gradD is not None:
				result += diffusivity_prior * cells.grad_sum(i, gradD * gradD)
	if jeffreys_prior:
		result += 2. * np.sum(np.log(diffusivity * dt_mean + squared_localization_error))
	return result

def infer_smooth_D(cells, localization_error=0.03, diffusivity_prior=0.05, jeffreys_prior=None, \
	min_diffusivity=None, **kwargs):
	if min_diffusivity is None:
		if jeffreys_prior:
			min_diffusivity = 0.01
		else:
			min_diffusivity = 0
	elif min_diffusivity is False:
		min_diffusivity = None
	# initialize the diffusivity array and the caches
	index, dt_mean, D_initial = [], [], []
	for i in cells:
		cell = cells[i]
		# sanity checks
		if not bool(cell):
			raise ValueError('empty cells')
		# ensure that translocations are properly oriented in time
		if not np.all(0 < cell.dt):
			warn('translocation dts are not all positive', RuntimeWarning)
			cell.dr[cell.dt < 0] *= -1.
			cell.dt[cell.dt < 0] *= -1.
		# initialize the cache
		cell.cache = dict(dr2=None)
		# initialize the local diffusivity parameter
		dt_mean_i = np.mean(cell.dt)
		D_initial_i = np.mean(cell.dr * cell.dr) / (2. * dt_mean_i)
		#
		index.append(i)
		dt_mean.append(dt_mean_i)
		D_initial.append(D_initial_i)
	any_cell = cell
	index, dt_mean, D_initial = np.array(index), np.array(dt_mean), np.array(D_initial)
	# parametrize the optimization procedure
	if min_diffusivity is not None:
		kwargs['bounds'] = [(min_diffusivity,None)] * D_initial.size
	# run the optimization
	sle = localization_error * localization_error # sle = squared localization error
	result = minimize(smooth_d_neg_posterior, D_initial, \
		args=(cells, sle, diffusivity_prior, jeffreys_prior, dt_mean, min_diffusivity), \
		**kwargs)
	# format the result
	D = result.x
	DD = pd.DataFrame(D, index=index, columns=['diffusivity'])
	return DD

