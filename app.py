import os
import requests
from flask import Flask, render_template, request, jsonify, redirect, url_for
from airtable import Airtable
app = Flask(__name__)

AIRTABLE_API_KEY = "keyKruB2figIcxSe0"
BASE_ID = "appe5NCnfkzZ0O2Dp"
TABLE_NAME = "productoSmartphones"
productos_seleccionados = []
products_table = Airtable(BASE_ID, TABLE_NAME, AIRTABLE_API_KEY)


criteria_weights = {
    "calidad_sonido": 1,
    "tipo": 1,
    "uso": 1,
    "comodidad": 1,
    "bateria": 1,
    "presupuesto":2,
}
criteria_ranges = {
    "calidad_sonido": 3,  # valores posibles: 1, 2, 3
    "tipo": 3,  # valores posibles: 1, 2, 3
    "uso": 3,  # valores posibles: 1, 2, 3
    "comodidad": 3,  # valores posibles: 1, 2, 3, 4
     "bateria": 3,
}



def calculate_similarity(criteria, product):
    total_points = 0
    max_points = 0

    for key, weight in criteria_weights.items():
        if key in product['fields']:
            criteria_value = criteria[key]
            product_value = product['fields'][key]

            if isinstance(criteria_value, str):
                if criteria_value == product_value:
                    similarity = 1
                else:
                    similarity = 0
            elif isinstance(criteria_value, (int, float)):
                value_range = criteria_ranges[key]  # Asumiendo que hay un diccionario con los rangos de valores para cada criterio
                similarity = 1 - (abs(criteria_value - product_value) / value_range)

            total_points += similarity * weight

        max_points += weight

    similarity_percentage = round((total_points / max_points) * 100,2)
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
        "calidad_sonido": request.form.get("calidad_sonido"),
        "tipo": request.form.get("tipo"),
        "uso": request.form.get("uso"),
        "comodidad": request.form.get("comodidad"),
        "bateria": request.form.get("bateria"),
        "presupuesto" : request.form.get("presupuesto"),
    }
    products = get_matching_products(criteria)
    if products:
        product_info = []
        for product in products:
             product_info.append({
                 "nombre": product['fields']['Name'],
                 "imagen": product['fields']['Assignee'][0]['url'],
                 "descripcion": product['fields']['Descripcion'],
                 "url": product['fields']['URL'],
                 "famosos": product['fields']['famouse_users'],
                 "youtubeVideo": product['fields']['youtubeVideo'],
                 "similitud": product['similitud']   # Porcentaje de simulitud que me faltaba
             })

        productos_seleccionados = product_info
        return redirect(url_for('resultado'))
    else:
        return jsonify({"error": "No se encontraron productos que coincidan con los criterios."})


@app.route("/resultado")
def resultado():
    return render_template("resultado.html", productos=productos_seleccionados)


if __name__ == "__main__":
    app.run(debug=True)