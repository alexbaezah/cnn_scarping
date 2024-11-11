import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json

# Función para obtener el cuerpo de una noticia
def get_full_article(url):
    response = requests.get(url)
    response.encoding = 'utf-8'  # Asegurar UTF-8
    soup = BeautifulSoup(response.text, 'html.parser')

    # Intentar extraer el cuerpo de la noticia
    article_body = soup.find_all('p')  # En algunos casos, los párrafos de la noticia están dentro de <p>
    full_text = " ".join([p.text for p in article_body])  # Unir todos los párrafos en un solo texto
    return full_text

# URL de CNN Chile
url = 'https://www.cnnchile.com/'

# Realiza la solicitud
response = requests.get(url)

# Asegurarse de que el contenido esté en UTF-8
response.encoding = 'utf-8'

# Parsear el contenido HTML
soup = BeautifulSoup(response.text, 'html.parser')

# Lista para almacenar las noticias
news_data = []

# Obtener la fecha de captura actual
fecha_captura = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Extraer noticia destacada principal
main_article = soup.find('div', class_='article')
if main_article:
    title = main_article.find('h2').text.strip() if main_article.find('h2') else 'Sin título'
    link = main_article.find('a')['href']
    description = main_article.find('p').text.strip() if main_article.find('p') else 'No description'
    
    # Obtener el cuerpo de la noticia
    full_article = get_full_article(link)
    
    # Guardar la noticia en el array con la fecha de captura
    news_data.append({
        "title": title,
        "link": link,
        "description": description,
        "full_article": full_article,
        "fecha_captura": fecha_captura
    })

# Extraer noticias relacionadas (lista de artículos)
related_articles = soup.find_all('div', class_='item')

for article in related_articles:
    # Busca primero un h2, si no existe busca un h3
    title_tag = article.find('h2') or article.find('h3')
    if title_tag:
        title = title_tag.text.strip()
        link = article.find('a')['href']
        
        # Obtener el cuerpo de la noticia
        full_article = get_full_article(link)
        
        # Guardar la noticia en el array con la fecha de captura
        news_data.append({
            "title": title,
            "link": link,
            "description": "Not available",  # En caso de no tener descripción específica
            "full_article": full_article,
            "fecha_captura": fecha_captura
        })

# Generar nombre de archivo con la fecha actual
file_name = f"noticias_cnn_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"

# Guardar el array como un archivo JSON con la fecha actual en el nombre
with open(file_name, 'w', encoding='utf-8') as f:
    json.dump(news_data, f, ensure_ascii=False, indent=4)

# Imprimir mensaje de éxito
print(f"Noticias guardadas en '{file_name}'")
