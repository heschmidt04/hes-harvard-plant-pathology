# Import csv to postgresql db

import psycopg2
import pandas as pd

# Update with your user name
conn = psycopg2.connect("host=localhost dbname=foliar user=postgres password='YourPassWordGoesHere'")
cur = conn.cursor()

cur.execute('DROP TABLE IF EXISTS users;')
cur.execute('DROP TABLE IF EXISTS classification_treatment_information;')
cur.execute('DROP TABLE IF EXISTS image_information;')

cur.execute('''CREATE TABLE users (
    uid serial NOT NULL PRIMARY KEY,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    date_registered TIMESTAMP NOT NULL DEFAULT NOW()
    );''')

cur.execute('''CREATE TABLE image_information (
    image_id  SERIAL PRIMARY KEY NOT NULL,
    uid INTEGER references users(uid),
    image_name TEXT NOT NULL,
    image_submitted_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    image_classification_id INTEGER references classification_treatment_information(id)
    );''')

cur.execute('''CREATE TABLE classification_treatment_information (
    id  SERIAL PRIMARY KEY NOT NULL,
    classification_name TEXT NOT NULL,
    background_info TEXT NOT NULL,
    treatment_info TEXT NOT NULL, 
    sources TEXT NOT NULL
    );''')

cur.execute('''CREATE TABLE treatment_methods (
    id  SERIAL PRIMARY KEY NOT NULL,
    treatment_name TEXT NOT NULL,
    treatment_methods TEXT NOT NULL, 
    sources TEXT NOT NULL
    );''')

conn.commit()

# df_users = pd.read_csv('./data/predefined_users.csv', index_col=0)
# for idx, u in df_users.iterrows():
#     # Data cleaning
# 
#     q = cur.execute(
#         '''INSERT INTO homework_users (username, first_name, last_name, prog_lang, experience_yr, age, hw1_hrs) VALUES (%s,%s,%s,%s,%s,%s,%s)''',
#         (u.username, u.first_name, u.last_name, u.prog_lang, u.experience_yr, u.age, u.hw1_hrs)
#     )
#     conn.commit()
 
cur.close()
conn.close()
