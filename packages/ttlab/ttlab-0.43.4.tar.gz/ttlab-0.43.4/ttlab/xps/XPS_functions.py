import numpy as np
from scipy import exp
from plotly.offline import init_notebook_mode, iplot
import plotly.graph_objs as go
from astropy.modeling import models, fitting
import matplotlib.pyplot as plt

DEBUG = False


class XPSFunctions:

    @staticmethod
    def find_carbon_peak(energy,counts,background_model):
        return XPSFunctions.find_peak(energy=energy,
                                      counts=counts,
                                      range=[270, 310],
                                      background_model=background_model)

    @staticmethod
    def find_peak(energy, counts, range, background_model, show_fit=False, gaussian=False):
        start_index = XPSFunctions._find_index_of_nearest(energy, range[0])
        end_index = XPSFunctions._find_index_of_nearest(energy, range[1])
        x = energy[end_index:start_index]
        y = counts[end_index:start_index]
        if background_model == 'shirley':
            background = XPSFunctions._shirley_calculate(x, y)
        else:
            background = XPSFunctions._find_background(y)

        n = len(x)  # the number of data
        mean = x[np.argmax(y)]  # note this correction
        sigma = 1  # note this correction
        max = np.max(y - background)
        if gaussian:
            t_init = models.Gaussian1D(mean=mean, amplitude=max, stddev=sigma)
        else:
            t_init = models.Voigt1D(x_0=mean, amplitude_L=max, fwhm_L=sigma, fwhm_G=sigma)
        fit_t = fitting.LevMarLSQFitter()
        t = fit_t(t_init, x, y - background, maxiter=10000)

        if show_fit:
            plt.plot(x,y)
            plt.plot(x,background)
            plt.plot(x,t(x)+background)
            plt.gca().invert_xaxis()
            plt.show()

        if fit_t.fit_info['ierr'] > 4:      # An integer flag. If it is equal to 1, 2, 3 or 4, the solution was found. Otherwise, the solution was not found. In either case, the optional output variable ‘mesg’ gives more information.
            fitted_position = 0
            error = 0
            print(fit_t.fit_info['message'])
        else:
            if gaussian:
                fitted_position = t.mean.value
            else:
                fitted_position = t.x_0.value

            error = np.sqrt(np.diag(fit_t.fit_info['param_cov']))[0]

        return fitted_position, error

    @staticmethod
    def plotly_orbitals(xps_data, orbital, offset=0, offset_multiplier=1):
        init_notebook_mode(connected=True)
        traces = []
        for i, key in enumerate(xps_data):
            traces.append(
                XPSFunctions._create_x_y_trace(
                    x=xps_data[key].get_energy_multi(orbital),
                    y=xps_data[key].get_counts_multi(orbital) + offset * offset_multiplier * i,
                    name=key))

        layout = layout = XPSFunctions._get_plotly_layout(orbital)
        fig = dict(data=traces, layout=layout)
        return iplot(fig)

    @staticmethod
    def plotly_surveys(xps_data, offset=0, offset_multiplier=1):
        init_notebook_mode(connected=True)
        traces = []
        for i, key in enumerate(xps_data):
            traces.append(
                XPSFunctions._create_x_y_trace(
                    x=xps_data[key].get_energy_survey(),
                    y=xps_data[key].get_counts_survey()+offset*offset_multiplier*i,
                    name=key))

        layout = XPSFunctions._get_plotly_layout()
        fig = dict(data=traces, layout=layout)
        return iplot(fig)

    @staticmethod
    def plotly_peak_position(xps_data, orbital, fit_range, show_fit=False):
        if not isinstance(xps_data, dict):
            xps_data = {'': xps_data}

        peak_position, peak_position_error = XPSFunctions._create_position_array(xps_data=xps_data,orbital=orbital, fit_range=fit_range, show_fit=show_fit)

        init_notebook_mode(connected=True)
        traces = [XPSFunctions._create_x_y_error_trace(
                x=list(xps_data.keys()),
                y=peak_position,
                error=peak_position_error)]

        layout = XPSFunctions._get_plotly_errorbar_layout()
        fig = dict(data=traces, layout=layout)
        return iplot(fig)

    @staticmethod
    def _create_position_array(xps_data, orbital, fit_range, show_fit):
        position = []
        position_error = []
        for sample in xps_data.keys():
            [pos, err] = XPSFunctions.find_peak(xps_data[sample].get_energy_multi(orbital),
                                                xps_data[sample].get_counts_multi(orbital), fit_range, 'shirley', show_fit)
            if show_fit:
                print(sample)
            position.append(pos)
            position_error.append(err)
        return  position, position_error

    @staticmethod
    def _gaussian(x, a, x0, sigma):
        return a * exp(-(x - x0) ** 2 / (2 * sigma ** 2))


    @staticmethod
    def _find_index_of_nearest(array, value):
        return (np.abs(array - value)).argmin()

    @staticmethod
    def _find_background(counts):
        return np.linspace(counts[0],counts[-1],len(counts))

    @staticmethod
    def _create_x_y_error_trace(x, y, error,name=''):
        return go.Scatter(
        x=x,
        y=y,
        mode='markers+lines',
        name=name,
        error_y=dict(
            type='data',
            array=error,
            visible=True
        )
    )

    @staticmethod
    def _create_x_y_trace(x, y, name=''):
        return go.Scatter(
        x=x,
        y=y,
        mode='lines',
        name=name
    )

    @staticmethod
    def _get_plotly_layout(title=''):
        return go.Layout(
            title = title,
            xaxis=dict(
                autorange='reversed',
                title='Energy [eV]',
            ),
            yaxis=dict(
                title='Counts [a.u.]',
                exponentformat='e',
                showexponent='All'
            )
        )

    @staticmethod

    def _get_plotly_errorbar_layout(title=''):
        return go.Layout(
            title = title,
            yaxis=dict(
                title='Peakposition [nm]'
            )
        )

    # https://github.com/kaneod/physics/blob/master/python/specs.py
    @staticmethod
    def _shirley_calculate(x, y, tol=1e-5, maxit=20):
        """ S = specs.shirley_calculate(x,y, tol=1e-5, maxit=10)
        Calculate the best auto-Shirley background S for a dataset (x,y). Finds the biggest peak
        and then uses the minimum value either side of this peak as the terminal points of the
        Shirley background.
        The tolerance sets the convergence criterion, maxit sets the maximum number
        of iterations.
        """

        # Make sure we've been passed arrays and not lists.
        x = np.array(x)
        y = np.array(y)

        # Sanity check: Do we actually have data to process here?
        if not (x.any() and y.any()):
            print("specs.shirley_calculate: One of the arrays x or y is empty. Returning zero background.")
            return np.zeros(x.shape)

        # Next ensure the energy values are *decreasing* in the array,
        # if not, reverse them.
        if x[0] < x[-1]:
            is_reversed = True
            x = x[::-1]
            y = y[::-1]
        else:
            is_reversed = False

        # Locate the biggest peak.
        maxidx = abs(y - np.amax(y)).argmin()

        # It's possible that maxidx will be 0 or -1. If that is the case,
        # we can't use this algorithm, we return a zero background.
        if maxidx == 0 or maxidx >= len(y) - 1:
            print("specs.shirley_calculate: Boundaries too high for algorithm: returning a zero background.")
            return np.zeros(x.shape)

        # Locate the minima either side of maxidx.
        lmidx = abs(y[0:maxidx] - np.amin(y[0:maxidx])).argmin()
        rmidx = abs(y[maxidx:] - np.amin(y[maxidx:])).argmin() + maxidx
        xl = x[lmidx]
        yl = y[lmidx]
        xr = x[rmidx]
        yr = y[rmidx]

        # Max integration index
        imax = rmidx - 1

        # Initial value of the background shape B. The total background S = yr + B,
        # and B is equal to (yl - yr) below lmidx and initially zero above.
        B = np.zeros(x.shape)
        B[:lmidx] = yl - yr
        Bnew = B.copy()

        it = 0
        while it < maxit:
            if DEBUG:
                print("Shirley iteration: ", it)
            # Calculate new k = (yl - yr) / (int_(xl)^(xr) J(x') - yr - B(x') dx')
            ksum = 0.0
            for i in range(lmidx, imax):
                ksum += (x[i] - x[i + 1]) * 0.5 * (y[i] + y[i + 1]
                                                   - 2 * yr - B[i] - B[i + 1])
            k = (yl - yr) / ksum
            # Calculate new B
            for i in range(lmidx, rmidx):
                ysum = 0.0
                for j in range(i, imax):
                    ysum += (x[j] - x[j + 1]) * 0.5 * (y[j] +
                                                       y[j + 1] - 2 * yr - B[j] - B[j + 1])
                Bnew[i] = k * ysum
            # If Bnew is close to B, exit.
            if np.linalg.norm(Bnew - B) < tol:
                B = Bnew.copy()
                break
            else:
                B = Bnew.copy()
            it += 1

        if it >= maxit:
            print("specs.shirley_calculate: Max iterations exceeded before convergence.")
        if is_reversed:
            return (yr + B)[::-1]
        else:
            return yr + B

