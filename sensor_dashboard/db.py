import sqlite3

import pandas as pd

CREATE_TABLE_QUERY = \
    """
    CREATE TABLE IF NOT EXISTS measurements (
        date_time TEXT PRIMARY KEY,
        temp REAL,
        humidity REAL
    );
    """

INSERT_RECORD_QUERY = \
    """
    INSERT INTO measurements (date_time, temp, humidity)
    VALUES(datetime('now', 'localtime'), ?, ?);
    """

SELECT_ALL_QUERY = \
    """
    SELECT * FROM measurements;
    """

DELETE_ALL_QUERY = \
    """
    DELETE FROM measurements;
    """

DELETE_OLDER_THAN_ONE_WEEK = \
    """
    DELETE FROM measurements
    WHERE date_time < datetime('now', 'localtime', '-1 week');
    """


class DB:
    def __init__(self, db_path):
        self.db_path = db_path
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute(CREATE_TABLE_QUERY)

    def add_measurement_to_db(self, temp, humidity):
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute(INSERT_RECORD_QUERY, [temp, humidity])
            conn.commit()

    def get_db_measurements_list(self):
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            query_res = cur.execute(SELECT_ALL_QUERY)
        return list(query_res)

    def get_db_measurements_df(self):
        measurements = self.get_db_measurements_list()
        if len(measurements) == 0:
            return None
        df = pd.DataFrame(measurements)
        df.columns = ['Time', 'Temperature', 'Humidity']
        df['Time'] = pd.to_datetime(df['Time'])
        return df

    def delete_all_measurements(self):
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            _ = cur.execute(DELETE_ALL_QUERY)

    def delete_older_than_one_week(self):
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            _ = cur.execute(DELETE_OLDER_THAN_ONE_WEEK)
            conn.commit()
