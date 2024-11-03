import psycopg2

# Establish the connection
with psycopg2.connect(
    user='postgres',
    password='12345678',
    database='sample_db',
    host='35.225.115.246',
    port=5432
) as conn:
    
    # Create a cursor and execute the query
    with conn.cursor() as cursor:
        cursor.execute('SELECT * FROM users')
        
        # Fetch and print all rows
        rows = cursor.fetchall()
        for row in rows:
            print(row)