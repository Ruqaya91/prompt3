import mysql.connector
from getpass import getpass

# Database connection configuration
db_config = {
    "host": "localhost",      # or your DB host
    "user": "your_mysql_user",
    "password": "your_mysql_password",
    "database": "your_database"
}

try:
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
except mysql.connector.Error as err:
    print(f"Error connecting to database: {err}")
    exit(1)

# Prompt user for credentials
username = input("Enter your username: ")
password = getpass("Enter your password: ")

# Query to check credentials
query = "SELECT * FROM users WHERE username = %s AND password = %s"
cursor.execute(query, (username, password))
result = cursor.fetchone()

if result:
    print("Login successful!")
else:
    print("Login failed.")

cursor.close()
conn.close()
