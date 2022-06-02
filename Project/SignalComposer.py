import csv
import PySimpleGUI as sg
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw_idle()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg


def main():
    sg.theme('Dark Brown2')

    # GUI Customizations
    ElementJustification = 'center'
    ElementResolution = 0.1
    ElementFont = 'System 17'
    SliderOrientation = 'horizontal'
    SliderRange1 = 0.0, 50.0
    SliderRange2 = 0.0, 2 * np.pi
    TextSize = 23, 1
    enableevent = True

    canvas1 = sg.Column([[sg.Canvas(size=(470, 100), key='-CANVAS-')]], key='Col1')
    canvas2 = sg.Column([[sg.Canvas(size=(470, 200), key='-CANVAS2-')]])

    layout = [[sg.Text('SignalComposer', size=(53, 1), justification=ElementJustification, font=ElementFont)],
              [sg.Text('Select The Signal You Want To Delete', font='System 10')],
              [sg.Combo(['Sine', 'Cosine', 'Both'], key='delsignal', readonly=True),
               sg.Combo(['0', '1'], key='delsignal2', readonly=True)],
              [sg.Pane([canvas1, canvas2], key='pane', orientation='h', size=(940, 480))],
              [sg.Text('Sin Magnitude', size=TextSize, justification=ElementJustification),
               sg.Text('Cos Magnitude', size=TextSize, justification=ElementJustification),
               sg.Text('Frequency', size=TextSize, justification=ElementJustification),
               sg.Text('Sin PhaseShift', size=TextSize, justification=ElementJustification),
               sg.Text('Cos PhaseShift', size=TextSize, justification=ElementJustification)],
              [sg.Slider(orientation=SliderOrientation, key='Sine Magnitude', range=SliderRange1,
                         resolution=ElementResolution, enable_events=enableevent),
               sg.Slider(orientation=SliderOrientation, key='Cosine Magnitude', range=SliderRange1,
                         resolution=ElementResolution, enable_events=enableevent),
               sg.Slider(orientation=SliderOrientation, key='Frequency', range=SliderRange1, enable_events=enableevent),
               sg.Slider(orientation=SliderOrientation, key='PhaseShift', range=SliderRange2,
                         resolution=ElementResolution, enable_events=enableevent),
               sg.Slider(orientation=SliderOrientation, key='PhaseShift2', range=SliderRange2,
                         resolution=ElementResolution, enable_events=enableevent)],
              [sg.Button('Set Changes!'), sg.Button('Delete Signal'),
               sg.Button('Save Data'), sg.Button('Plot Changes')]]
    window = sg.Window('SignalComposer', layout, finalize=True, resizable=True, auto_size_text=True,
                       auto_size_buttons=True, element_justification=ElementJustification)
    fig, ax = plt.subplots()
    fig2, ax2 = plt.subplots(nrows=3, constrained_layout=True)
    fig_agg = draw_figure(window['-CANVAS-'].TKCanvas, fig)
    fig_agg2 = draw_figure(window['-CANVAS2-'].TKCanvas, fig2)
    EventList = ['Sine Magnitude', 'Cosine Magnitude', 'Frequency', 'PhaseShift', 'PhaseShift2']
    # Binding Maximize Window Event To GUI EVENTS
    window.bind('<Configure>', 'Event')

    def preparesignals():
        time = np.linspace(-np.pi, np.pi, 1000)
        sin = values['Sine Magnitude'] * (np.sin(values['Frequency'] * time - values['PhaseShift']))
        cos = values['Cosine Magnitude'] * (np.cos(2 * values['Frequency'] * time - values['PhaseShift2']))
        return sin, cos, time

    def plotrealtime():
        ax2[2].cla()
        prepareaxes(ax2[2])
        sin, cos, time = preparesignals()
        ax2[2].plot(time, sin + cos)
        fig_agg2.draw_idle()

    def prepareaxes(ax):
        ax.grid(True)
        ax.set_xlabel('Angle In Rad')
        ax.axhline(y=0, color='k')
        ax.axvline(x=0, color='k')

    def SignalSummer(sin, cos, time, SineList=[], CosineList=[], SummatedSignal=[]):
        SignalView(sin, cos, time)
        SineList.append(sin)
        CosineList.append(cos)
        SummatedSignal.append(sin + cos)
        SignalPlotter(SummatedSignal, time)
        return SineList, CosineList, SummatedSignal

    def SignalPlotter(SummatedSignal, time):
        ax.cla()
        try:
            ax.plot(time, sum(SummatedSignal))
        except:
            sg.popup('You Deleted All The Signals!')
        ax.set_title('Summation Signal')
        prepareaxes(ax)
        fig_agg.draw_idle()

    def SignalView(sin, cos, time):
        # ax2 is a List Of Axes ax2[0] is the top right & ax2[1] is the bottom right,
        # ax is general name for axes in matplotlib
        ax2[0].cla()
        ax2[1].cla()
        ax2[0].plot(time, sin, color='red')
        ax2[0].set_title('Sine Wave')
        ax2[1].plot(time, cos, color='green')
        ax2[1].set_title('Cosine Wave')
        prepareaxes(ax2[0])
        prepareaxes(ax2[1])
        # Draw On Canvas
        fig_agg2.draw_idle()

    def SignalDelete(SineList, CosineList, SummatedList):
        if values['delsignal'] == 'Sine':
            try:
                SineList.pop(values['delsignal2'])
            except:
                sg.popup('You Already Removed This Component!')
            try:
                SummatedList[values['delsignal2']] = CosineList[values['delsignal2']]
            except:
                SummatedList.pop(values['delsignal2'])
        elif values['delsignal'] == 'Cosine':
            try:
                CosineList.pop(values['delsignal2'])
            except:
                sg.popup('You Already Removed This Component!')
            try:
                SummatedList[values['delsignal2']] = SineList[values['delsignal2']]
            except:
                SummatedList.pop(values['delsignal2'])
        elif values['delsignal'] == 'Both':
            try:
                SineList.pop(values['delsignal2'])
                CosineList.pop(values['delsignal2'])
                SummatedList.pop(values['delsignal2'])
            except Exception as e:
                sg.popup('You Already Removed This Component!')

    def savedata(sin, cos, time):
        with open('SignalDATA.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Time', 'Summated Signal'])
            for i in range(len(time)):
                writer.writerow([time[i], sum(sin)[i] + sum(cos)[i]])

    while True:
        event, values = window.read(timeout=10)
        if event in (sg.WIN_CLOSED, None):
            break
        if event == 'Set Changes!':
            sine, cosine, timef = preparesignals()
            SineList, CosineList, SumList = SignalSummer(sine, cosine, timef)
            window['delsignal2'].update(values=[i for i in range(len(SumList))])
        if event == 'Delete Signal':
            SignalDelete(SineList, CosineList, SumList)
            window['delsignal2'].update(values=[i for i in range(len(SumList))])
        if event == 'Save Data':
            savedata(SineList, CosineList, timef)
        if event == 'Plot Changes':
            SignalPlotter(SumList, timef)
        if event == 'Event':
            window['pane'].expand(True, True)
            window['-CANVAS-'].expand(True, True)
            window['-CANVAS2-'].expand(True, True)
        if event in EventList:
            plotrealtime()

    window.close()


if __name__ == '__main__':
    main()
