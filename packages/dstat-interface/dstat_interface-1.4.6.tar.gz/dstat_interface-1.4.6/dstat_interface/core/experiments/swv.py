import time
import struct
from copy import deepcopy

from .experiment_template import PlotBox, Experiment


class SWVBox(PlotBox):
    def setup(self):
        self.plot_format = {
            'swv': {'xlabel': "Voltage (mV)",
                    'ylabel': "Current (A)"
                    }
        }
    def format_plots(self):
        """
        Creates and formats subplots needed. Overrides superclass.
        """
        self.subplots = {'swv': self.figure.add_subplot(111)}
        
        for key, subplot in self.subplots.items():
            subplot.ticklabel_format(style='sci', scilimits=(0, 3),
                                     useOffset=False, axis='y')
            subplot.plot([],[])
            subplot.set_xlabel(self.plot_format[key]['xlabel'])
            subplot.set_ylabel(self.plot_format[key]['ylabel'])


class SWVExp(Experiment):
    """Square Wave Voltammetry experiment"""
    id = 'swv'

    def setup(self):
        self.datatype = "SWVData"
        self.xlabel = "Voltage (mV)"
        self.ylabel = "Current (A)"
        self.data = {
                     'swv' : [([], [], [], [])]
                    }  # voltage, current, forwards, reverse
        self.line_data = ([], [], [], [])
        self.datalength = 2 * self.parameters['scans']
        self.databytes = 10
        self.columns = ['Voltage (mV)', 'Net Current (A)',
                        'Forward Current (A)', 'Reverse Current (A)']
        self.plotlims = {
            'swv': {
                'xlims': tuple(sorted(
                    (int(self.parameters['start']),
                     int(self.parameters['stop']))
                )
                )
            }
        }

        plot = SWVBox()
        plot.setlims('swv', **self.plotlims['swv'])
        self.plots.append(plot)

        self.stop_mv = int(self.parameters['stop'])
        self.max_mv = abs(int(self.parameters['start']) - int(self.parameters['stop']))
        self.scan_points = self.max_mv * 2 / float(self.parameters['step'])

        self.commands += "E"
        self.commands[2] += "S"
        self.commands[2] += str(self.parameters['clean_s'])
        self.commands[2] += " "
        self.commands[2] += str(self.parameters['dep_s'])
        self.commands[2] += " "
        self.commands[2] += str(int(
                                    int(self.parameters['clean_mV'])/
                                    self.re_voltage_scale*
                                    (65536./3000)+32768
                                ))
        self.commands[2] += " "
        self.commands[2] += str(int(
                                    int(self.parameters['dep_mV'])/
                                    self.re_voltage_scale*
                                    (65536./3000)+32768
                                ))
        self.commands[2] += " "
        self.commands[2] += str(int(
                                    int(self.parameters['start'])/
                                    self.re_voltage_scale*
                                    (65536./3000)+32768
                                ))
        self.commands[2] += " "
        self.commands[2] += str(int(
                                    int(self.parameters['stop'])/
                                    self.re_voltage_scale*
                                    (65536./3000)+32768
                                ))
        self.commands[2] += " "
        self.commands[2] += str(int(
                                    int(self.parameters['step'])/
                                    self.re_voltage_scale*
                                    (65536./3000)
                                ))
        self.commands[2] += " "
        self.commands[2] += str(int(
                                    int(self.parameters['pulse'])/
                                    self.re_voltage_scale*
                                    (65536./3000)
                                ))
        self.commands[2] += " "
        self.commands[2] += str(self.parameters['freq'])
        self.commands[2] += " "
        self.commands[2] += str(self.parameters['scans'])
        self.commands[2] += " "
    
    def data_handler(self, input_data):
        """Overrides Experiment method to calculate difference current"""
        scan, data = input_data
        # uint16 + int32
        voltage, forward, reverse = struct.unpack('<Hll', data)
        f_trim = forward+self.gain_trim
        r_trim = reverse+self.gain_trim
        
        return (scan, (
                       (voltage-32768)*3000./65536*self.re_voltage_scale,
                       (f_trim-r_trim)*(1.5/self.gain/8388607),
                       f_trim*(1.5/self.gain/8388607),
                       r_trim*(1.5/self.gain/8388607)
                       )
                )
    
    def store_data(self, incoming, newline):
        """Stores data in data attribute. Should not be called from subprocess.
        Can be overriden for custom experiments."""
        line, data = incoming
        
        if newline is True:
            self.data['swv'].append(deepcopy(self.line_data))

        for i, item in enumerate(self.data['swv'][line]):
            item.append(data[i])

    def get_progress(self):
        try:
            if int(self.parameters['scans']) != 0:
                scans_prog = (len(self.data['swv'])-1) / float(self.parameters['scans'])
                scan_prog = (len(self.data['swv'][-1][0])-1) / self.scan_points / float(self.parameters['scans'])
                prog = scans_prog + scan_prog
                if prog > 1:
                    prog = 1
                return prog
            else:
                return 1 - (abs(self.stop_mv - self.data['swv'][-1][0][-1])/self.max_mv)
        except IndexError:
            return 0


class DPVExp(SWVExp):
    """Diffential Pulse Voltammetry experiment."""
    id = 'dpv'
    def setup(self):
        self.datatype = "SWVData"
        self.xlabel = "Voltage (mV)"
        self.ylabel = "Current (A)"
        self.data = {
                     'swv' : [([], [], [], [])]
                    }  # voltage, current, forwards, reverse
        self.line_data = ([], [], [], [])
        self.datalength = 2
        self.databytes = 10
        self.columns = ['Voltage (mV)', 'Net Current (A)',
                        'Forward Current (A)', 'Reverse Current (A)']

        self.plotlims = {
            'swv': {
                'xlims': tuple(sorted(
                    (int(self.parameters['start']),
                     int(self.parameters['stop']))
                )
                )
            }
        }

        plot = SWVBox()
        plot.setlims('swv', **self.plotlims['swv'])
        self.plots.append(plot)

        self.stop_mv = int(self.parameters['stop'])
        self.max_mv = abs(int(self.parameters['start']) - int(self.parameters['stop']))

        self.commands += "E"
        self.commands[2] += "D"
        self.commands[2] += str(self.parameters['clean_s'])
        self.commands[2] += " "
        self.commands[2] += str(self.parameters['dep_s'])
        self.commands[2] += " "
        self.commands[2] += str(int(
                                    int(self.parameters['clean_mV'])/
                                    self.re_voltage_scale*
                                    (65536./3000)+32768
                                ))
        self.commands[2] += " "
        self.commands[2] += str(int(
                                    int(self.parameters['dep_mV'])/
                                    self.re_voltage_scale*
                                    (65536./3000)+32768
                                ))
        self.commands[2] += " "
        self.commands[2] += str(int(
                                    int(self.parameters['start'])/
                                    self.re_voltage_scale*
                                    (65536./3000)+32768
                                ))
        self.commands[2] += " "
        self.commands[2] += str(int(
                                    int(self.parameters['stop'])/
                                    self.re_voltage_scale*
                                    (65536./3000)+32768
                                ))
        self.commands[2] += " "
        self.commands[2] += str(int(
                                    int(self.parameters['step'])/
                                    self.re_voltage_scale*
                                    (65536./3000)
                                ))
        self.commands[2] += " "
        self.commands[2] += str(int(
                                    int(self.parameters['pulse'])/
                                    self.re_voltage_scale*
                                    (65536./3000)
                                ))
        self.commands[2] += " "
        self.commands[2] += str(self.parameters['period'])
        self.commands[2] += " "
        self.commands[2] += str(self.parameters['width'])
        self.commands[2] += " "

    def get_progress(self):
        try:
            return 1 - (abs(self.stop_mv - self.data['swv'][-1][0][-1])/self.max_mv)
        except IndexError:
            return 0