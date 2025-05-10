#!/usr/bin/env python
# coding: utf-8

# In[23]:


import sqlite3
import time

# Database file path
db_path = r"D:\MSC\SW studio\Bank fraud_Sql.db"

# Table names
source_table = "new"
target_table = "dwh"

def move_transactions():
    conn = sqlite3.connect(db_path, timeout=10)  # timeout to prevent locking issues
    cur = conn.cursor()

    try:
        # Fetch all rows from source_table
        cur.execute(f'SELECT * FROM "{source_table}"')
        rows = cur.fetchall()

        if rows:
            # Get column names and quote each one
            col_names = [f'"{description[0]}"' for description in cur.description]
            target_columns = col_names + ['fraud']
            placeholders = ','.join(['?'] * len(target_columns))

            # Add fraud = 0 to each row
            rows_with_fraud = [row + (0,) for row in rows]

            # Insert into target_table
            cur.executemany(
                f'INSERT INTO "{target_table}" ({",".join(target_columns)}) VALUES ({placeholders})',
                rows_with_fraud
            )

            # Delete all from source_table
            cur.execute(f'DELETE FROM "{source_table}"')
            conn.commit()

            print(f"Moved {len(rows)} rows to {target_table} with fraud=0.")

    except Exception as e:
        print("Error:", e)

    finally:
        conn.close()

# Run every 3 seconds
print("Monitoring 'new' table every 3 seconds. Press Ctrl+C to stop.")
try:
    while True:
        move_transactions()
        time.sleep(3)
except KeyboardInterrupt:
    print("\nStopped monitoring.")


# In[ ]:




