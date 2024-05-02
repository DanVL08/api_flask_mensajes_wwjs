from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow, fields
from config import config
import datetime
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root@localhost/prefeco_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
conexion = MySQL(app)
db = SQLAlchemy(app)
ma = Marshmallow(app)

#MODELOS
class Alumnos(db.Model):
    __tablename__ = 'alumnos'

    alumno_id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50))
    apellido1 = db.Column(db.String(50))
    apellido2 = db.Column(db.String(50))
    fecha_nacimiento = db.Column(db.Date)
    grado = db.Column(db.Integer)
    grupo = db.Column(db.String(10))
    matricula = db.Column(db.String(20))
    direccion = db.Column(db.String(100))
    telefono = db.Column(db.String(15))
    pagos = db.relationship('Pagos', backref='alumno')
#NECESITAMOS DESCUBRIR EL TIPO DE DATO PARA MONTO
class alumnoSchema(ma.Schema):
    class Meta:
        fields = ('alumno_id','nombre', 'apellido1','apellido2','fecha_nacimiento','grado','grupo','matricula','direccion','telefono')

alumno_schema =  alumnoSchema()
alumnos_schema =  alumnoSchema(many=True)

class Pagos(db.Model):
    __tablename__ = 'pagos'
    pago_id      = db.Column(db.Integer, primary_key=True)
    alumno_id    = db.Column(db.Integer, db.ForeignKey('alumnos.alumno_id'))
    matricula    = db.Column(db.String(20))
    fecha_pago   = db.Column(db.Date)
    monto        = db.Column(db.Numeric(10,2))
    metodo_pago  = db.Column(db.String(20))
    estado_pago  = db.Column(db.String(15))
    concepto_pago= db.Column(db.String(50))
class pagoSchema(ma.Schema):
    class Meta:
        fields = ('pago_id','alumno_id','matricula','fecha_pago','monto','metodo_pago','estado_pago','concepto_pago')#,'metodo_pago','estado_pago','concepto_pago

pago_schema =  pagoSchema()
pagos_schema =  pagoSchema(many=True)  

@app.route('/alumnos', methods=['GET'])
def get_alumnos_con_alchemy():
    all_alumnos = Alumnos.query.all()
    resultados = alumnos_schema.dump(all_alumnos)
    return jsonify({'alumnos':resultados})

@app.route('/alchemy-alumnos/<matricula>', methods=['GET'])
def leer_alumno_con_alchemy(matricula):
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

    try:
        cursor = conexion.connection.cursor()
        
        # Obtener el primer día del mes actual
        primer_dia_mes_actual = datetime.datetime.today().replace(day=1).date()
        
        # Obtener el último día del mes actual
        ultimo_dia_mes_actual = primer_dia_mes_actual.replace(day=28) + datetime.timedelta(days=4)
        ultimo_dia_mes_actual = ultimo_dia_mes_actual - datetime.timedelta(days=ultimo_dia_mes_actual.day)
        
        # Consultar la matrícula de los alumnos que han realizado un pago este mes
        sql = """
            SELECT DISTINCT alumnos.matricula
            FROM alumnos
            INNER JOIN pagos ON alumnos.alumno_id = pagos.alumno_id
            WHERE pagos.fecha_pago >= '{0}' AND pagos.fecha_pago <= '{1}'
        """.format(primer_dia_mes_actual, ultimo_dia_mes_actual)
        
        cursor.execute(sql)
        datos_alumnos = cursor.fetchall()
        
        # Crear lista de matrículas de alumnos con pago este mes
        matriculas_con_pago = [alumno[0] for alumno in datos_alumnos]
        
        # Crear objeto JSON de respuesta
        respuesta = {'matriculas_con_pago_mes_actual': matriculas_con_pago, 'mensaje': "Matrículas de alumnos con pago este mes"}
        return jsonify(respuesta)

    except Exception as ex:
        return jsonify({'mensaje': ex})


@app.route('/alumnos_con_pago_mes_actual', methods=['GET'])
def matriculas_pago_mes_actual():
    # Obtener el primer y último día del mes actual
    
    primer_dia_mes_actual = datetime.datetime.today().replace(day=1).date()
    print("primer dia: ", primer_dia_mes_actual)
    ultimo_dia_mes_actual = primer_dia_mes_actual.replace(day=28) + datetime.timedelta(days=4)
    ultimo_dia_mes_actual = ultimo_dia_mes_actual - datetime.timedelta(days=ultimo_dia_mes_actual.day)

    # Consulta SQLAlchemy equivalente
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