from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
from models import db, ma, Alumnos, Pagos, alumnoSchema, pagoSchema
from config import config
import datetime
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root@localhost/prefeco_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
conexion = MySQL(app)
db.init_app(app)
ma.init_app(app)

alumno_schema =  alumnoSchema()
alumnos_schema =  alumnoSchema(many=True)

pago_schema =  pagoSchema()
pagos_schema =  pagoSchema(many=True)  

@app.route('/alumnos', methods=['GET'])
def get_alumnos_con_alchemy():
    all_alumnos = Alumnos.query.all()
    resultados = alumnos_schema.dump(all_alumnos)
    return jsonify({'alumnos':resultados})

@app.route('/alumnos/<matricula>', methods=['GET'])
def leer_alumno(matricula):
    try:
        alumno = Alumnos.query.filter_by(matricula=matricula).one_or_404()
        respuesta = alumno_schema.dump(alumno)
        return jsonify({'alumno':respuesta})
    except Exception as ex:
        return jsonify({'error':ex})

#AHORA QUIERO OBTENER UN SOLO PAGO
#FUENTE:https://www.youtube.com/watch?v=VVX7JIWx-ss
@app.route('/pagos/<matricula>', methods=['GET'])
def obtener_pagos(matricula):
    try:
        alumno = Alumnos.query.filter_by(matricula=matricula).one_or_404()
        alumno_respuesta = alumno_schema.dump(alumno)
        pagos = Pagos.query.filter_by(matricula=matricula)
        pagos_respuesta = pagos_schema.dump(pagos)

        respuesta_final = {
           'alumno_id': alumno_respuesta['alumno_id'],
           'nombre': alumno_respuesta['nombre'],
           'apellido1': alumno_respuesta['apellido1'],
            "pagos":pagos_respuesta
        }
        return jsonify(respuesta_final)
    except Exception as ex:
        return({'Ocurrio un error al consultar los datos del alumno': ex})


@app.route('/alumnos_con_pago_mes_actual', methods=['GET'])
def matriculas_pago_mes_actual():
    # Obtener el primer y último día del mes actual
    
    primer_dia_mes_actual = datetime.datetime.today().replace(day=1).date()
    print("primer dia: ", primer_dia_mes_actual)
    ultimo_dia_mes_actual = primer_dia_mes_actual.replace(day=28) + datetime.timedelta(days=4)
    ultimo_dia_mes_actual = ultimo_dia_mes_actual - datetime.timedelta(days=ultimo_dia_mes_actual.day)

    # Consulta SQLAlchemy Para obtener los alumnos con pago
    matriculas = db.session.query(Alumnos.matricula).join(Pagos, Alumnos.alumno_id == Pagos.alumno_id).filter(
        Pagos.fecha_pago >= primer_dia_mes_actual,
        Pagos.fecha_pago <= ultimo_dia_mes_actual
    ).distinct().all()

    # Convertir los resultados en una lista plana de matrículas
    matriculas_list = [matricula[0] for matricula in matriculas]

    return jsonify({"matriculas_con_pago_mes_actual": matriculas_list,'mensaje': "Matrículas de alumnos con pago este mes"})

#EN CASO QUE EL USUARIO ACCEDA A UNA RUTA NO ENCONTRADA
def pagina_no_encontrada(error):
    return "<h1>La pagina que intentas buscar no existe...</h1>",404 #Devuelve el mensaje y ademas el codigo de error a la peticion http


if  __name__ == '__main__':
    app.config.from_object(config['development'])
    app.register_error_handler(404,pagina_no_encontrada)
    app.run()