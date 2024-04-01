import mysql.connector

config = {
    'user': 'user',
    'password': 'password',
    'host': 'localhost',  
    'port': '3306',
    'database': 'head_office',
    'raise_on_warnings': True
}

try:
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()

    create_table_query = """
    CREATE TABLE IF NOT EXISTS sales (
      remote_id INT,
      branch_office_id INT,
      date VARCHAR(5),
      region VARCHAR(10),
      product VARCHAR(10),
      qty INT,
      cost DECIMAL(10, 2),
      amt DECIMAL(10, 2),
      tax DECIMAL(10, 2),
      total DECIMAL(10, 2),
      PRIMARY KEY (remote_id, branch_office_id)
    );
    """
    cursor.execute(create_table_query)

    cnx.commit()
    print("Table created successfully.")
except mysql.connector.Error as err:
    print(f"Error: {err}")
finally:
    if 'cursor' in locals():
        cursor.close()
    if 'cnx' in locals() and cnx.is_connected():
        cnx.close()
