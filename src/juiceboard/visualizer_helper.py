import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objs as go
import copy
import shap
import matplotlib.pyplot as plt
import pandas as pd

MAIN_PLOT_STRUCTURE = [
    {
        'x': [],
        'y': [],
        'name': 'Intermittent',
        'mode': 'markers',
        'marker': {'size': 12, 'color': '#ff8000', 'opacity': '0.8' } # Orange
    },
    {
        'x': [],
        'y':[],
        'name': 'Regular',
        'mode': 'markers',
        'marker': {'size': 12, 'color': '#006eff', 'opacity': '0.8' } # Blue
    },
    {
        'x': [],
        'y': [],
        'name': 'Selected',
        'mode': 'markers',
        'marker': {'size': 12, 'color': '#000000', 'line': {'width': 3, 'color': '#000000'},} # Black
    }
]

AXIS_OPTIONS = [
    {'label': 'Runtime (sec)', 'value': 'runtime'},
    {'label': 'CPU Load (%)', 'value':  'public.job_runs.cpu_load'},
    {'label': 'Linux32', 'value': 'cat:system:linux32'},
    {'label': 'Linux32 Stylo Disabled', 'value': 'cat:system:linux32-stylo-disabled'},
    {'label': 'Linux 64', 'value': 'cat:system:linux64'},
    {'label': 'Linux 64 Qr', 'value': 'cat:system:linux64-qr'},
    {'label': 'Linux 64 Stylo Disabled', 'value': 'cat:system:linux64-stylo-disabled'},
    {'label': 'OS X 10.10', 'value': 'cat:system:osx-10-10'},
    {'label': 'Windows 10 64', 'value': 'cat:system:windows10-64'},
    {'label': 'Windows 7 32', 'value': 'cat:system:windows7-32'},
    {'label': 'Profile-Guided Optimization', 'value': 'cat:platform_option:pgo'},
    {'label': 'Platform Opt', 'value': 'cat:platform_option:opt'},
    {'label': 'Platform Debug', 'value': 'cat:platform_option:debug'},
    {'label': 'Address Sanitizer', 'value': 'cat:platform_option:asan'},
    {'label': 'Decision Runtime', 'value': 'run_time'},
    {'label': 'Decision CPU Load', 'value': 'public.decisions.cpu_load'},

    {'label': 'Suite', 'value': 'suite'},
    {'label': 'Platform', 'value': 'platform'},
    {'label': 'job_type_name', 'value': 'job_type_name'},
    {'label': 'submitted_by', 'value': 'submitted_by'},
]

class Visualizer_Helper():
    def __init__(self):
        pass    
        
    def get_option_label(self,option):
        ret=None
        for x in AXIS_OPTIONS:
            if x['value']==option:
                ret=x['label']
                break
        return ret

    def get_summary_plots(self, data):

        plots = [html.H2('Failure Summary')]
        results_data = {}

        for row in data:
            if(results_data.get(row['suite']) == None):
                results_data[row['suite']] = {'Intermittent':{'Date':[],'Count':[]}, 'Regular':{'Date':[],'Count':[]}}
            date = '{0}'.format(row['submit_time'].date())
            if 'intermittent_failure' in  row['decision_result']:
                if date in results_data[row['suite']]['Intermittent']['Date']:
                    indx = results_data[row['suite']]['Intermittent']['Date'].index(date)
                    results_data[row['suite']]['Intermittent']['Count'][indx] += 1
                else:
                    results_data[row['suite']]['Intermittent']['Date'].append(date)
                    results_data[row['suite']]['Intermittent']['Count'].append(1)
            else:
                if date in results_data[row['suite']]['Regular']['Date']:
                    indx = results_data[row['suite']]['Regular']['Date'].index(date)
                    results_data[row['suite']]['Regular']['Count'][indx] += 1
                else:
                    results_data[row['suite']]['Regular']['Date'].append(date)
                    results_data[row['suite']]['Regular']['Count'].append(1)
        
        for suite in results_data:

            data_sorted = sorted(zip(results_data[suite]['Intermittent']['Date'],results_data[suite]['Intermittent']['Count']))
            results_data[suite]['Intermittent']['Date'] = [date for date,_ in data_sorted]
            results_data[suite]['Intermittent']['Count'] = [count for _,count in data_sorted]
            max_y = max(results_data[suite]['Intermittent']['Count'])
            df = pd.DataFrame(data=results_data[suite]['Intermittent'])
            intermittent = go.Scatter(
                x = df.Date,
                y = df['Count'],
                name = "Intermittent",
                mode='lines+markers',
                marker = {'size': 8, 'color': '#ff8000', 'opacity': 0.8 }, # Orange
                line = {'color':'#ff8000'},
            )

            data_sorted = sorted(zip(results_data[suite]['Regular']['Date'],results_data[suite]['Regular']['Count']))
            results_data[suite]['Regular']['Date'] = [date for date,_ in data_sorted]
            results_data[suite]['Regular']['Count'] = [count for _,count in data_sorted]
            max_y = max([max_y, max(results_data[suite]['Regular']['Count'])])
            df = pd.DataFrame(data=results_data[suite]['Regular'])
            regular = go.Scatter(
                x = df.Date,
                y = df['Count'],
                name = "Regular",
                mode='lines+markers',
                marker= {'size': 8, 'color': '#006eff', 'opacity': 0.8 }, # Blue
                line = {'color':'#006eff'},
            )
            plot = dcc.Graph(id='{0}_plot'.format(suite), 
                className = 'summary-plot',
                figure = {
                    'data': [intermittent, regular],
                    'layout': {
                        'title':'Test suite: {0}'.format(suite),
                        'titlefont': {'family':'Arial', 'size':18},
                        'xaxis': {
                            'rangeselector': {'buttons': [
                                {'count':1,'label':'1d','step':'day','stepmode':'backward'},
                                {'count':7,'label':'1w','step':'day','stepmode':'backward'},
                                {'count':1,'label':'1m','step':'month','stepmode':'backward'},
                                {'count':6,'label':'6m','step':'month','stepmode':'backward'},
                                {'step':'all'}]},
                            'rangeslider':{},
                            'type': 'date',
                            'tickfont': {'size':14,'family':'Arial'},
                        },
                        'yaxis': {
                            'title':'Failures',
                            'range':[-1,max_y+1],
                            'zeroline': False,
                            'tickfont': {'size':14,'family':'Arial'},
                            'titlefont': {'size':14,'family':'Arial'},
                        },
                    },
                },
            )
            plots.append(plot)
        return plots
        
    def get_main_plot(self, data, selected, x_label, y_label):  #selected is an id which must be present in both decisions and job_runs table
        
        plot_data = copy.deepcopy(MAIN_PLOT_STRUCTURE)
        plot = []
        for job in data:
            res=dict(job)
            apppendkey=-1

            if x_label=='runtime':
                res['x']=res['x'].total_seconds()
            if y_label=='runtime':
                res['y']=res['y'].total_seconds()

            if(res['id'] in selected):
                appendkey=2
                if(res['decision_result']==" intermittent_failure"):
                    color = '#ff8000'
                    line_color = '#111111'
                else:
                    color = '#006eff'
                    line_color = '#111111'
                # Change formatting
                plot_data[appendkey]['marker']['color'] = color
                plot_data[appendkey]['marker']['line']['color'] = line_color
            elif(res['decision_result']==" intermittent_failure"):
                appendkey=0
            else:
                appendkey=1

            plot_data[appendkey]['x'].append(res['x'])
            plot_data[appendkey]['y'].append(res['y'])

            plot = dcc.Graph(
                id='plot',
                figure={
                    'data': plot_data,
                    'layout': {
                        'title':'{0} vs. {1}'.format(self.get_option_label(x_label), self.get_option_label(y_label)),
                        'clickmode': 'event+select',
                        'xaxis':{'title':self.get_option_label(x_label)},
                        'yaxis':{'title':self.get_option_label(y_label)},
                    },
                }
            )
        return [plot]
       
    def get_force_plot(self, data):
        shap.initjs()
        for job in data:
            res = dict(job)
            key = -1
            if res['result'] == " intermittent_failure":
                key = 0
            else:
                key = 1
            pto_sh = res['asan'] + res['debug'] + res['opt'] + res['pgo']
            pt_sh =res['l32'] + res['l32sd'] + res['l64'] + res['l64qr'] + res['l64sd'] + res['o10'] + res['w1064'] + res['w732']
            SHAPS = [[key,res['rt_sh'],res['cl_sh'],pto_sh,pt_sh,res['rt'],res['cl'],1,1]]
        df = pd.DataFrame(SHAPS, columns=['result','rt_sh','cl_sh','pto_sh','pt_sh','rt','cl','pto','pt'])
        Y = df['result']
        X = df[['rt_sh','cl_sh','pto_sh','pt_sh']]
        X_test = df[['rt','cl','pto','pt']]
        html_body=shap.force_plot(Y.to_numpy(), X.to_numpy(), X_test.to_numpy(), feature_names= ['run_time','cpu_load','platform_option','platform'], show=False).data
        return [html.H2('SHAP Force Plot'),html.Iframe(id='force-plot',srcDoc="<script src='assets/bundle.js'></script>"+html_body)]
