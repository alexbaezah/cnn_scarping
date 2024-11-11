import psycopg2

# Configuración de la conexión a PostgreSQL
def get_db_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="noticias_db",
        user="postgres",
        password="1234"
    )
    return conn

# Función que devuelve una lista de category_ids relevantes para una noticia
def get_relevant_category_ids(news_content, conn):
    category_ids = []
    cur = conn.cursor()

    # Diccionario de categorías y palabras clave asociadas
    categories_keywords = {
        "Política": ["gobierno", "presidente", "elecciones", "política"],
        "Deportes": ["fútbol", "deporte", "partido", "gol", "equipo"],
        "Economía": ["economía", "finanzas", "mercado", "dinero", "inversión"],
        "Cultura": ["arte", "música", "cine", "teatro", "cultura"],
        "Tecnología": ["tecnología", "internet", "software", "redes", "ciberseguridad"],
    }

    # Revisar cada categoría y asociar categorías relevantes a la noticia
    for category, keywords in categories_keywords.items():
        if any(keyword.lower() in news_content.lower() for keyword in keywords):
            cur.execute("SELECT id FROM categories WHERE nombre = %s", (category,))
            result = cur.fetchone()
            if result:
                category_ids.append(result[0])

    cur.close()
    return category_ids

# Función para poblar la tabla de relaciones news_categories
def populate_news_categories():
    conn = get_db_connection()
    cur = conn.cursor()

    # Seleccionar todas las noticias
    cur.execute("SELECT id, full_article FROM news")
    all_news = cur.fetchall()

    # Iterar sobre cada noticia y asociar categorías relevantes
    for news_id, full_article in all_news:
        category_ids = get_relevant_category_ids(full_article, conn)

        # Insertar cada relación en la tabla news_categories
        for category_id in category_ids:
            cur.execute(
                "INSERT INTO news_categories (news_id, category_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                (news_id, category_id)
            )
        print(f"Noticia {news_id} asociada con categorías {category_ids}")

    # Confirmar los cambios
    conn.commit()
    cur.close()
    conn.close()

# Ejecutar la función para poblar la tabla news_categories
populate_news_categories()
