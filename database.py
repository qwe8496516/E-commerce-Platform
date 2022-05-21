import psycopg2
conn = psycopg2.connect(database="Database_Topic", user="postgres", password="123456789", host="127.0.0.1", port="5432")
print("Opened database successfully")
cur = conn.cursor()
cur.execute("SELECT * from members;")
rows = cur.fetchall()
for row in rows:
    print("m_fname = ",row[0],",m_lanme = ",row[1],",m_id = ",row[2],"\nm_phone = ",row[3],",m_email = ",row[4],",m_sex = ",row[5],",m_add = ",row[6],",m_pass = ",row[7],"\n"),

print("print Operation done successfully")
conn.close()