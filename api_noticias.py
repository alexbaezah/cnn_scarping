import json
from flask import Flask, jsonify, request, Response
import psycopg2
from psycopg2.extras import RealDictCursor
import unicodedata
from datetime import datetime
from flask import Flask, render_template

# Configuración de Flask
app = Flask(__name__)

# Configuración de la conexión a PostgreSQL
def get_db_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="noticias_db",
        user="postgres",
        password="1234"
    )
    return conn

# Endpoint para obtener todas las noticias
@app.route('/noticias/' or '/noticias', methods=['GET'])
def get_all_news():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Consulta SQL que utiliza la tabla intermedia `news_categories`
        cur.execute('''
        SELECT news.id, news.title, news.description, news.link,
                COALESCE(ARRAY_AGG(categories.nombre), ARRAY[]::text[]) AS categorias,
                TO_CHAR(news.fecha_captura, 'DD/MM/YY') AS fecha_captura
            FROM news
            LEFT JOIN news_categories ON news.id = news_categories.news_id
            LEFT JOIN categories ON news_categories.category_id = categories.id
            GROUP BY news.id, news.fecha_captura
            ORDER BY news.fecha_captura DESC
        ''')
        
        noticias = cur.fetchall()
        cur.close()
        conn.close()
        
        # Retornar el resultado como JSON
        return Response(json.dumps(noticias, ensure_ascii=False, indent=4), mimetype='application/json')
    except Exception as e:
        print("Error al obtener todas las noticias:", e)
        return jsonify({"error": "Error al obtener las noticias"}), 500



# Función para normalizar y convertir texto a minúsculas
def normalize_text(text):
    return ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    ).lower()  # Convertir a minúsculas después de eliminar tildes

# Endpoint para obtener noticias por categoría
@app.route('/noticias/<categoria>', methods=['GET'])
def get_news_by_category(categoria):
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Normalizar y convertir a minúsculas la categoría recibida en el URL
        categoria_normalizada = normalize_text(categoria)
        
        # Buscar el ID de la categoría normalizada
        cur.execute('SELECT id, nombre FROM categories')
        categorias = cur.fetchall()
        
        category_id = None
        for cat in categorias:
            if normalize_text(cat['nombre']) == categoria_normalizada:
                category_id = cat['id']
                break
        
        if category_id is None:
            return jsonify({"message": "Categoría no encontrada"}), 404

        # Consulta para obtener las noticias de la categoría usando la tabla intermedia `news_categories`
        cur.execute('''
            SELECT news.title, news.description, news.link, categories.nombre AS categoria
            FROM news
            JOIN news_categories ON news.id = news_categories.news_id
            JOIN categories ON news_categories.category_id = categories.id
            WHERE categories.id = %s
        ''', (category_id,))
        
        noticias = cur.fetchall()
        
        cur.close()
        conn.close()
        
        if noticias:
            return Response(json.dumps(noticias, ensure_ascii=False, indent=4), mimetype='application/json')
        else:
            return jsonify({"message": "No se encontraron noticias para la categoría especificada"}), 404
    except Exception as e:
        print("Error al obtener noticias por categoría:", e)
        return jsonify({"error": "Error al obtener las noticias para la categoría"}), 500


# Endpoint para listar todas las categorías
@app.route('/categorias', methods=['GET'])
def get_all_categories():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Consulta todas las categorías
        cur.execute('SELECT id, nombre FROM categories')
        categorias = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return Response(json.dumps(categorias, ensure_ascii=False, indent=4), mimetype='application/json')
    except Exception as e:
        print("Error al obtener categorías:", e)
        return jsonify({"error": "Error al obtener las categorías"}), 500


    


# Endpoint para buscar noticias por palabras clave
@app.route('/noticias/buscar', methods=['GET'])
def buscar_noticias():
    query = request.args.get('q', '').strip()  # Obtener el parámetro de búsqueda y eliminar espacios en blanco

    if not query:
        return jsonify({"error": "Parámetro de búsqueda 'q' es requerido"}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Consulta SQL para buscar en título, descripción o contenido completo
        cur.execute('''
            SELECT 
                news.id AS noticia_id,
                news.title AS titulo,
                news.description AS descripcion,
                news.link AS enlace,
                news.full_article AS articulo_completo,
                news.fecha_captura AS fecha_captura,
                array_agg(categories.nombre) AS categorias
            FROM 
                news
            LEFT JOIN 
                news_categories ON news.id = news_categories.news_id
            LEFT JOIN 
                categories ON news_categories.category_id = categories.id
            WHERE 
                news.title ILIKE %s OR 
                news.description ILIKE %s OR 
                news.full_article ILIKE %s
            GROUP BY 
                news.id
            ORDER BY news.fecha_captura DESC
        ''', (f'%{query}%', f'%{query}%', f'%{query}%'))
        
        # Obtener y procesar los datos
        noticias = cur.fetchall()
        
        # Convertir datetime a string para JSON y formatear los datos de salida
        for noticia in noticias:
            if 'fecha_captura' in noticia and noticia['fecha_captura']:
                noticia['fecha_captura'] = noticia['fecha_captura'].strftime('%d-%m-%Y')
        
        cur.close()
        conn.close()
        
        # Responder con las noticias encontradas o un mensaje si no hay resultados
        if noticias:
            return Response(json.dumps(noticias, ensure_ascii=False, indent=4), mimetype='application/json')
        else:
            return jsonify({"message": "No se encontraron noticias que coincidan con la búsqueda"}), 404

    except Exception as e:
        print("Error en la búsqueda de noticias:", e)
        return jsonify({"error": "Error al realizar la búsqueda de noticias"}), 500

# Endpoint para mostrar la vista de los endpoints
@app.route('/index', methods=['GET'])
def view_endpoints():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)


