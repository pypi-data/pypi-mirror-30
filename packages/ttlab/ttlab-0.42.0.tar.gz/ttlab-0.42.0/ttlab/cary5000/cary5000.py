from .cary5000_data_reader import  Cary5000DataReader
from plotly.offline import init_notebook_mode, iplot
import plotly.graph_objs as go

class Cary5000:

    def __init__(self, filename):
        self.filename = filename
        self.data = Cary5000DataReader.read_data(filename=self.filename)

    def get_wavelength(self, sample):
        return self.data[sample].wavelength

    def get_transmission(self, sample):
        return self.data[sample].transmission

    def get_samples(self):
        return self.data.keys()

    def plotly_all(self, title=''):
        init_notebook_mode(connected=True)
        data = []
        for sample in self.get_samples():
            if sample == 'Baseline':
                continue
            x = self.data[sample].wavelength
            y = self.data[sample].transmission
            trace = Cary5000._create_x_y_trace(x, y, sample)
            data.append(trace)
        layout = Cary5000._get_plotly_layout(title)
        fig = go.Figure(data=data, layout=layout)
        return iplot(fig)


    @staticmethod
    def _create_x_y_trace(x, y, name):
        return go.Scatter(x=x, y=y, name=name)

    @staticmethod
    def _get_plotly_layout(title=''):
        return go.Layout(
            title = title,
            xaxis=dict(
                title='Wavelength [nm]'
            ),
            yaxis=dict(
                title='%T'
            )
        )
