import numpy as np
from plotly.offline import init_notebook_mode, iplot
import plotly.graph_objs as go
from astropy.modeling import models, fitting
import matplotlib.pyplot as plt


class Cary5000Functions:

    @staticmethod
    def find_peak(wavelength, transmission, range):
        start_index = Cary5000Functions._find_index_of_nearest(wavelength, range[0])
        end_index = Cary5000Functions._find_index_of_nearest(wavelength, range[1])
        x = wavelength[end_index:start_index]
        y = -transmission[end_index:start_index]
        background = Cary5000Functions._find_background(y)
        n = len(x)  # the number of data
        mean = x[np.argmax(y)]  # note this correction
        sigma = 1  # note this correction
        max = np.max(y - background)
        t_init = models.Gaussian1D(mean=mean, amplitude=max, stddev=sigma)
        fit_t = fitting.LevMarLSQFitter()
        t = fit_t(t_init, x, y - background, maxiter=10000)

        # plt.plot(x, y, 'ko')
        # plt.plot(x, t(x) + background, label='gauss')
        # plt.show()

        if fit_t.fit_info['ierr'] > 4:  # An integer flag. If it is equal to 1, 2, 3 or 4, the solution was found. Otherwise, the solution was not found. In either case, the optional output variable ‘mesg’ gives more information.
            fitted_position = 0
            error = 0
            print(fit_t.fit_info['message'])
        else:
            fitted_position = t.mean.value
            error = np.sqrt(np.diag(fit_t.fit_info['param_cov']))[0]

        return fitted_position, error

    @staticmethod
    def _create_min_peak_array(data, range):
        bla = []
        error = []
        for key in data.get_samples():
            if key == 'Baseline':
                continue
            amin = np.argmin(np.array(data.get_transmission(key)))
            bla.append(data.get_wavelength(key)[amin])
            error.append(float(0.5))

        return bla, error


    @staticmethod
    def plotly_peakposition(spectras, range, method = 0):

        if not isinstance(spectras,dict):
            spectras = {'' : spectras}

        init_notebook_mode(connected=True)
        trace = []
        for name, data in spectras.items():
            if method == 0:
                x, error = Cary5000Functions._create_peak_array(data,range)
            else:
                x, error = Cary5000Functions._create_min_peak_array(data, range)
            y = []
            for key in data.get_samples():
                if key == 'Baseline':
                    continue
                y.append(key)
            trace.append(Cary5000Functions._create_x_y_trace(y, x, error, name))

        layout = Cary5000Functions._get_plotly_layout()
        fig = go.Figure(data=trace, layout=layout)
        return iplot(fig)

    @staticmethod
    def _create_peak_array(data, range):
        peaks = []
        error = []
        for key in data.get_samples():
            if key == 'Baseline':
                continue
            tmp_peak, tmp_error = Cary5000Functions.find_peak(data.get_wavelength(key), data.get_transmission(key), range)
            peaks.append(tmp_peak)
            error.append(tmp_error)
        return peaks, error

    @staticmethod
    def _find_index_of_nearest(array, value):
        return (np.abs(array - value)).argmin()

    @staticmethod
    def _find_background(counts):
        return np.linspace(counts[0],counts[-1],len(counts))

    @staticmethod
    def _create_x_y_trace(x, y, error,name):
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
    def _get_plotly_layout(title=''):
        return go.Layout(
            title = title,
            xaxis=dict(
                title='Sample'
            ),
            yaxis=dict(
                title='Peak Position [nm]'
            )
        )

