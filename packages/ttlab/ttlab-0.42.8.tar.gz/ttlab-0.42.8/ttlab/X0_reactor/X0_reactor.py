from ..mass_spectrometer import MassSpectrometer
from ..flow_reactor import FlowReactor
import numpy as np
import matplotlib.pyplot as plt


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

    def correct_for_drifting(self,correction_gas='Ar'):
        self.MassSpectrometer.correct_for_drifting(correction_gas=correction_gas)

    def calculate_activation_energy(self,time_intervals,gas):
        temperature = np.array([])
        ion_current = np.array([])
        for interval in time_intervals:
            temperature = np.append(temperature,[self._get_average_sample_temperature_in_interval(interval)])
            ion_current = np.append(ion_current,[self._get_average_ion_current_in_interval(interval,gas)])
        linear_fit = np.polyfit(1 / (temperature+273), np.log(ion_current), 1)
        boltzmann_constant = 0.0083144621 # kj/(K*mol)
        activation_energy = -linear_fit[0]*boltzmann_constant
        return activation_energy, temperature, ion_current, linear_fit

    def plot_activation_energy(self,time_intervals,gas,ax=None):
        activation_energy, temperature, ion_current, linear_fit = self.calculate_activation_energy(time_intervals,gas)
        boltzmann_constant = 0.0083144621 # kj/(K*mol)
        temperature_fit = np.array([1/(temperature[0]+273), 1/(temperature[len(temperature)-1]+273)])
        ion_current_fit = temperature_fit*linear_fit[0] + linear_fit[1]
        if ax is None:
            ax = plt.axes()
        ax.plot(1/(temperature+273),np.log(ion_current),'o')
        ax.plot(temperature_fit,ion_current_fit, label=str(round(activation_energy,2)) + ' kJ/mol')
        ax.legend()
        return ax


    def _get_average_sample_temperature_in_interval(self, interval):
        sample_temperature = self.get_sample_temperature()
        flow_reactor_time = self.get_flow_reactor_time()
        start_index = self._find_index_of_nearest(flow_reactor_time,interval[0])
        end_index = self._find_index_of_nearest(flow_reactor_time,interval[1])
        return np.mean(sample_temperature[start_index:end_index])

    def _get_average_ion_current_in_interval(self,interval,gas):
        ion_current = self.get_ion_current(gas)
        ms_time = self.get_ms_time(gas)
        start_index = self._find_index_of_nearest(ms_time,interval[0])
        end_index = self._find_index_of_nearest(ms_time,interval[1])
        return np.mean(ion_current[start_index:end_index])

    def _align_times(self):
        time_difference = self.MassSpectrometer.start_time - self.FlowReactor.start_time
        self.MassSpectrometer.shift_start_time_back(time_difference)

    @staticmethod
    def _find_index_of_nearest(array, value):
        return (np.abs(array - value)).argmin()
