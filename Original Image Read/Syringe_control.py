import PySimpleGUI as sg
########################### Syringe control windows ###################################
############################## IVA PART ################################
def syringe_operation(syringecontrols):
    '''Here will be the code operating the syringe, taking the flowrate and volume/duration desired'''
    # here #
    if syringecontrols == []:
        return ('None',0,0,0,0,0)
    else:
        controltype,syringeno,flowrate,control,flowrate_units,control_units = syringecontrols
    print(f'Type: {controltype}, Syringe number: {syringeno}, Flow rate: {flowrate}{flowrate_units}, Control: {control}{control_units}')
    return (controltype,syringeno,flowrate,control,flowrate_units,control_units)
############################# END OF IVA PART ######################
def syringewindow1():
    layout = [
        [sg.Text('Do you want to use volume or duration control?')],
        [sg.Button('Volume', size=(8, 2)),sg.Button('Duration', size=(8, 2))],
        [sg.Button('Cancel', size=(8, 2))]
    ]
    syringewindow1 = sg.Window('Control type',layout,size=(600,400))
    while True:
        event, values = syringewindow1.read()
        if event == 'Cancel': #sg.WIN_CLOSED or 'Cancel':
            con_type = []
            break
        elif event=='Volume':
            con_type = ['Volume',['µL', 'mL', 'L']]
            break
        elif event=='Duration':
            con_type = ['Duration',['minutes','hours']]
            break
    syringewindow1.close()
    return con_type
def syringewindow2(type,measure_units):
    flowrate_units = ['µL/min', 'mL/min', 'µL/hr', 'mL/hr']
    layout = [
        [sg.Text(f'You have chosen {type} control')],
        [[sg.Text('Syringe number:')],[sg.Input('',size=(10, 4),key='-Syringe no-')]],
        [[sg.Text('Flow rate:')],[sg.Input('',size=(10, 4),key='-Flow rate-'),sg.Combo(flowrate_units, font=('Arial Bold', 12),key='-Flowrate units-')]],#sg.Text('L/min')]],
        [[sg.Text(f'{type}:')],[sg.Input('', size=(10, 4),key ='-Control-'),sg.Combo(measure_units, font=('Arial Bold', 12),key='-Control units-')]],
        [sg.Button('Cancel', size=(8, 2)),sg.Button('Confirm',size=(8,2))]
    ]
    syringewindow2= sg.Window(f'Flow rate and {type} control',layout,size=(600,400))
    while True:
        event, values = syringewindow2.read()
        if event == 'Cancel':
            userinput = []  
            break
        elif event in ('Confirm'):
            userinput = [type,int(values['-Syringe no-']),float(values['-Flow rate-']),float(values['-Control-']),str(values['-Flowrate units-']),str(values['-Control units-'])]
            break
    syringewindow2.close()
    return userinput
