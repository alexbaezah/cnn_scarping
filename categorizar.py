import psycopg2

# Conexión a PostgreSQL
conn = psycopg2.connect(
    host="localhost",
    database="noticias_db",
    user="postgres",
    password="1234"
)

# Crear cursor
cur = conn.cursor()

# Definir las categorías y palabras clave asociadas
categories_keywords = {
    "Política": ["gobierno", "presidente", "elecciones", "política"],
    "Deportes": ["fútbol", "deporte", "partido", "gol", "equipo"],
    "Economía": ["economía", "finanzas", "mercado", "dinero", "inversión"],
    "Cultura": ["arte", "música", "cine", "teatro", "cultura"],
    "Tecnología": ["tecnología", "internet", "software", "redes", "ciberseguridad"],
}

# Función para obtener el id de la categoría por nombre
def get_category_id(nombre):
    cur.execute("SELECT id FROM categories WHERE nombre = %s", (nombre,))
    result = cur.fetchone()
    return result[0] if result else None

# Función para categorizar una noticia basada en su contenido
def categorize_article(full_article):
    full_article_lower = full_article.lower()  # Convertir el texto a minúsculas para buscar palabras clave
    
    for category, keywords in categories_keywords.items():
        for keyword in keywords:
            if keyword in full_article_lower:
                return category  # Retorna la categoría en la que encuentra la primera coincidencia de palabra clave

    return "Otros"  # Retorna "Otros" si no coincide con ninguna categoría

# Consulta para seleccionar todas las noticias que necesitan categorización
cur.execute("SELECT id, full_article FROM news WHERE category_id IS NULL")

# Obtener todas las noticias pendientes de categorización
news_to_categorize = cur.fetchall()

# Categorizar y actualizar cada noticia
for news_id, full_article in news_to_categorize:
    # Determinar la categoría por nombre
    category_name = categorize_article(full_article)
    # Obtener el ID de la categoría desde la tabla `categories`
    category_id = get_category_id(category_name)
    
    # Actualizar la noticia con el category_id en la tabla news
    cur.execute("UPDATE news SET category_id = %s WHERE id = %s", (category_id, news_id))
    print(f"Noticia ID {news_id} categorizada como: {category_name} (ID {category_id})")

# Confirmar los cambios en la base de datos
conn.commit()
print("Categorías actualizadas en la base de datos")

# Cerrar la conexión
cur.close()
conn.close()