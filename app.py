import os
import requests
from flask import Flask, render_template, request, jsonify, redirect, url_for
from airtable import Airtable
import numpy as np
import openai

app = Flask(__name__)

AIRTABLE_API_KEY = "keyKruB2figIcxSe0"
BASE_ID = "appe5NCnfkzZ0O2Dp"
TABLE_NAME = "SMARTPHONES"
productos_seleccionados = []
products_table = Airtable(BASE_ID, TABLE_NAME, AIRTABLE_API_KEY)


value_mappings = {
    "Muy_bueno": 3,
    "Bueno": 2,
    "Basico": 1,
    "Grande": 3,
    "Mediana": 2,
    "Pequeno": 1,
    "Gama_alta": 3,
    "Gama_media": 2,
    "Gama_baja": 1,
}




criteria_weights = {
    "Rendimiento":1,
    "Tamano_de_pantalla": 1,
    "Calidad_de_camara": 1,
    "batería": 1,
    "calidad_const":1,
    "presupuesto": 4,
}
criteria_ranges = {
    "Rendimiento":3,
    "Tamano_de_pantalla": 3,
    "Calidad_de_camara": 3,
    "batería": 3,
    "calidad_const": 3,
    "presupuesto": 3,
}

import openai

""" def get_chatgpt_response(user_preferences):
    openai.api_key = "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"

    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=f"eres un experto en moviles necesito que des las razones por las cuales el producto({product[nombre]}) es el ideal para una esta persona/caso:{user_preferences}\n\nRespuesta:",
        temperature=0.7,
        max_tokens=150,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    ) """

def get_chatgpt_response(user_preferences, nombre_producto,descripcion):
    openai.api_key = "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"
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=f"eres un experto en moviles necesito que des las razones por las cuales el producto {nombre_producto} es ideal para esta persona considerando sus preferencias: {user_preferences}en base a la {descripcion}del producto\n\nRespuesta:",
        temperature=0.7,
        max_tokens=150,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    return response.choices[0].text.strip()





   # print("Entrada a ChatGPT:", user_preferences)  # Imprime la entrada a ChatGPT
    #print("Respuesta sin procesar de ChatGPT:", response.choices)  # Imprime la respuesta sin procesar de ChatGPT
    answer = response.choices[0].text.strip()
    return answer







def calculate_similarity(criteria, product):
    total_points = 0
    max_points = 0
    criteria_vector = []
    product_vector = []

    for key, weight in criteria_weights.items():
        if key in product['fields']:
            criteria_value = value_mappings[criteria[key]]
            product_value = value_mappings[product['fields'][key]]

            criteria_vector.append(criteria_value * weight)
            product_vector.append(product_value * weight)

    # Calcular la similitud del coseno
    similarity = np.dot(criteria_vector, product_vector) / (np.linalg.norm(criteria_vector) * np.linalg.norm(product_vector))
    similarity_percentage = round(similarity * 100, 2)
    return similarity_percentage






def get_matching_products(criteria):
    airtable_products = products_table.get_all()
    similarity_product_list = []  # Asegúrate de tener esta línea

    for product in airtable_products:
        similarity = calculate_similarity(criteria, product)
        product['similitud'] = similarity
        similarity_product_list.append((similarity, product))

    sorted_similarity_product_list = sorted(similarity_product_list, key=lambda x: x[0], reverse=True)
    top_3_products = [product[1] for product in sorted_similarity_product_list[:3]]

    return top_3_products



@app.route("/")
def index():
    return render_template("index.html")


@app.route("/submit", methods=["POST"])
def submit():
    global productos_seleccionados
    criteria = {
        "Rendimiento": request.form.get("Rendimiento"),
        "Tamano_de_pantalla": request.form.get("Tamano_de_pantalla"),
        "Calidad_de_camara": request.form.get("Calidad_de_camara"),
        "bateria": request.form.get("bateria"),
        "calidad_const": request.form.get("calidad_const"),
        "presupuesto": request.form.get("presupuesto"),
        
    }
    products = get_matching_products(criteria)
    if products:
        product_info = []
        for product in products:
             nombre = product['fields']['Modelo']
             descripcion=product['fields']['Descripcion']
             print(f"{nombre}")
             preferencias_usuario = request.form.get("preferencias")
             chatgpt_respuesta =  get_chatgpt_response(preferencias_usuario, nombre,descripcion)
             similarity = calculate_similarity(criteria, product)
             product['similarity'] = round(similarity * 100, 2)
             imagenes = product['fields'].get('imagenes')
             if imagenes and len(imagenes) > 0:
                imagen = imagenes[0]['url']
             else:
                imagen = None

             product_info.append({
                 "nombre": nombre,
                 #ahora se reciben 3 imagenees en vez de una
                 "imagen": imagen,
                 "descripcion": product['fields']['Descripcion'],
                 "url": product['fields']['URL'],
                 "famosos": product['fields']['famouse_users'],
                 "youtubeVideo": product['fields']['youtubeVideo'],
                 "similitud": product['similitud'],   # Porcentaje de simulitud que me faltaba
                
                 "chatgpt_response": chatgpt_respuesta,
             })

        productos_seleccionados = product_info
        return redirect(url_for('resultado', chatgpt_respuesta=chatgpt_respuesta))
    else:
        return jsonify({"error": "No se encontraron productos que coincidan con los criterios."})


@app.route("/resultado")
def resultado():
    chatgpt_respuesta = request.args.get('chatgpt_respuesta', None)
    return render_template("resultado.html", productos=productos_seleccionados,chatgpt_respuesta=chatgpt_respuesta)


if __name__ == "__main__":
    app.run(debug=True)