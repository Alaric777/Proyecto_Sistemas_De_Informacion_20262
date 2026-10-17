import os
from datetime import date, datetime
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_file
from psycopg.errors import UniqueViolation

load_dotenv()
app = Flask(__name__)

@app.get('/')
def inicio():
    return send_file(Path(__file__).with_name('index.html'))

@app.post('/api/huespedes')
def registrar():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error='Se requiere un JSON válido.'), 400
    campos = ['Nombres','Apellidos','Tipo_Documento','Numero_Documento',
              'Fecha_Arrendamiento','Lugar_Provenida','Lugar_Partida']
    if any(not isinstance(data.get(k), str) or not data[k].strip() for k in campos):
        return jsonify(error='Completa todos los campos obligatorios.'), 400
    limites = {'Nombres':250,'Apellidos':250,'Tipo_Documento':50,
               'Numero_Documento':50,'Lugar_Provenida':250,'Lugar_Partida':250}
    if any(len(data[k]) > n for k,n in limites.items()):
        return jsonify(error='Uno de los campos supera su longitud máxima.'), 400
    try:
        fecha = date.fromisoformat(data['Fecha_Arrendamiento'])
        checkout = datetime.fromisoformat(data['fecha_Checkout']) if data.get('fecha_Checkout') else None
        if checkout and checkout.date() < fecha:
            return jsonify(error='La salida no puede ser anterior al alojamiento.'), 400
    except (ValueError, TypeError):
        return jsonify(error='Formato de fecha inválido.'), 400
    try:
        with psycopg.connect(os.environ['DATABASE_URL']) as conn:
            with conn.cursor() as cur:
                cur.execute("""INSERT INTO Usuario_hostal
                    (Nombres, Apellidos, Tipo_Documento, Numero_Documento,
                     Fecha_Arrendamiento, Lugar_Provenida, Lugar_Partida, fecha_Checkout)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                    RETURNING Id_Usuario_hostal""",
                    (data['Nombres'].strip(),data['Apellidos'].strip(),
                     data['Tipo_Documento'].strip(),data['Numero_Documento'].strip(),
                     fecha,data['Lugar_Provenida'].strip(),data['Lugar_Partida'].strip(),checkout))
                nuevo_id = cur.fetchone()[0]
        return jsonify(id=nuevo_id, mensaje='Registro guardado'), 201
    except UniqueViolation:
        return jsonify(error='Ya existe un huésped con ese tipo y número de documento.'), 409
    except (psycopg.Error, KeyError):
        app.logger.exception('Error de base de datos')
        return jsonify(error='No se pudo guardar. Revisa la conexión con PostgreSQL.'), 500

if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_DEBUG') == '1')
