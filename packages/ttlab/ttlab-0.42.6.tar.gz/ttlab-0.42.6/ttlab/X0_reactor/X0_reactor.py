from ..mass_spectrometer import MassSpectrometer
from ..flow_reactor import FlowReactor


class X0Reactor:

    def __init__(self, filename_ms, filename_fr):
        self.MassSpectrometer = MassSpectrometer(filename=filename_ms)
        self.FlowReactor = FlowReactor(filename=filename_fr)
        self._align_times()

    def plot_ms(self, gas, ax=None, color=None):
        return self.MassSpectrometer.plot(gas=gas, ax=ax, color=color)

    def plot_all_ms(self,ax=None):
        return self.MassSpectrometer.plot_all(ax)

    def plot_flow_rate(self, mfc):
        return self.FlowReactor.plot_flow_rate(mfc)

    def plot_reactor_temperature(self):
        return self.FlowReactor.plot_reactor_temperature()

    def plot_sample_temperature(self, ax=None):
        return self.FlowReactor.plot_sample_temperature(ax)

    def get_sample_temperature(self):
        return self.FlowReactor.get_sample_temperature()

    def get_flow_reactor_time(self):
        return self.FlowReactor.get_time()

    def get_ms_time(self,gas):
        return self.MassSpectrometer.get_time_relative(gas)

    def get_ion_current(self,gas):
        return self.MassSpectrometer.get_ion_current(gas)

    def _align_times(self):
        time_difference = self.MassSpectrometer.start_time - self.FlowReactor.start_time
        self.MassSpectrometer.shift_start_time_back(time_difference)
