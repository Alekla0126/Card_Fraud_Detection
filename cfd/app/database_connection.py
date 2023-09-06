import psycopg2

# Parámetros de conexión a la base de datos
db_params = {
    'dbname': 'card_fraud_detection',
    'user': 'alekb',
    'password': 'NxEDX8aB1uxByZHssMCyHZ0ICWVNBlwL',
    'host': 'dpg-cjs6j2tm702s73b4dvq0-a.oregon-postgres.render.com',
    'port': '5432'
}

def connect_to_database():
    try:
        connection = psycopg2.connect(**db_params)
        return connection
    except psycopg2.Error as e:
        print("Error al conectar a la base de datos PostgreSQL:", e)
        return None