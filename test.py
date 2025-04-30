import sqlite3
import pandas as pd

# ✅ Show data from attendance.db
print("🟢 Data from attendance.db:")
conn1 = sqlite3.connect('attendance.db')
df1 = pd.read_sql_query("SELECT * FROM attendance", conn1)  # replace 'attendance' if table name is different
print(df1)
conn1.close()

print("\n" + "-"*50 + "\n")

# ✅ Show data from users.db
print("🔵 Data from users.db:")
conn2 = sqlite3.connect('users.db')
df2 = pd.read_sql_query("SELECT * FROM users", conn2)  # replace 'users' if table name is different
print(df2)
conn2.close()
