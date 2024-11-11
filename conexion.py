import psycopg2
import json

# Conexión a PostgreSQL
conn = psycopg2.connect(
    host="localhost",  # Cambia esto si usas un host diferente
    database="noticias_db",
    user="postgres",
    password="1234"
)

# Crear cursor
cur = conn.cursor()

# Función para guardar noticias en PostgreSQL
def save_news_to_db(news_data):
    for news in news_data:
        cur.execute('''
            INSERT INTO news (title, link, description, full_article, fecha_captura)
            VALUES (%s, %s, %s, %s, %s)
        ''', (news['title'], news['link'], news['description'], news['full_article'], news['fecha_captura']))
    
    conn.commit()  # Confirmar los cambios
    print("Noticias guardadas en PostgreSQL")

# Cargar datos desde el archivo JSON
with open('noticias_cnn_2024-10-25.json', 'r', encoding='utf-8') as f:
    news_data = json.load(f)

# Guardar las noticias en la base de datos
save_news_to_db(news_data)

# Cerrar la conexión
cur.close()
conn.close()
