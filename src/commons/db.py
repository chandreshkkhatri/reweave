"""db queries"""

import sqlite3

conn = sqlite3.connect('clockwork.db', isolation_level=None,check_same_thread=False)

""" DB level queries """
def create_request_table():
    cur = conn.cursor()
    cur.execute(create_video_request_table_query)
    return cur

def create_bulk_request_table():
    cur = conn.cursor()
    cur.execute('''CREATE TABLE bulk_video_request(
        job_id VAR_CHAR(255),
        file_name VAR_CHAR(255)
        )''')
    return cur

def delete_table(table_name):
    cur = conn.cursor()
    cur.execute(f'DROP TABLE "{table_name}";')
    return cur.fetchall()

def get_job_status(job_id):
    cur = conn.cursor()
    cur.execute(f'SELECT status FROM video_request WHERE job_id="{job_id}"')
    return cur.fetchone()

def get_video_request(id):
    cur = conn.cursor()
    cur.execute(f'SELECT * FROM video_request WHERE rowid="{id}"')
    return cur.fetchone()

def create_video_request(job_id,file_name,template,content,status):
    cur = conn.cursor()
    cur.execute(f'INSERT INTO video_request (job_id, file_name, template, content, status) VALUES("{job_id}","{file_name}","{template}","{content}","{status}");')
    return cur.fetchone()

def create_bulk_video_request(job_id, filename):
    cur = conn.cursor()
    cur.execute(f'INSERT INTO video_request (job_id, file_name) VALUES("{job_id}","{filename}");')
    return cur.fetchone()
    
def delete_video_request(id):
    cur = conn.cursor()
    cur.execute(f'DELETE FROM video_request WHERE rowid="{id}"')
    return cur

def update_video_request_status(job_id,status):
    cur = conn.cursor()
    cur.execute(f'UPDATE video_request SET status="{status}" WHERE job_id="{job_id}"')
    return cur.fetchone()

def get_video_requests():
    cur = conn.cursor()
    cur.execute(get_video_requests_query)
    return cur.fetchall()
    
def get_video_request_status(id):
    cur = conn.cursor()
    cur.execute(f'SELECT status FROM video_request WHERE id="{id}"')
    return cur.fetchone()

def get_table_info(table_name):
    cur = conn.cursor()
    cur.execute(f"""SELECT name FROM sqlite_master WHERE type="{table_name}";""")
    return cur.fetchall()

get_video_requests_query = 'SELECT rowid, * FROM video_request'
create_video_request_table_query = '''CREATE TABLE video_request(
    job_id VAR_CHAR(255), 
    file_name VAR_CHAR(255), 
    template VAR_CHAR(255), 
    content VAR_CHAR(255), 
    status VAR_VHAR(255));'''
    
if __name__ == '__main__':
    newcur = conn.cursor()
    query = 'SELECT * FROM video_request'
    newcur.execute(query)
    print(newcur.fetchall())