import PySimpleGUI as sg
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from numpy import dot, tile, sinc, newaxis
from scipy.fft import rfft, rfftfreq
import SignalComposer as main3


def draw_figure(canvas, figure):
    # Attach Matplotlib Figure To GUI CANVAS
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw_idle()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg


def main():
    sg.theme('Dark Red2')
    canvas1 = sg.Column([[sg.Canvas(size=(470, 100), key='-CANVAS-')]], key='secondary')
    canvas2 = sg.Column([[sg.Canvas(size=(470, 200), key='-CANVAS2-')]])

    layout = [
        [sg.Text('Signal-Reconstruction', size=(53, 1), justification='center', font='System 17')],
        [sg.Pane([canvas1, canvas2], key='pane', orientation='h', size=(940, 480))],
        [sg.Slider(orientation='horizontal', key='Nsamples', range=(0.0, 12.0))],
        [sg.Button('Set Samples'), sg.Button('Set Interpolation'), sg.Button('SignalComposer'),
         sg.Button('Show Graph'), sg.Button('Hide Graph'), sg.Button('Read File')]]
    window = sg.Window('Signal-Reconstruction', layout, finalize=True, resizable=True, auto_size_text=True,
                       auto_size_buttons=True, element_justification='center')
    # ax is known name for matplotlib axes
    fig, ax = plt.subplots(nrows=2, constrained_layout=True)
    fig2, ax2 = plt.subplots()
    # Choosing What To Draw On Each Canvas
    fig_agg = draw_figure(window['-CANVAS-'].TKCanvas, fig)
    fig_agg2 = draw_figure(window['-CANVAS2-'].TKCanvas, fig2)
    window.bind('<Configure>', 'Event')

    def prepareaxes(ax):
        ax.cla()
        ax.grid(True)
        ax.set_xlabel('Angle In Rad')
        ax.axhline(y=0, color='k')
        ax.axvline(x=0, color='k')

    def ExtractSigInfo(file='SignalDATA.csv'):
        datafile = pd.read_csv(file, header=0, index_col=False)
        sumsignal = [datafile.iloc[:, 1][i] for i in range(datafile.iloc[:, 0].size)]
        FrequencyComponent = rfft(sumsignal)
        # remove imaginary components in FFT
        FrequencyComponent = abs(FrequencyComponent)
        Frequencies = rfftfreq(len(sumsignal), 1 / 1000)
        Frequencieslist = [i for i in Frequencies if FrequencyComponent[int(i)] >= 100]
        MaxFrequency = max(Frequencieslist)
        time = [datafile.iloc[:, 0][i] for i in range(datafile.iloc[:, 0].size)]
        return MaxFrequency, sumsignal, time

    def Sampling(sumsignal, time):
        samples = int(values['Nsamples'])
        sampling_rate = int(1000 / samples)
        sumsignal_sampled_list = []
        time_sampled_list = []
        for i in range(0, len(time), sampling_rate):
            sumsignal_sampled_list.append(sumsignal[i])
            time_sampled_list.append(time[i])
        sumsignal_sampled = np.array(sumsignal_sampled_list)
        time_sampled = np.array(time_sampled_list)
        resampledsignal = (sumsignal_sampled, time_sampled)
        ax2.cla()
        prepareaxes(ax2)
        ax2.plot(time, sumsignal)
        ax2.plot(time_sampled, sumsignal_sampled, '*')
        ax2.set_title('Original Signal')
        fig_agg2.draw_idle()
        return resampledsignal

    def Interpolation(sumsig, time, resampledsignal):
        interpolatedsignal = sinc_interp(resampledsignal[0], resampledsignal[1], time)
        prepareaxes(ax[0])
        ax[0].plot(time, sumsig)
        ax[0].plot(resampledsignal[1], resampledsignal[0], '*')
        ax[0].plot(time, interpolatedsignal, '.', markersize=4)
        prepareaxes(ax[1])
        ax[1].plot(time, interpolatedsignal)
        ax[1].set_title('Reconstructed Signal')
        fig_agg.draw_idle()

    def sinc_interp(samples, sampletime, time):
        if len(samples) != len(sampletime):
            raise Exception('samples and sampletime must be the same length')

        # Find the period
        T = sampletime[1] - sampletime[0]

        sincM = tile(time, (len(sampletime), 1)) - tile(sampletime[:, newaxis], (1, len(time)))
        interpolatedsignal = dot(samples, sinc(sincM / T))
        return interpolatedsignal

    while True:
        event, values = window.read(timeout=10)
        if event in (sg.WIN_CLOSED, None):
            useless_exitnumber = 0
            exit(useless_exitnumber)
        if event == 'Set Samples':
            try:
                if fileflag is not True:
                    MaxFrequency, sumsignal, time = ExtractSigInfo()
            except:
                MaxFrequency, sumsignal, time = ExtractSigInfo()
            window['Nsamples'].update(range=(0, 3 * MaxFrequency))
            sampledsignal = Sampling(sumsignal, time)
        if event == 'Set Interpolation':
            Interpolation(sumsignal, time, sampledsignal)
        if event == 'SignalComposer':
            main3.main()
        if event == 'Hide Graph':
            window['secondary'].update(visible=False)
        if event == 'Show Graph':
            window['secondary'].update(visible=True)
        if event == 'Read File':
            filename = sg.popup_get_file('filename to open', no_window=True, file_types=(("CSV Files", "*.csv"),))
            fileflag = True
            MaxFrequency, sumsignal, time = ExtractSigInfo(filename)
        if event == 'Event':
            window['pane'].expand(True, True)
            window['-CANVAS-'].expand(True, True)
            window['-CANVAS2-'].expand(True, True)
    window.close()


if __name__ == '__main__':
    main()
