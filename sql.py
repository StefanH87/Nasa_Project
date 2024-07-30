import mysql.connector



my_db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="wildfires"
)
cursor = my_db.cursor()  # cursor verweist auf die Datenbank



#my_cursor.execute("CREATE DATABASE wildfires")
cursor.execute("SHOW DATABASES")
for db in cursor:
    print(db)

#def show_tables():
#   cursor.execute("SELECT * FROM global_wildfires")
 #   result = cursor.fetchall()

#    for t in result:
#        print(t)
#----------------------------------------------------------------------


sql_table_global_wildfires = """
        CREATE TABLE global_wildfires(
            event_id INTEGER AUTO_INCREMENT PRIMARY KEY,
            date DATE NOT NULL,
            time TIME NOT NULL,
            timestamp TIMESTAMP,
            longitude DOUBLE,
            latitude DOUBLE,
            city VARCHAR(255) NOT NULL,
            region VARCHAR(255),
            territorium VARCHAR(255),
            country VARCHAR(100) NOT NULL            
        )
     """
sql_table_wildfires_size = """                        
        CREATE TABLE wildfires_size(
            size_id INTEGER AUTO_INCREMENT PRIMARY KEY,
            event_id INTEGER,
            type VARCHAR(25),
            magnitude_unit FLOAT,
            magnitude_value FLOAT,
            square_meter FLOAT,
            square_km FLOAT,
            FOREIGN KEY (event_id) REFERENCES global_wildfires(event_id)
        )
     """


cursor.execute(sql_table_global_wildfires)
cursor.execute(sql_table_wildfires_size)