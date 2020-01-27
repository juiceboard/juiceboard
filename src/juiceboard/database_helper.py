import dash_html_components as html
import sqlalchemy as sqa

"""
Design decisions:
Reactive database access - no duplication of database on server side

Required 'decisions' table structure: [['id'],['decision'],['feature_1'],...,['feature_n']]
"""

JOB_QUERY = "SELECT public.decisions.id AS id,decision AS decision_result,push_id,submit_time,submitted_by AS user_author,suite from public.decisions,public.job_runs WHERE public.decisions.id=public.job_runs.id"
FILE_QUERY = "SELECT link from public.relevant_sources Where public.relevant_sources.id=%s;"
MAIN_PLOT_QUERY='SELECT public.decisions.id AS id,decision AS decision_result,{0} AS y,{1} AS x from public.decisions,public.job_runs WHERE public.decisions.id=public.job_runs.id;'
FEEDBACK_QUERY = 'SELECT feedback.feedback AS feedback, feedback.comments as comments from public.feedback WHERE public.feedback.id=%s;'
SEND_FEEDBACK_QUERY = 'INSERT INTO feedback (id, feedback, comments) VALUES (%s, %s, %s) ON CONFLICT (id) DO UPDATE SET feedback=%s, comments=%s;'
FORCE_PLOT_QUERY = 'SELECT de.decision as result, de.run_time AS rt_sh, de.cpu_load AS cl_sh,'\
                    'de.\"cat:platform_option:asan\" as asan, de.\"cat:platform_option:debug\" as debug, de.\"cat:platform_option:opt\" as opt, de.\"cat:platform_option:pgo\" as pgo,'\
                    'de.\"cat:system:linux32\" as l32, de.\"cat:system:windows10-64\" as w1064, de.\"cat:system:linux32-stylo-disabled\" as l32sd, de.\"cat:system:linux64\" as l64,'\
                    'de.\"cat:system:linux64-qr\" as l64qr, de.\"cat:system:linux64-stylo-disabled\" as l64sd, de.\"cat:system:osx-10-10\" as o10, de.\"cat:system:windows7-32\" as w732,'\
                    'th.run_time AS rt, th.cpu_load AS cl from public.decisions as de,public.treeherder as th WHERE de.id=th.id AND th.id=%s;'

class Database_Helper():
    def __init__(self, host, port):
        self.host = host
        self.port = port

        # SQLAlchemy engine
        self.connection = None
        self.engine = None
        self.sqa_e=sqa

    def connect(self):
        try:
            self.engine = self.sqa_e.create_engine('postgresql+psycopg2://postgres:@{0}/?port={1}'.format(self.host, self.port))
            self.connection = self.engine.connect()
            if(self.engine.table_names() == []):
                return False
        except Exception as e:
            return False
        return True
     
    def is_connected(self):
        return not (self.connection == None)
        
    def close(self):
        self.connection.close()
        self.connection = None
        self.engine.dispose()
        self.engine = None

    def substitute_markdown_result(self, job, job_result):
        feedback = self.feedback_query(job['id'])[0]
        if ' intermittent_failure' in job_result:
            if(feedback == 'intermittent'):
                job['decision_result'] = '![ intermittent_failure](assets/intermittent_y.png "Intermittent failure\nFeedback: intermittent")'
            elif(feedback == 'regular'):
                job['decision_result'] = '![ intermittent_failure](assets/intermittent_n.png "Intermittent failure\nFeedback: regular")'
            else:
                job['decision_result'] = '![ intermittent_failure](assets/intermittent.png "Intermittent failure\nFeedback: none")'
        else:
            if(feedback == 'intermittent'):
                job['decision_result'] = '![ regular_failure](assets/regular_n.png "Regular failure\nFeedback: intermittent")'
            elif(feedback == 'regular'):
                job['decision_result'] = '![ regular_failure](assets/regular_y.png "Regular failure\nFeedback: regular")'
            else:
                job['decision_result'] = '![ regular_failure](assets/regular.png "Regular failure\nFeedback: none")'
        return job
         
    def get_jobs_list(self):
        if not self.is_connected():
            return []
        try:
            jobs = self.query_result_list(self.connection.execute(JOB_QUERY))
        except:
            return []
        for job in jobs:
            job_result = job['decision_result']
            job = self.substitute_markdown_result(job, job_result)
        return jobs

    def get_file_list(self,job_id):
        files=[]
        links = []
        try:
            data = result=self.connection.execute(FILE_QUERY,str(job_id))
        except Exception as e:
            return []
        for raw in data:
            for link in raw[0].split(' '):
                files.append(html.A(link, className='hyperlink',href=link.strip()))
        
        return files

    def get_plot_data(self,x='runtime',y='public.job_runs.cpu_load'):
        if ':' in x or '-' in x:
            x='"'+x+'"'
        if ':' in y or '-' in y:
            y='"'+y+'"'
        if x=='runtime':
            x='(end_time - start_time)'
        if y=='runtime':
            y='(end_time - start_time)'
        
        try: 
            result = self.connection.execute(MAIN_PLOT_QUERY.format(y,x))
            return result
        except Exception as e:
            return []

    def feedback_query(self,job_id):
        if job_id == None:
            return 'none', ''
        try:
            response = self.connection.execute(FEEDBACK_QUERY,(str(job_id)))
        except Exception as e:
            return 'none', ''
        feedback = 'none'
        text = ''
        for row in response:
            feedback = row['feedback'].strip()
            text = row['comments']
        return feedback,text

    def submit_feedback(self, job_id, value, text):
        result=[]
        if job_id == None:
            return
        if text == None:
            text = ''
        try:
            response = self.connection.execute(SEND_FEEDBACK_QUERY,(str(job_id),value,text,value,text))
        except Exception as e:
            return
        
    def query_result_list(self,data):
        jobs=[]
        for job in data:
            jobdict=dict(job)
            job_result = jobdict['decision_result']
            jobdict = self.substitute_markdown_result(jobdict, job_result)
            jobs.append(jobdict)
        return jobs

    def filter_jobs_list_contains(self,columns,filter_strings):
        try:
            result = []
            query = 'SELECT * FROM ({0}) AS xpp WHERE '.format(JOB_QUERY)
            for ind, column in enumerate(columns):
                value = filter_strings[ind]
                if(column=='submit_time' and type(value) is list):
                    if not value[0]:
                        value[0] = '2017-01-01'
                    if not value[1]:
                        value[1] = '2020-01-01'
                    query += "{0} >= '{1}' AND {0} <='{2}'".format(column,value[0],value[1])

                else:
                    query += "{0}::varchar(255) LIKE '{1}%%'".format(column,value)
                if not (ind == (len(columns) - 1)):  # last element
                    query += ' AND '
            result = self.connection.execute(query)
        except Exception as e:
            return []
        return self.query_result_list(result)
        
    def get_shap_data(self,job_id):
        try:
            result = self.connection.execute(FORCE_PLOT_QUERY,str(job_id))
            return result
        except Exception as e:
            return []
