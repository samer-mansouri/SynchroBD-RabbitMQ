import mysql.connector
import os

config = {
    'user': os.getenv('BRANCH_OFFICE_2_DB_USER'),
    'password': os.getenv('BRANCH_OFFICE_2_DB_PASSWORD'),
    'host': os.getenv('BRANCH_OFFICE_2_DB_HOST'),
    'port': os.getenv('BRANCH_OFFICE_2_DB_PORT'),
    'database': os.getenv('BRANCH_OFFICE_2_DB_NAME'),
    'raise_on_warnings': True
}

try:
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()

    create_table_query = """
    CREATE TABLE IF NOT EXISTS sales (
      date VARCHAR(5),
      region VARCHAR(10),
      product VARCHAR(10),
      qty INT,
      cost DECIMAL(10, 2),
      amt DECIMAL(10, 2),
      tax DECIMAL(10, 2),
      total DECIMAL(10, 2),
      id INT AUTO_INCREMENT PRIMARY KEY
    );
    """

    insert_data_query = """
    INSERT INTO sales (date, region, product, qty, cost, amt, tax, total) VALUES
    (%s, %s, %s, %s, %s, %s, %s, %s);
    """

    data_to_insert = [
        ("1-Apr", "East", "Paper", 73, 12.95, 945.35, 66.17, 1011.52),
        ("1-Apr", "West", "Paper", 33, 12.95, 427.35, 29.91, 457.26),
        ("2-Apr", "East", "Pens", 14, 2.19, 30.66, 2.15, 32.81),
        ("2-Apr", "West", "Pens", 40, 2.19, 87.60, 6.13, 93.73),
        ("3-Apr", "East", "Paper", 21, 12.95, 271.95, 19.04, 290.99),
        ("3-Apr", "West", "Paper", 10, 12.95, 129.50, 9.07, 138.57)
    ]

    cursor.execute(create_table_query)

    cursor.executemany(insert_data_query, data_to_insert)

    cnx.commit()
    print("Table created and data inserted successfully.")
except mysql.connector.Error as err:
    print(f"Error: {err}")
finally:
    if 'cursor' in locals():
        cursor.close()
    if 'cnx' in locals() and cnx.is_connected():
        cnx.close()
