from flask import Flask, render_template, request
import requests
import difflib
import random
import mysql.connector

app = Flask(__name__)

conexion = mysql.connector.connect(
    host='localhost',
    user='root',
    password='',
    database='uno'
)
cursor = conexion.cursor()

historial_busqueda = []
backgrounds = ['background1.jpg', 'background2.jpg', 'background3.jpg']

def obtener_descripcion_pokedex(nombre_pokemon):
    url = f"https://pokeapi.co/api/v2/pokemon-species/{nombre_pokemon}"
    try:
        respuesta = requests.get(url)
        respuesta.raise_for_status()  # Lanzar una excepción en caso de error de solicitud
        
        datos = respuesta.json()
        descripcion = datos['flavor_text_entries'][0]['flavor_text']  # Tomamos la primera descripción, podrías ajustarlo si deseas una en particular
        return descripcion
    except requests.exceptions.HTTPError as e:
        return "No se pudo obtener la descripción de la Pokédex."

def obtener_region_aparicion(nombre_pokemon):
    url = f"https://pokeapi.co/api/v2/pokemon-species/{nombre_pokemon}"
    try:
        respuesta = requests.get(url)
        respuesta.raise_for_status()  # Lanzar una excepción en caso de error de solicitud
        
        datos = respuesta.json()
        if 'version_group' in datos:
            regiones = [version['version']['name'] for version in datos['version_group'] if version['version']['name'] != '']
            return regiones
        else:
            return ["No se encontró información de aparición del Pokémon."]
    except requests.exceptions.HTTPError as e:
        return ["No se pudo obtener la información de aparición del Pokémon."]

def obtener_debilidades(nombre_pokemon):
    url = f"https://pokeapi.co/api/v2/pokemon/{nombre_pokemon}"
    try:
        respuesta = requests.get(url)
        respuesta.raise_for_status()  # Lanzar una excepción en caso de error de solicitud
        
        datos = respuesta.json()
        debilidades = []
        for tipo in datos['types']:
            tipo_nombre = tipo['type']['name']
            url_tipo = f"https://pokeapi.co/api/v2/type/{tipo_nombre}"
            respuesta_tipo = requests.get(url_tipo)
            respuesta_tipo.raise_for_status()
            datos_tipo = respuesta_tipo.json()
            for damage_relation in datos_tipo['damage_relations']['double_damage_from']:
                debilidades.append(damage_relation['name'])
        return debilidades
    except requests.exceptions.HTTPError as e:
        return ["No se pudo obtener la información de debilidades del Pokémon."]

@app.route('/')
def index():
    background_image = random.choice(backgrounds)
    pokemons = obtener_nombres_pokemon()
    tipos = obtener_tipos_pokemon()
    return render_template('index.html', pokemons=pokemons, tipos=tipos, historial_busqueda=historial_busqueda, background_image=background_image)

@app.route('/buscar', methods=['POST'])
def buscar_pokemon():
    nombre_pokemon = request.form['nombre_pokemon'].lower()
    tipo_pokemon = request.form['tipo_pokemon'].lower() if 'tipo_pokemon' in request.form else None
    historial_busqueda.append(nombre_pokemon)
    
    if tipo_pokemon:  # Si se está buscando por tipo
        url = f"https://pokeapi.co/api/v2/type/{tipo_pokemon}"
        try:
            respuesta = requests.get(url)
            respuesta.raise_for_status()  # Lanzar una excepción en caso de error de solicitud
            
            datos = respuesta.json()
            pokemons = [pokemon['pokemon']['name'] for pokemon in datos['pokemon']]
            
            if nombre_pokemon:  # Si se proporcionó un nombre de Pokémon
                # Mostrar la información del Pokémon seleccionado
                url_pokemon = f"https://pokeapi.co/api/v2/pokemon/{nombre_pokemon}"
                respuesta_pokemon = requests.get(url_pokemon)
                respuesta_pokemon.raise_for_status()
                datos_pokemon = respuesta_pokemon.json()
                
                nombre = datos_pokemon['name']
                id_pokemon = datos_pokemon['id']
                tipos = [tipo['type']['name'] for tipo in datos_pokemon['types']]
                habilidades = [habilidad['ability']['name'] for habilidad in datos_pokemon['abilities']]
                imagen_url = datos_pokemon['sprites']['front_default']
                descripcion_pokedex = obtener_descripcion_pokedex(nombre)
                regiones_aparicion = obtener_region_aparicion(nombre)
                debilidades = obtener_debilidades(nombre)
                
                sugerencia = obtener_sugerencia(nombre)
                
                return render_template('resultado.html', 
                                       nombre=nombre,
                                       id_pokemon=id_pokemon,
                                       tipos=tipos,
                                       habilidades=habilidades,
                                       imagen_url=imagen_url,
                                       sugerencia=sugerencia,
                                       descripcion_pokedex=descripcion_pokedex,
                                       regiones_aparicion=regiones_aparicion,
                                       debilidades=debilidades,
                                       historial_busqueda=historial_busqueda)
            else:  # Si no se proporcionó un nombre de Pokémon
                # Mostrar un Pokémon aleatorio de la lista obtenida
                nombre_random = random.choice(pokemons)
                url_pokemon = f"https://pokeapi.co/api/v2/pokemon/{nombre_random}"
                respuesta_pokemon = requests.get(url_pokemon)
                respuesta_pokemon.raise_for_status()
                datos_pokemon = respuesta_pokemon.json()
                
                nombre = datos_pokemon['name']
                id_pokemon = datos_pokemon['id']
                tipos = [tipo['type']['name'] for tipo in datos_pokemon['types']]
                habilidades = [habilidad['ability']['name'] for habilidad in datos_pokemon['abilities']]
                imagen_url = datos_pokemon['sprites']['front_default']
                descripcion_pokedex = obtener_descripcion_pokedex(nombre)
                regiones_aparicion = obtener_region_aparicion(nombre)
                debilidades = obtener_debilidades(nombre)
                
                sugerencia = obtener_sugerencia(nombre)
                
                return render_template('resultado.html', 
                                       nombre=nombre,
                                       id_pokemon=id_pokemon,
                                       tipos=tipos,
                                       habilidades=habilidades,
                                       imagen_url=imagen_url,
                                       sugerencia=sugerencia,
                                       descripcion_pokedex=descripcion_pokedex,
                                       regiones_aparicion=regiones_aparicion,
                                       debilidades=debilidades,
                                       historial_busqueda=historial_busqueda)
        except requests.exceptions.HTTPError as e:
            return render_template('error.html', mensaje="Error al buscar Pokémon por tipo.")
    else:  # Si se está buscando por nombre
        url_base = "https://pokeapi.co/api/v2/pokemon/"
        url = url_base + nombre_pokemon
        try:
            respuesta = requests.get(url)
            respuesta.raise_for_status()  # Lanzar una excepción en caso de error de solicitud
            
            datos = respuesta.json()
            
            nombre = datos['name']
            id_pokemon = datos['id']
            tipos = [tipo['type']['name'] for tipo in datos['types']]
            habilidades = [habilidad['ability']['name'] for habilidad in datos['abilities']]
            imagen_url = datos['sprites']['front_default']
            descripcion_pokedex = obtener_descripcion_pokedex(nombre)
            regiones_aparicion = obtener_region_aparicion(nombre)
            debilidades = obtener_debilidades(nombre)
            
            sugerencia = obtener_sugerencia(nombre_pokemon)
            
            return render_template('resultado.html', 
                                   nombre=nombre,
                                   id_pokemon=id_pokemon,
                                   tipos=tipos,
                                   habilidades=habilidades,
                                   imagen_url=imagen_url,
                                   sugerencia=sugerencia,
                                   descripcion_pokedex=descripcion_pokedex,
                                   regiones_aparicion=regiones_aparicion,
                                   debilidades=debilidades,
                                   historial_busqueda=historial_busqueda)
        except requests.exceptions.HTTPError as e:
            sugerencia = obtener_sugerencia(nombre_pokemon)
            return render_template('error.html', mensaje=f"¡El Pokémon no fue encontrado! ¿Quisiste decir '{sugerencia}'?" if sugerencia else "¡El Pokémon no fue encontrado! Por favor, asegúrate de ingresar un nombre de Pokémon válido.")

@app.route('/comentar', methods=['POST'])
def comentar():
    comentario = request.form['comentario']
    try:
        cursor.execute("INSERT INTO Comentarios (comentario) VALUES (%s)", (comentario,))
        conexion.commit()
        return render_template('index.html', mensaje="¡Comentario guardado correctamente!")
    except mysql.connector.Error as error:
        return render_template('index.html', mensaje=f"Error al guardar comentario: {error}")

def obtener_sugerencia(nombre_pokemon):
    nombres_pokemon = obtener_nombres_pokemon()
    sugerencia = difflib.get_close_matches(nombre_pokemon, nombres_pokemon, n=1, cutoff=0.6)
    if sugerencia:
        return sugerencia[0]
    else:
        return None

def obtener_nombres_pokemon():
    url_base = "https://pokeapi.co/api/v2/pokemon?limit=1000"
    nombres_pokemon = []
    try:
        respuesta = requests.get(url_base)
        respuesta.raise_for_status()
        datos = respuesta.json()
        for pokemon in datos['results']:
            nombre = pokemon['name']
            nombres_pokemon.append(nombre)
    except requests.exceptions.RequestException as e:
        return []
    return sorted(nombres_pokemon)  # Devolver la lista de nombres de Pokémon ordenada alfabéticamente

def obtener_tipos_pokemon():
    url_base = "https://pokeapi.co/api/v2/type"
    tipos_pokemon = []
    try:
        respuesta = requests.get(url_base)
        respuesta.raise_for_status()
        datos = respuesta.json()
        for tipo in datos['results']:
            tipo_nombre = tipo['name']
            tipos_pokemon.append(tipo_nombre)
    except requests.exceptions.RequestException as e:
        return []
    return sorted(tipos_pokemon)  # Devolver la lista de tipos de Pokémon ordenada alfabéticamente

if __name__ == '__main__':
    app.run(debug=True)
