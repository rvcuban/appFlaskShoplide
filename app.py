import os
import requests
from flask import Flask, render_template, request, jsonify, redirect, url_for

app = Flask(__name__)

AIRTABLE_API_KEY = "keyKruB2figIcxSe0"
BASE_ID = "appe5NCnfkzZ0O2Dp"
TABLE_NAME = "productoAuriculares"



@app.route("/")
def home():
    return render_template("index.html")



def get_matching_product(criteria):
    url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}"
    }
    response = requests.get(url, headers=headers)
    records = response.json().get("records", [])

    for record in records:
        fields = record.get("fields")
        if all(fields.get(key) == value for key, value in criteria.items()):
            return record

    return None

@app.route('/submit', methods=['POST'])
def submit():
    criteria = {
        "calidad_sonido": request.form.get("calidad_sonido"),
        "tipo": request.form.get("tipo"),
        "uso": request.form.get("uso"),
        "comodidad": request.form.get("comodidad"),
        "bateria": request.form.get("bateria"),
    }
    product = get_matching_product(criteria)
    if product:
        return redirect(url_for('resultado', producto_nombre=product['fields']['Name'], producto_imagen=product['fields']['Assignee'][0]['url'], producto_descripcion=product['fields']['Descripcion']))
    else:
        return jsonify({"error": "No se encontró un producto que coincida con los criterios."})



# Nueva ruta 'resultado'
@app.route('/resultado', methods=['GET'])
def resultado():
    producto_nombre = request.args.get("producto_nombre")
    producto_imagen = request.args.get("producto_imagen")
    return render_template('resultado.html', producto_nombre=producto_nombre, producto_imagen=producto_imagen)




if __name__ == "__main__":
    app.run(debug=True)