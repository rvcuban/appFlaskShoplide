import os
import requests
from flask import Flask, render_template, request, jsonify, redirect, url_for

app = Flask(__name__)

AIRTABLE_API_KEY = "keyKruB2figIcxSe0"
BASE_ID = "appe5NCnfkzZ0O2Dp"
TABLE_NAME = "productoAuriculares"
productos_seleccionados = []

@app.route("/")
def home():
    return render_template("index.html")

def get_matching_products(criteria):
    url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}"
    }
    response = requests.get(url, headers=headers)
    records = response.json().get("records", [])

    matching_products = []
    for record in records:
        fields = record.get("fields")
        if all(fields.get(key, None) == value for key, value in criteria.items()):
            matching_products.append(record)

    return matching_products[:3] if matching_products else None

@app.route('/submit', methods=['POST'])
def submit():
    global productos_seleccionados
    criteria = {
        "calidad_sonido": request.form.get("calidad_sonido"),
        "tipo": request.form.get("tipo"),
        "uso": request.form.get("uso"),
        "comodidad": request.form.get("comodidad"),
        "bateria": request.form.get("bateria"),
        
    }
    products = get_matching_products(criteria)
    if products:
        product_info = []
        for product in products:
            product_info.append({
                "nombre": product['fields']['Name'],
                "imagen": product['fields']['Assignee'][0]['url'],
                "descripcion": product['fields']['Descripcion'],
                "url": product['fields']['URL']
            })
        productos_seleccionados = product_info
        return redirect(url_for('resultado'))
    else:
        return jsonify({"error": "No se encontraron productos que coincidan con los criterios."})

@app.route('/resultado', methods=['GET'])
def resultado():
    global productos_seleccionados
    return render_template('resultado.html', productos=productos_seleccionados)

if __name__ == "__main__":
    app.run(debug=True)
