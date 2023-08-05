import numpy as np


class X0Functions:

    @staticmethod
    def subtract_background(background,signal,gas):
        ion_current_bg = background.get_ion_current(gas=gas)
        time_relative_bg = background.get_ms_time(gas=gas)
        ion_current_signal = signal.get_ion_current(gas=gas)
        time_relative_signal = signal.get_ms_time(gas=gas)
        resulting_signal = []
        resulting_time = []
        for n in range(0,len(time_relative_signal)-1):
            index_of_nearest_time = X0Functions._find_index_of_nearest(time_relative_bg,time_relative_signal[n])
            if abs(time_relative_signal[n]-time_relative_bg[index_of_nearest_time])< 20:
                diff = ion_current_signal[n] - ion_current_bg[index_of_nearest_time]
                resulting_signal.append(diff)
                resulting_time.append(time_relative_signal[n])
        return np.array(resulting_signal), np.array(resulting_time)

    @staticmethod
    def _find_index_of_nearest(array, value):
        return (np.abs(array - value)).argmin()
