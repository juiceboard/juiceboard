import time
import sys
import dash
import dash_table as dt
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State

from database_helper import *
from visualizer_helper import *
    
# Session config
if ((len(sys.argv) == 2) and (sys.argv[1] == 'local')):
    print("Running JuiceBoard locally...")
    DATABASE_HOST = '127.0.0.1'
    SERVER_HOST = '127.0.0.1'
    SERVER_PORT = '5000'
    DEBUG = True
else:
    DATABASE_HOST = 'juiceboard-db'
    SERVER_HOST = '0.0.0.0'
    SERVER_PORT = '5000'
    DEBUG = False

DATABASE_PORT = '5432'

COLORS = {'back_dark': '#062F39','orange':'#fc8803','light_orange':'#ffc26e'}

DEFAULT_DATA_STYLE = []

DEFAULT_CELL_STYLE = [
    {'if': {'column_id': 'push_id'},'width': '7%','maxWidth':0,'textOverflow':'ellipsis','text-align':'center'},
    {'if': {'column_id': 'user_author'},'width': '10%','maxWidth':0,'textOverflow':'ellipsis','text-align':'left'},
    {'if': {'column_id': 'submit_time'},'width': '15%','maxWidth':0,'textOverflow':'ellipsis','text-align':'center'},
    {'if': {'column_id': 'suite'},'width': '10%','maxWidth':0,'textOverflow':'ellipsis','text-align':'center'},
    {'if': {'column_id': 'decision_result'},'width':'8%','minWidth':'75px','maxWidth':'75px','text-align':'right','overflow':'hidden'},
]

DEFAULT_RIGHT_MENU = html.Div(id='features',children=[html.H2('Select Features')])

FEEDBACK_OPTIONS = [
    {'label': 'None', 'value': 'none'},
    {'label': 'Regular', 'value': 'regular'},
    {'label': 'Intermittent', 'value': 'intermittent'},
]

app = dash.Dash(__name__)
application = app.server

def juiceboard_init(app,vz,db):
    #while db.connect() == False:
    #    print("Waiting to connect to database...")
    #    time.sleep(2)
    db.connect()

    app.layout = html.Div(
        id='app-container',
        children=[
            # Banner
            html.Div(
                id='banner',
                className='banner',
                children=[html.H1('JuiceBoard')],
            ),
            html.A("dummy", id='dummy-for-javascript-callback', hidden=True, href="http://"),
            # Left Column
            html.Div(
                id='left-column',
                className='column',
                children=[
                    dt.DataTable(
                        id='data-table',
                        data=db.get_jobs_list(),
                        columns=[
                            {'name':'Push ID','id':'push_id'},
                            {'name':'User','id':'user_author'},
                            {'name':'Date','id':'submit_time'},
                            {'name':'Test Suite','id':'suite'},
                            {'name':'Result','id':'decision_result','type':'text', 'presentation':'markdown'},
                        ],
                        fixed_rows = {'headers':True},
                        style_as_list_view = True,
                        sort_action = 'native',
                        filter_action='custom',
                        virtualization = True,
                        page_action='none',
                        tooltip_conditional = [],
                        style_header = {'font-family':'Arial','color': '#FF602B','font-size':'1.4rem','text-align':'center','whiteSpace':'normal'},
                        style_data = {'font-family':'Arial','font-size':'1.2rem','height':'5vh',},
                        style_cell_conditional=DEFAULT_CELL_STYLE,
                        style_table = {'display':'flex','maxHeight':'96vh','height':'96vh'},
                    ),
                ],
            ),
            # Right column
            html.Div(
                id='right-column',
                className='column',
                children=[
                    html.Div(id='main-plot',children=[]),
                    html.Div(id='right-menu',
                        children=[
                            html.Div(id='choose-axis',style={'display':'none'},
                                children=[
                                    html.H2('Select Features'),
                                    dcc.Dropdown(id='plot_choose_axis_x',
                                        options=AXIS_OPTIONS,
                                        value='runtime',
                                        clearable=False,
                                        searchable=False,
                                    ),
                                    dcc.Dropdown(id='plot_choose_axis_y',
                                        options=AXIS_OPTIONS,
                                        value='public.job_runs.cpu_load',
                                        clearable=False,
                                        searchable=False,
                                    ),
                                ]
                            ),
                            html.Div(id='feedback-menu',
                                children=[
                                    html.H2('Feedback'),
                                    dcc.Dropdown(id='choose-feedback',
                                        options=FEEDBACK_OPTIONS,
                                        value='none',
                                        clearable=False,
                                        searchable=False,
                                    ),
                                    dcc.Textarea(
                                        id='feedback-text',
                                        placeholder='Comments...',
                                        draggable=False,
                                        maxLength=200,
                                        contentEditable=False,
                                    ),
                                    html.Button(
                                        'Submit',
                                        id='submit-button',
                                    ),
                                ],
                                style={'display':'none'},
                            ),
                        ]
                    ),
                    html.Div(id='force-plot-div',
                        children=[],
                    ),
                    html.Div(id='file-div',
                        children=[
                            html.H2('Files', id='file-title',hidden=True),
                            html.Div(id='file-list',children=[]),
                        ],
                    ),

                ],
            ),
        ],
    )
    app.clientside_callback(
        '''
        function() {
            if(typeof MY_LOG_NR_CALLS_JUICEBOARD_DATATABLE == 'undefined'){
                MY_LOG_NR_CALLS_JUICEBOARD_DATATABLE=true
                //document.getElementsByClassName("dash-filter column-2")[0].innerHTML+='<button>From</button>'
                //document.getElementById("123_picker_edit").setAttribute("style","margin-left:35px")
                document.getElementsByClassName("dash-filter column-2")[0].children[0].setAttribute("style","display:none");
                document.getElementsByClassName("dash-filter column-2")[0].setAttribute("style","display:none")
                var original_edit=document.getElementsByClassName("dash-filter column-2")[0].children[0];
                var input_elements=document.getElementsByClassName("cell cell-0-1 dash-fixed-row")[0].children[0].children[0].children[1];
                var before_table=input_elements.children[2];
                var after_table=input_elements.children[1];
                var btn_get_next_value=function(btn_value){
                if (typeof btn_value == 'undefined'){
                    return 'From';
                }else if(btn_value=='From'){
                    return 'To';
                }else if(btn_value=='To'){
                    return 'Reset';
                }else if(btn_value=='Reset'){
                    return 'From';
                }
                return '';
                }
                var dispatch_datatable_column_change=function(setvalue,input_element,original_edit){
                    original_edit.setAttribute("value",setvalue);
                    var nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
                    nativeInputValueSetter.call(input_element, setvalue);
                    var ev2 = new Event('input', { bubbles: true});
                    input_element.dispatchEvent(ev2);//simulates a keydown event
                    var ke = new KeyboardEvent("keydown", {bubbles: true, cancelable: true, keyCode: 13});
                    input_element.dispatchEvent(ke);
                }
                var insert_button=document.createElement("button");
                var datepicker_id="12346743_id_datepicker";
                var dummy_id="1sdasd2346743_er";
                insert_button.innerHTML=btn_get_next_value();
                insert_button.onclick=function(evt){
                    btn=evt.target
                    setvalue='';
                    var dispatch=false;
                    if(btn.innerHTML=='From'){
                        document.getElementById(dummy_id).setAttribute("value",document.getElementById(datepicker_id).value);
                    }else if(btn.innerHTML=='To'){
                        setvalue="DATEFORMAT:"+document.getElementById(dummy_id).getAttribute("value")+";;;;"+document.getElementById(datepicker_id).value
                        dispatch=true;
                    }else if(btn.innerHTML=='Reset'){
                        setvalue="";
                        dispatch=true;
                    }
                    //now dispatch
                    if(dispatch){
                        dispatch_datatable_column_change(setvalue,document.getElementsByClassName("dash-filter column-2")[0].children[0],original_edit);
                    }
                    document.getElementById(datepicker_id).value="";//Reset
                    btn.innerHTML=btn_get_next_value(btn.innerHTML);
                }
                var insert_date=document.createElement("input");
                insert_date.setAttribute("type","date");
                insert_date.setAttribute("id",datepicker_id);
                var insert_dummy=document.createElement("input");
                insert_dummy.setAttribute("type","text");
                insert_dummy.setAttribute("id",dummy_id);
                insert_dummy.setAttribute("style","display:none");
                input_elements.insertBefore(insert_button,before_table);
                input_elements.insertBefore(insert_date,before_table);
                input_elements.insertBefore(insert_dummy,before_table);

                //this section focuses on the decision_result column only
                document.getElementsByClassName("dash-filter column-4")[0].setAttribute("style","display:none")
                var original_edit=document.getElementsByClassName("dash-filter column-4")[0].children[0];
                original_edit.setAttribute("style","display:none");
                decision_values=["All","Regular","Intermittent"];
                decision_opt=[""," regular_failure"," intermittent_failure"];
                var dropdown=document.createElement("select");
                for(var i=0;i<decision_values.length;i++){
                    val=decision_values[i];
                    var opt=document.createElement("option");
                    opt.value=decision_opt[i];
                    opt.innerHTML=val;
                    dropdown.appendChild(opt);
                }
                dropdown.onchange=function(){
                    dispatch_datatable_column_change(this.value,document.getElementsByClassName("dash-filter column-4")[0].children[0],original_edit);
                }
                input_elements.insertBefore(dropdown,input_elements.children[7]);
            }
            return ('https://');
        }
        '''
        ,Output('dummy-for-javascript-callback','href'),
        [Input('data-table', 'filter_query')]
    )
    # Server side query callback
    @app.callback(
        Output('data-table', 'data'),
        [Input('data-table', 'filter_query'),
        Input('submit-button', 'n_clicks')],)

    def update_table(filter, n_clicks):

        data_values=[]
        update=False
        if(filter!=None and len(filter)>1 and filter[0]=='{'):
            currentelem=1
            global_Column_ids=[]
            global_Column_values=[]

            multiple_elements=True
            while multiple_elements==True:
                column_id_buffer = []
                while(filter[currentelem]!='}'):#TODO:could lead to an infinite loop an bad input
                    column_id_buffer.append(filter[currentelem])
                    currentelem=currentelem+1
                column_id=''.join(column_id_buffer)
                #TODO:check if column_id exists
                if(len(filter)>(currentelem+2)):
                    currentelem=currentelem+2
                    op_buffer = []
                    while (filter[currentelem] != ' '):  # TODO:could lead to an infinite loop an bad input
                        op_buffer.append(filter[currentelem])
                        currentelem = currentelem + 1
                    operation=''.join(op_buffer)
                    currentelem=currentelem+1
                    if(operation=='contains'):
                        pending_value_buffer=[]
                        value_buffer=[]
                        backup_current_element=currentelem
                        delimiter=" "
                        if(currentelem<len(filter) and filter[currentelem]=='"'):
                            delimiter='"'
                            backup_current_element=backup_current_element+1
                            currentelem=currentelem+1
                        while(backup_current_element<len(filter) and  filter[backup_current_element]!=delimiter ):#just probe
                            pending_value_buffer.append(filter[backup_current_element])
                            backup_current_element=backup_current_element+1
                        #after probing determine right size
                        #check if at the end
                        if(backup_current_element==len(filter)):
                            #copy to value buffer
                            while (currentelem < backup_current_element):
                                value_buffer.append(filter[currentelem])
                                currentelem=currentelem+1
                        elif filter[backup_current_element]==delimiter:
                            while (currentelem < backup_current_element):
                                value_buffer.append(filter[currentelem])
                                currentelem=currentelem+1
                            currentelem=currentelem+1

                        if(currentelem<len(filter))and(filter[currentelem]=='&')and((currentelem+1)<len(filter)) and (filter[currentelem+1]=='&'):
                            #there are multiple elements
                            multiple_elements=True
                            currentelem=currentelem+4
                            #value_buffer.pop()#because overestimates by 1 in the previous while loop
                            if not((currentelem+4)<len(filter)):
                                multiple_elements=False

                        else:
                            multiple_elements=False

                        value=''.join(value_buffer)
                        update=True
                        checkstr_dateformat="DATEFORMAT:"
                        if(column_id=='submit_time' and value.find(checkstr_dateformat)==0):
                            value=value[len(checkstr_dateformat):]
                            value=value.split(";;;;")

                        if(column_id=='decision_result' and value[0]!=" "):
                            value=" "+value
                        global_Column_ids.append(column_id)
                        global_Column_values.append(value)
                    else:
                        break
            data_values = db.filter_jobs_list_contains(global_Column_ids, global_Column_values)
        if(len(data_values)==0 and not update):
            data_values=db.get_jobs_list()

        return data_values

    # Main app callback, multiple inputs, multiple outputs
    @app.callback(
        [
            Output('data-table','style_data_conditional'),
            Output('main-plot','children'),
            Output('file-list', 'children'),
            Output('file-title', 'hidden'),
            Output('choose-axis','style'),
            Output('feedback-menu','style'),
            Output('choose-feedback','value'),
            Output('feedback-text','value'),
            Output('force-plot-div', 'children')
        ],
        [
            Input('data-table', 'active_cell'),
            Input('plot_choose_axis_x', 'value'),
            Input('plot_choose_axis_y', 'value'),
        ]
    )
    def update_all(active_cell,choose_x_axis,choose_y_axis):
        if(not (active_cell == None)):
            job_id = active_cell['row_id']
            rowindx = active_cell['row']
            label, text = db.feedback_query(job_id)
            return [
                [
                    {'if': {'row_index': rowindx}, 'background-color':COLORS['light_orange']},
                ],
                vz.get_main_plot(db.get_plot_data(choose_x_axis,choose_y_axis),[job_id],choose_x_axis,choose_y_axis),
                db.get_file_list(job_id),
                False,
                {'display':'inline'},
                {'display':'inline'},
                label,
                text,
                vz.get_force_plot(db.get_shap_data(job_id)),
            ]
        else:
            # Output in order of callback args
            return [DEFAULT_DATA_STYLE,vz.get_summary_plots(db.get_jobs_list()),[],True,{'display':'none'},{'display':'none'},'none','',[]]

    # Feedback callback
    @app.callback(
    [
        Output('choose-feedback', 'searchable')],
    [
        Input('submit-button','n_clicks'),
    ],
    state=[
        State('data-table', 'active_cell'),
        State('choose-feedback','value'),
        State('feedback-text','value'),
    ])
    def update_feedback(clicks, active_cell, type, text):
        if(not (active_cell == None)):
            job_id = active_cell['row_id']
            db.submit_feedback(job_id, type, text)
        return [False]

    return {'update_feedback':update_feedback,'update_table':update_table,'update_all':update_all}

db = Database_Helper(DATABASE_HOST, DATABASE_PORT)
vz = Visualizer_Helper()
app.title = 'JuiceBoard'
exported_functions=juiceboard_init(app,vz,db)
    
if __name__ == '__main__':

    app.run_server(host=SERVER_HOST,port=SERVER_PORT,debug=DEBUG)
