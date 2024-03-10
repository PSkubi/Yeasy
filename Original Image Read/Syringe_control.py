import PySimpleGUI as sg
########################### Syringe control windows ###################################
############################## IVA PART ################################
def syringe_operation(syringecontrols):
    '''Here will be the code operating the syringe, taking the list of controltype,syringeno,flowrate,control,flowrate_units,control_units'''
    # here #
    if syringecontrols == []:
        return ('None',0,0,0,0,0)
    else:
        controltype,syringeno,flowrate,control,flowrate_units,control_units = syringecontrols
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
        if event in (sg.WIN_CLOSED,'Cancel'):
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
def syringewindow2(type,measure_units,syringeno):
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
            if userinput[2] == 0 or userinput[3] == 0:
                sg.popup(f'Flow rate or {type} value cannot be 0')
                continue
            elif int(userinput[2]) < 0 or userinput[3] < 0:
                sg.popup(f'Flow rate or {type} value cannot be negative')
                continue
            elif userinput[1]>syringeno:
                sg.popup(f'Syringe number cannot be higher than {syringeno}')
                continue
            elif userinput[1]<1:
                sg.popup(f'Syringe number cannot be lower than 1')
                continue
            elif userinput[1] == '':
                sg.popup(f'Syringe number was not specified')
                continue
            elif userinput[2] == '':
                sg.popup(f'Flow rate was not specified')
                continue
            elif userinput[3] == '':    
                sg.popup(f'{type} was not specified')
                continue
            elif userinput[4] == '':
                sg.popup(f'Flow rate units were not specified')
                continue
            elif userinput[5] == '':
                sg.popup(f'{type} units were not specified')
                continue
            break
    syringewindow2.close()
    return userinput
