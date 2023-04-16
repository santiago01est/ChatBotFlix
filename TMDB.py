import requests
# Configurar las credenciales de la API de TMDb
API_KEY = "764d08acf76677de0c5358a603dcc9g5" # Reemplaza con tu propia API Key de TMDb
BASE_URL = "https://api.themoviedb.org/3"

def buscarPelicula(name):
    print(name)
    url = f"{BASE_URL}/search/movie"
    params = {
        "api_key": API_KEY,
        "query": name,
        "language": "es" # Idioma de los resultados
    }
    response = requests.get(url, params=params)
    data = response.json()
    if "results" in data and data["results"]:
        pelicula = data["results"][0]
        titulo = pelicula["title"]
        sinopsis = pelicula["overview"]
        poster = pelicula["poster_path"]
        informacion = f"Título: {titulo}\nSinopsis: {sinopsis}"
        url_poster = "https://image.tmdb.org/t/p/w500"+poster
        return url_poster,informacion
    else:
        return "","No se encontró la película." 
    
def buscar_id_pelicula(name):
    print(name)
    url = f"{BASE_URL}/search/movie"
    params = {
        "api_key": API_KEY,
        "query": name,
        "language": "es" # Idioma de los resultados
    }
    response = requests.get(url, params=params)
    data = response.json()
    if "results" in data and data["results"]:
        pelicula = data["results"][0]
        id = pelicula["id"]
        return id
    else:
        return "No se encontró la película." 

def buscar_recomendacion_pelicula(name,num_peliculas):
    lista_recomendaciones=[]
    id=buscar_id_pelicula(name)
    url = f"{BASE_URL}/movie/{id}/recommendations"
    params = {
        "api_key": API_KEY,
        "language": "es" # Idioma de los resultados
    }
    response = requests.get(url, params=params)
    data = response.json()
    if "results" in data and data["results"]:
        for i in range(num_peliculas):
            pelicula = data["results"][i]
            lista_recomendaciones.append(pelicula)
        return lista_recomendaciones
    else:
        return "No se encontró la película." 

    
