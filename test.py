import mysql.connector

print("🔌 Connecting...")
conn = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="KAgdeckeywukMe0",
    database="analizeprog",
    port=3306,
    connection_timeout=5
)
print("✅ Connected.")
cursor = conn.cursor()
cursor.execute("SELECT NOW()")
print("⏰ Time:", cursor.fetchone()[0])
cursor.close()
conn.close()
