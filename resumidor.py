import spacy
import psycopg2
import json

# Cargar el modelo de spaCy en español
nlp = spacy.load('es_core_news_md')

# Conexión a PostgreSQL
conn = psycopg2.connect(
    host="localhost",
    database="noticias_db",
    user="postgres",
    password="1234"
)

# Crear cursor
cur = conn.cursor()

# Función para generar un resumen usando spaCy
def generate_summary(full_article, sentence_limit=2):
    # Procesar el artículo con spaCy
    doc = nlp(full_article)
    
    # Tomar las primeras 'sentence_limit' frases
    summary = " ".join([str(sent) for sent in doc.sents][:sentence_limit])
    return summary

# Función para leer noticias desde un archivo JSON
def load_news_from_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# Función para actualizar las noticias en PostgreSQL
def update_news_in_db(news_data):
    for news in news_data:
        # Verificar si la descripción está como "Not available"
        if news['description'] == "Not available":
            print(f"Actualizando noticia: {news['title']}")
            
            # Generar una nueva descripción basada en el artículo completo
            news['description'] = generate_summary(news['full_article'])  # Usa el resumen automático
            print(f"Descripción generada: {news['description'][:100]}...")  # Imprimir los primeros 100 caracteres de la descripción
            
            # Comprobar si el link existe en la base de datos antes de hacer el update
            cur.execute('SELECT link FROM news WHERE link = %s', (news['link'],))
            result = cur.fetchone()
            
            if result:
                print(f"Link encontrado: {news['link']}, actualizando...")
                # Actualizar la noticia en la base de datos
                cur.execute('''
                    UPDATE news
                    SET description = %s
                    WHERE link = %s
                ''', (news['description'], news['link']))
                print(f"Filas afectadas: {cur.rowcount}")  # Verificar cuántas filas fueron afectadas por el UPDATE
            else:
                print(f"Link no encontrado en la base de datos: {news['link']}")
    
    conn.commit()  # Confirmar los cambios
    print("Noticias actualizadas en PostgreSQL")

# Cargar noticias desde el archivo JSON
news_data = load_news_from_json('noticias_cnn_2024-10-25.json')

# Actualizar las noticias en la base de datos
update_news_in_db(news_data)

# Cerrar conexión
cur.close()
conn.close()
