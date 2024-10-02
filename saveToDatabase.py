# import psycopg2

# # Database connection parameters
# conn = psycopg2.connect(
#     dbname='prodetect_postgresql_api',
#     user='root',
#     password='GBaALwQ2LdWVkKc80tbBzGzoz0BtB2uo',
#     host='dpg-cq1h3u3v2p9s73acnfng-a.oregon-postgres.render.com',
#     port='5432'
# )

# cur = conn.cursor()

# # Path to your CSV file
# csv_file_path = '/Users/judeukana/MestProjects/Python/NewCo/transactions.csv'

# # SQL command to create the table (if not already created)
# create_table_query = '''
# CREATE TABLE IF NOT EXISTS transactions (
#     id SERIAL PRIMARY KEY,
#     CustomerID VARCHAR(8),
#     AccountNumber VARCHAR(8),
#     TransactionType VARCHAR(6),
#     Amount DECIMAL(10, 2),
#     AccountBalance DECIMAL(10, 2),
#     ReceiverName VARCHAR(100),
#     TransactionTime TIMESTAMP
# );
# '''
# try:
#     cur.execute(create_table_query)
#     conn.commit()
# except psycopg2.Error as e:
#     print(f"Error creating table: {e}")
#     conn.rollback()


# # Command to copy data from CSV file to the PostgreSQL table
# try:
#     with open(csv_file_path, 'r') as f:
#         next(f)
#     cur.copy_expert("COPY transactions (id, CustomerID, AccountNumber,TransactionType,Amount,AccountBalance,ReceiverName,TransactionTime) FROM STDIN WITH CSV HEADER DELIMITER AS ','", f)

# # Commit the transaction and close the connection
#     conn.commit()
# except psycopg2.Error as e:
#     print(f"Error copying data: {e}")
#     conn.rollback()



# cur.close()
# conn.close()

# print("Data loaded successfully")






import psycopg2

# Database connection parameters
conn = psycopg2.connect(
    dbname='prodetect_postgresql_api_two',
    user='prodetect_postgresql_api_two_user',
    password='MFhVtFl5E9eQ8gUxr8ueCo2IlLH24VVr',
    host='dpg-cqlqo5tumphs739lbn7g-a.oregon-postgres.render.com',
    port='5432'
)

cur = conn.cursor()

# Path to your CSV file
csv_file_path = '/Users/judeukana/MestProjects/Python/NewCo/DataSets/transactions_with_transactionid.csv'

# SQL command to create the table if it does not exist
create_table_query = '''
CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    TransactionID VARCHAR(10),
    CustomerID VARCHAR(8),
    AccountNumber VARCHAR(8),
    TransactionType VARCHAR(6),
    Amount DECIMAL(10, 2),
    AccountBalance DECIMAL(10, 2),
    ReceiverName VARCHAR(100),
    TransactionTime TIMESTAMP
);
'''
try:
    cur.execute(create_table_query)
    conn.commit()
except psycopg2.Error as e:
    print(f"Error creating table: {e}")
    conn.rollback()

# Command to copy data from CSV file to the PostgreSQL table
try:
    with open(csv_file_path, 'r', encoding='utf-8') as f:
        next(f)  # Skip the header row
        cur.copy_expert("COPY transactions (TransactionID, CustomerID, AccountNumber, TransactionType, Amount, AccountBalance, ReceiverName, TransactionTime) FROM STDIN WITH CSV HEADER DELIMITER AS ','", f)

    conn.commit()
except psycopg2.Error as e:
    print(f"Error copying data: {e}")
    conn.rollback()

# Close the connection
cur.close()
conn.close()

print("Data loaded successfully")



