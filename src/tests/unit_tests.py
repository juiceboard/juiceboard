# Unit tests for the Juiceboard app using the python unittest framework

import sys

# Change working dir to juiceboard src folder
sys.path.append("..\\juiceboard\\")

import unittest
import subprocess
import dash

# Source modules
from database_helper import *
from visualizer_helper import *
from juiceboard import *

TEST_ID_INT = 170841655
TEST_ID_REG = 168754280
TEST_FEEDBACK_NONE = 171948923
TEST_DATABASE_IP = '127.0.0.1'
BAD_IP = '0.0.0.1'
PORT = '5432'
BAD_PORT = '11111'

class TestDatabase(unittest.TestCase):

    def test_connection(self):
        try:
            db = Database_Helper(BAD_IP, BAD_PORT)
            self.assertFalse(db.connect())
            db = Database_Helper(TEST_DATABASE_IP, PORT)
            self.assertTrue(db.connect())
            db.close()
        except Exception as e:
            print('TestDatabase.test_connection ',e)
            raise e
            return
        print('TestDatabase.test_connection,\t\t\t\tPass')

    def test_decisions_job_runs_table(self):
        try:
            db = Database_Helper(TEST_DATABASE_IP, PORT)
            db.connect()
            result = db.connection.execute(JOB_QUERY)
            self.assertIsNotNone(result)
            db.close()
        except Exception as e:
            print('TestDatabase.test_decisions_job_runs_table ',e)
            raise e
            return
        print('TestDatabase.test_decisions_job_runs_table,\t\tPass')

    def test_relevant_files_table(self):
        try:
            db = Database_Helper(TEST_DATABASE_IP, PORT)
            db.connect()
            result = db.connection.execute(FILE_QUERY,TEST_ID_INT)
            self.assertIsNotNone(result)
            db.close()
        except Exception as e:
            print('TestDatabase.test_relevant_files_table ',e)
            return
        print('TestDatabase.test_relevant_files_table,\t\tPass')

class TestDatabaseHelper(unittest.TestCase):

    def test_connect(self):
        try: 
            db = Database_Helper(BAD_IP, BAD_PORT)
            self.assertFalse(db.connect())
            db = Database_Helper(TEST_DATABASE_IP, PORT)
            self.assertTrue(db.connect())
            db.close()
        except Exception as e:
            print('TestDatabaseHelper.test_connect ', e)
            raise e
            return
        print('TestDatabaseHelper.test_connect,\t\t\tPass')

    def test_get_jobs_list(self):
        try:
            db = Database_Helper(TEST_DATABASE_IP, PORT)
            db.connect()
            job_list = db.get_jobs_list()
        except Exception as e:
            print('TestDatabaseHelper.test_get_jobs_list ', e)
            raise e
            return
        self.assertTrue(type(job_list)) == list
        self.assertTrue(len(job_list) > 0)
        db.close()
        print('TestDatabaseHelper.test_get_jobs_list,\t\t\tPass')

    def test_get_file_list(self):
        try:
            db = Database_Helper(TEST_DATABASE_IP, PORT)
            db.connect()
            file_list = db.get_file_list(TEST_ID_INT)
        except Exception as e:
            print('TestDatabaseHelper.test_get_file_list', e)
            raise e
            return
        self.assertTrue(type(file_list)) == list
        self.assertTrue(len(file_list) > 0)
        db.close()
        print('TestDatabaseHelper.test_get_file_list,\t\t\tPass')

    def test_get_plot_data(self):
        try:
            db = Database_Helper(TEST_DATABASE_IP, PORT)
            db.connect()
            plot_data = db.get_plot_data('runtime','public.job_runs.cpu_load')
            plot_data = db.get_plot_data('runtime','runtime')
            plot_data = db.get_plot_data('cat:platform_option:debug','cat:platform_option:debug')
        except Exception as e:
            print('TestDatabaseHelper.test_get_plot_data ', e)
            raise e
            return
        self.assertIsNotNone(plot_data)
        db.close()
        print('TestDatabaseHelper.test_get_plot_data,\t\t\tPass')

    def test_feedback_query(self):
        try:
            db = Database_Helper(TEST_DATABASE_IP, PORT)
            db.connect()
            result = db.feedback_query(None)
            result = db.feedback_query(TEST_FEEDBACK_NONE)
            result = db.feedback_query(TEST_ID_INT)
        except Exception as e:
            print('TestDatabaseHelper.test_feedback_query ', e)
            raise e
            return
        self.assertIsNotNone(result)
        db.close()
        print('TestDatabaseHelper.test_feedback_query,\t\tPass')

    def test_submit_feedback(self):
        try:
            db = Database_Helper(TEST_DATABASE_IP, PORT)
            db.connect()
            result = db.submit_feedback(TEST_ID_INT, 'none', '')
            result = db.submit_feedback(TEST_ID_INT, 'none', None)
        except Exception as e:
            print('TestDatabaseHelper.test_submit_feedback ', e)
            raise e
            return
        db.close()
        print('TestDatabaseHelper.test_submit_feedback,\t\tPass')

    def test_filter_jobs_list_contains(self):
        try:
            db = Database_Helper(TEST_DATABASE_IP, PORT)
            db.connect()
            result = db.filter_jobs_list_contains(['push_id'], ['32'])
            self.assertNotEqual(result, [])
            result = db.filter_jobs_list_contains(['submit_time'], [['','']])
            self.assertIsNotNone(result, [])
        except Exception as e:
            print('TestDatabaseHelper.test_filter_jobs_list_contains ', e)
            raise e
            return
        db.close()
        print('TestDatabaseHelper.test_filter_jobs_list_contains,\tPass')

class TestVisualizerHelper(unittest.TestCase):

    def test_get_option_label(self):
        try:
            vz = Visualizer_Helper()
            label = vz.get_option_label('runtime')
        except Exception as e:
            print('TestVisualizerHelper.test_get_option_label', e)
            raise e
            return
        self.assertIsNotNone(label)
        print('TestVisualizerHelper.test_get_option_label,\t\tPass')
        
    def test_get_main_plot(self):
        try:
            db = Database_Helper(TEST_DATABASE_IP, PORT)
            db.connect()
            vz = Visualizer_Helper()
            plot_data = db.get_plot_data('runtime', 'public.job_runs.cpu_load')
            plot = vz.get_main_plot(plot_data, [TEST_ID_INT], 'runtime', 'public.job_runs.cpu_load')
            self.assertNotEqual(plot, [])
            plot_data = db.get_plot_data('public.job_runs.cpu_load', 'runtime')
            plot = vz.get_main_plot(plot_data, [TEST_ID_REG], 'public.job_runs.cpu_load', 'runtime')
            self.assertNotEqual(plot, [])
        except Exception as e:
            print('TestVisualizerHelper.test_get_main_plot ',e)
            raise e
            return
        db.close()
        print('TestVisualizerHelper.test_get_main_plot,\t\tPass')
        
    def test_get_summary_plots(self):
        try:
            db = Database_Helper(TEST_DATABASE_IP, PORT)
            db.connect()
            vz = Visualizer_Helper()
            plots = vz.get_summary_plots(db.get_jobs_list())
            self.assertNotEqual(plots, [])
        except Exception as e:
            print('TestVisualizerHelper.test_get_summary_plots ',e)
            raise e
            return
        db.close()
        print('TestVisualizerHelper.test_get_summary_plots,\t\tPass')


    def test_get_force_plot(self):
        try:
            db = Database_Helper(TEST_DATABASE_IP, PORT)
            db.connect()
            vz = Visualizer_Helper()

            plot_data = db.get_shap_data(TEST_ID_INT)
            plot = vz.get_force_plot(plot_data)
            self.assertNotEqual(plot, [])

            plot_data = db.get_shap_data(TEST_ID_REG)
            plot = vz.get_force_plot(plot_data)
            self.assertNotEqual(plot, [])
        except Exception as e:
            print('TestVisualizerHelper.test_get_force_plot', e)
            raise e
            return
        print('TestVisualizerHelper.test_get_force_plot,\t\tPass')


class JuiceBoardMockDataBase_ExceptionTest:
    def connect(self):
        return True
    def get_jobs_list(self):
        raise Exception

class MockVisualizer_HelperException:
    def get_main_plot(self, data, selected, x_label, y_label):
        raise Exception()
    def get_force_plot(self, data, app):
        raise Exception()

class MockDataBAseEngineQueryFailCOnnection:
    def execute(self,arg):
        raise Exception("db exception goes through")

class MockDataBaseEngineQueryFail:
    def connect(self):
        return MockDataBAseEngineQueryFailCOnnection()

class MockDataBaseInstantiationFail_Query:
    def create_engine(self,cmd):
        return MockDataBaseEngineQueryFail()

class TestJuiceBoard(unittest.TestCase):
    def test_withstand_data_layout_db_exceptions(self):
        db=Database_Helper('localhost',3434)
        db.sqa=MockDataBaseInstantiationFail_Query()
        WithStand=False
        try:
            juiceboard_init(dash.Dash(__name__), MockVisualizer_HelperException(),db)
        except:
            WithStand=True
        self.assertFalse(WithStand)

    def test_withstand_dbexception_update_table(self):
        db = Database_Helper('localhost', 3434)
        db.sqa = MockDataBaseInstantiationFail_Query()
        WithStand = False
        try:
            exp=juiceboard_init(dash.Dash(__name__), MockVisualizer_HelperException(), db)
            exp['update_table']('{name} contains hello')
        except:
            WithStand = True
        self.assertFalse(WithStand)

    def test_withstand_dbexception_update_all(self):
        db = Database_Helper('localhost', 3434)
        db.sqa = MockDataBaseInstantiationFail_Query()
        WithStand = False
        try:
            exp=juiceboard_init(dash.Dash(__name__), MockVisualizer_HelperException(), db)
            recover= exp['update_all'](None, 'runtime', 'public.job_runs.cpu_load')
            contains=False
            if('display' in recover[3] and 'display' in recover[4] and recover[3]['display']=='none' and recover[3]['display']=='none'):
                contains=True
            self.assertEqual(contains,True)
            exp['update_all']({'row': 1, 'row_id': 1}, 'runtime', 'public.job_runs.cpu_load')
        except:
            WithStand = True
        self.assertFalse(WithStand)

    def test_withstand_dbexception_update_feedback(self):
        db = Database_Helper('localhost', 3434)
        db.sqa = MockDataBaseInstantiationFail_Query()
        WithStand = False
        try:
            exp=juiceboard_init(dash.Dash(__name__), MockVisualizer_HelperException(), db)
            db.id=None
            res=exp['update_feedback']('regular')
            self.assertEqual(res[0],False)
            exp['update_feedback']('regular')
        except:
            WithStand = True
        self.assertFalse(WithStand)

class JuiceBoardMockDataBase_update_table_test:
    job_column_id=[]
    job_column_value=[]
    job_list_called=False
    def connect(self):
        return True
    def is_connected(self):
        return True
    def get_jobs_list(self):
        self.job_list_called=True
        return []
    def filter_jobs_list_contains(self,global_Column_ids, global_Column_values):
        self.job_column_id=global_Column_ids
        self.job_column_value=global_Column_values
        return []
    def feedback_query(self):
        raise Exception
    def get_file_list(self):
        raise Exception
    def get_plot_data(self):
        raise Exception


class TestJuiceBoardFunctions(unittest.TestCase):
    def test_update_table(self):
        db = JuiceBoardMockDataBase_update_table_test()
        exp = juiceboard_init(dash.Dash(__name__), Visualizer_Helper(), db)
        update_table = exp['update_table']
        value1 = 'row_id'
        value2 = 'Value'
        clicks = 0
        update_table('{' + value1 + '} contains ' + value2,clicks)
        self.assertEqual(value1, db.job_column_id[0])
        self.assertEqual(value2, db.job_column_value[0])

        db.job_column_value = []
        db.job_column_id = []
        row_ids = ['ich', '2', 'k']
        row_values = ['abc', 'def', 'ghi']
        update_table(
            '{' + row_ids[0] + '} contains ' + row_values[0] + ' && ' + '{' + row_ids[1] + '} contains ' + row_values[
                1] + ' && {' + row_ids[2] + '} contains ' + row_values[2],clicks)
        self.assertEqual(row_ids[0], db.job_column_id[0])
        self.assertEqual(row_values[0], db.job_column_value[0])
        self.assertEqual(row_ids[1], db.job_column_id[1])
        self.assertEqual(row_values[1], db.job_column_value[1])
        self.assertEqual(row_ids[2], db.job_column_id[2])
        self.assertEqual(row_values[2], db.job_column_value[2])

        db.job_list_called = False
        update_table('{dfs} equals edc',clicks)
        self.assertTrue(db.job_list_called)

        db.job_column_value = []
        db.job_column_id = []
        update_table('{user_author} contains &',clicks)
        self.assertEqual(db.job_column_id[0], 'user_author')
        self.assertEqual(db.job_column_value[0], '&')

        db.job_column_value = []
        db.job_column_id = []
        update_table('{user_author} contains &&',clicks)
        self.assertEqual(db.job_column_id[0], 'user_author')
        self.assertEqual(db.job_column_value[0], '&&')

        db.job_column_value = []
        db.job_column_id = []
        update_table('{user_author} contains "&& a"',clicks)
        self.assertEqual(db.job_column_id[0], 'user_author')
        self.assertEqual(db.job_column_value[0], '&& a')

if __name__ == '__main__':
    print('Starting juiceboard unit tests... Commit prefix: ' + 
          str(subprocess.check_output(['git', 'describe','--always']).strip().decode('utf-8')))
    unittest.main()
