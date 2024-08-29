# import psycopg2

# db = psycopg2.connect(user = "postgres",
#                       password = "12345",
#                       host = "127.0.0.1",
#                       port = "5432",
#                       database = "postgres")


# imlec = db.cursor()

# # print(db.get_dsn_parameters())

# komut_CREATE = """CREATE TABLE isimler(
#                 id SERIAL PRIMARY KEY,
#                 ad TEXT NOT NULL,
#                 soyad TEXT NOT NULL
#                 );"""

# imlec.execute(komut_CREATE)
# db.commit()


#---------------------------------------------------------------------------------------------------------------


# import psycopg2

# database_name = "postgres"
# user_name = "postgres"
# password = "12345"
# host_ip = "127.0.0.1"
# host_port = "5432"

# baglanti = psycopg2.connect(database = database_name,
#                             user = user_name,
#                             password = password,
#                             host = host_ip,
#                             port = host_port)

# baglanti.autocommit = True
# cursor = baglanti.cursor()

# query = "CREATE DATABASE car_db"
# cursor.execute(query)
