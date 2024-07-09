import sqlite3
import logging
import pandas as pd
import numpy as np
import json

#suppressing the settingWithCopyWarning in pandas 
pd.options.mode.chained_assignment = None


logger = logging.basicConfig(filename='./dev/changelog.md', level=logging.DEBUG, 
                             format='[%(asctime)s] %(levelname)s')

logger = logging.getLogger(__name__)

def cleaning_cade_course(cleaned_cade):
    #handling missing values
    no_career = {'career_path_id': 0, 
                'career_path_name': 'no career', 
                'hours_to_complete': 0}
    cleaned_cade.loc[len(cleaned_cade)] = no_career

    return cleaned_cade

# def cleaning_job_df(cade_student_jobs: pd.DataFrame):
#     #dropping duplicates
#     return (cade_student_jobs.drop_duplicates(inplace=True))
def cleaning_job_df(cade_student_jobs):
    #dropping duplicates
    return (cade_student_jobs.drop_duplicates())

def cleaning_cade_students(cleaned_cade):
    #splitting mailing_address to address, city and state
    def extract_contact_info(contact_info):
        try:
            info = json.loads(cleaned_cade['contact_info'].replace("'", "'"))
            return pd.Series([info.get('mailing_address'), info.get('email')])
        except json.JSONDecodeError:
            return pd.Series([None, None])
        cleaned_cade[['mailing_address', 'email']] = cleaned_cade['contact_info'].apply(extract_contact_info)
        split_mailing_address = cleaned_cade.mailing_address.str.split(',', expand=True)
        split_mailing_address.columns = ['address', 'city', 'state', 'zip_code']
        cleaned_cade = pd.concat([cleaned_cade.drop('mailing_address', axis=1), split_mailing_address], axis=1)

    #converting datatypes for dob, job_id, num_course_taken, current_career_path, time_spent_hrs
    cleaned_cade['job_id'] = cleaned_cade['job_id'].astype(float)
    cleaned_cade['num_course_taken'] = cleaned_cade['num_course_taken'].astype(float)
    cleaned_cade['current_career_path_id'] = cleaned_cade['current_career_path_id'].astype(float)
    cleaned_cade['time_spent_hrs'] = cleaned_cade['time_spent_hrs'].astype(float)

    #dropping null values 
    cleaned_cade = cleaned_cade.dropna(subset=['num_course_taken'])
    cleaned_cade = cleaned_cade.dropna(subset=['job_id'])

    #filling in missing values for time_spent_hrs and current_career_path_id
    cleaned_cade['time_spent_hrs'] = np.where(cleaned_cade['time_spent_hrs'].isnull(), 0, cleaned_cade['time_spent_hrs'])
    cleaned_cade['current_career_path_id'] = np.where(cleaned_cade['current_career_path_id'].isnull(), 0, cleaned_cade['current_career_path_id'])

    return cleaned_cade


#ensuring updated database has the same schema as the origional 
def test_schema(cademycode, finally_cleaned_cade):
    errors = 0
    for col in finally_cleaned_cade:
        try:
            if cademycode[col].dtypes != finally_cleaned_cade[col].dtypes:
                errors += 1
        except NameError as NE:
            logger.exception(NE)
            raise next
        
    if errors > 0:
        error_message = str(errors) + ' column(s) dtypes arent the same'
        logger.exception(error_message)
    assert errors == 0, error_message

def test_num_of_columns(cleaned_cade, cademycode):
    try:
        assert len(cleaned_cade) == len(cademycode)
    except AssertionError as AE:
        logging.exception(AE)
        raise AE
    else:
        print('Number of columns are the same')


def test_path_id(cade_students, cadecode_courses):
    """
    Unit test to ensure joined keys exists between student and courses table
    """
    cade_students = cade_students.current_career_path_id.unique()
    cadecode_courses = cadecode_courses.career_path_id.unique()
    is_sub = np.isin(cade_students, cadecode_courses)
    #creating a new variable missing_id that contains the IDs of students who are not in the is_sub subset.
    missing_id = cade_students[~is_sub]
    try:
        assert len(missing_id) == 0, 'Missing current_career_path_id(s): ' + str(list(missing_id))
    except AssertionError as AE:
        logger.exception(AE)
        raise AE
    else:
        print('current_career_path_ids are present')

def test_cade_student_jobs(cade_students, cade_student_jobs):
    """
    Unit test to ensure joined keys exists between students and jobs table
    """
    cade_students = cade_students.job_id.unique()
    cade_student_jobs = cade_student_jobs.job_id.unique()
    is_subset = np.isin(cade_students, cade_student_jobs)
    #creating a new variable missing_id that contains the IDs of students who are not in the is_sub subset.
    missing_id = cade_students[~is_subset]
    try:
        assert len(missing_id) == 0, 'Missing job_id(s): ' + str(list(missing_id))
    except AssertionError as AE:
        logger.exception(AE)
        raise AE
    else:
        print('job_id(s) are present')

def test_null_values(cleaned_cade):
    """
    unit test to ensure rows in cleaned table are not null
    paramaters: cleaned_cade(cleaned data)

    returns: None
    """
    cleaned_cade_missing = cleaned_cade[cleaned_cade.isnull().any(axix=1)]
    missing_count = len(cleaned_cade_missing)
    try:
        assert missing_count == 0, 'There are ' + str(missing_count) + ' nulls in the table'
    except AssertionError as AE:
        logger.exception(AE)
        raise AE
    else:
        print('no null rows found')

def test_num_columns(cleaned_cade, cade_data):
    """
    unit test to ensure number of columns in cleaned dataframe matches the number of columns in SQLite3 database table
    paramaters: cleaned_data(SQLite3 table), cleaned_cade(cleaned data)
    """
    try:
        assert len(cleaned_cade.columns) == len(cade_data.columns)
    except AssertionError as AE:
        logger.exception(AE)
        raise AE
    else:
        print('Same number of columns')

def main():
    #inizializing log
    logger.info('Starting log')

    #checking current version and calculate next version for changelog
    # with open('./dev/changelog.md') as x:
    #     lines = x.readline()
    # next_version = int(lines[0].split('.')[2][0])+1
    with open('./dev/changelog.md') as x:
        first_line = x.readline().strip()
    next_version = int(first_line.split(':')[2][0])+1

    #connect to the dev database and read in the three tables
    con = sqlite3.connect('./dev/cademycode.db')
    students = pd.read_sql_query('SELECT * FROM cademycode_students', con)
    career = pd.read_sql_query('SELECT * FROM cademycode_courses', con)
    student_jobs = pd.read_sql_query('SELECT * FROM cademycode_student_jobs', con)
    con.close()

    #get the current prod table, if exists
    try:
        con = sqlite3.connect('./prod/cleaned_cade.db')
        cleanDB = pd.read_sql_table('SELECT * FROM cleaned_cade', con)
        missingDB = pd.read_sql_query('SELECT * FROM missing_data', con)
        con.close()

        #filtering for students that dont exists in cleaned data
        new_students = students[~np.isin(students.uuid.unique(), cleanDB.uuid.unique())]
    except:
        new_students = students 
        cleanDB = []

        #running cleaning_cade_students function on new students
    clean_new_students = cleaning_cade_students(new_students)
    missing_data = cleaning_cade_students(new_students)

    #updating and inserting new missing data if there is any
    if len(missing_data) > 0:
        sqlite_con = sqlite3.connect('./dev/cleaned_cade.db')
        missing_data.to_sql('missing_data', sqlite_con, if_exists='append', index=False)
        sqlite_con.close()

    #continue only if there is new student data
    if len(clean_new_students) > 0:
        #cleaning tables
        clean_career = cleaning_cade_course(career)
        clean_student_jobs = cleaning_job_df(student_jobs)

    
        ## unit testing before joining ##
        ## making sure required keys are present ##
        test_cade_student_jobs(clean_new_students, clean_student_jobs)
        test_path_id(clean_new_students, clean_career)
        ##

        clean_new_students['job_id'] = clean_new_students['job_id'].astype(int)
        clean_new_students['current_career_path_id'] = clean_new_students['current_career_path_id'].astype(int)

        ######## getting a key error on 'current_career_path_id' ########
        clean_df = clean_new_students.merge(clean_career, left_on='current_career_path_id', right_on='current_career_path_id', how='left')
        clean_df = clean_df.merge(clean_student_jobs, on='job_id', how='left')

        ## unit test ##
        ## making sure chema and complete data before updating and inserting data ##
        if len(clean_df) > 0:
            test_num_of_columns(clean_df, cleanDB)
            test_schema(clean_df, cleanDB)
        test_null_values(clean_df)
        ##

        #updating and inserting clean data to cleaned_cade.db
        with sqlite3.connect('./dev/cleaned_cade.db') as sqlite_con:
            clean_df.to_sql('cade_concat', sqlite_con, if_exists='append', index=False)
            cleanDB = pd.read_sql_query('SELECT * FROM cade_concat', sqlite_con)
            sqlite_con.close()

        #write new clean data to cleaned_cade
        cleanDB.to_csv('./dev/cleaned_cade.csv')

        #create new automatic changelog entry
        new_lines = [
            '## 0.0.' +str(next_version) + '\n' + 
            '### Added\n' +
            '- ' + str(len(clean_df)) + ' more data to database of raw data\n' +
            '- ' + str(len(missingDB)) + ' new missing data to missing_info table\n' +
            '\n'
        ]
        with_lines = ''.join(new_lines + line)
 
        #updating changelog
        with open('./dev/changelog.md', 'w') as f:
            for line in with_lines:
                f.write(line)
    else:
        print('No new data')
        logger.info('No new data')
    logger.info('Ending Log')

if __name__ == '__main__':
    main()

