from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
from config import config
import datetime
app = Flask(__name__)

conexion = MySQL(app)

@app.route('/alumnos', methods=['GET'])
def listar_alumnos():
    try:
        cursor = conexion.connection.cursor()
        sql = "SELECT nombre, apellido1, matricula FROM alumnos"
        cursor.execute(sql)
        datos = cursor.fetchall()
        alumnos = []
        #AGREGAR LOS DATOS DE LOS ALUMNOS A UN JSON
        for fila in datos:
            alumno = {'nombre':fila[0], 'apellido1':fila[1], 'matricula': fila[2]}
            alumnos.append(alumno)
        return jsonify({'alumnos':alumnos, 'mensaje':"Alumnos listados!"})
    except Exception as ex:
        return jsonify({'mensaje':"Error"})

 #LEE UN SOLO ALUMNO Y LO MUESTRA    
@app.route('/alumnos/<matricula>', methods=['GET'])
def leer_alumno(matricula):
    try:
        cursor = conexion.connection.cursor()
        sql = "SELECT nombre, apellido1, matricula FROM alumnos WHERE matricula = '{0}'".format(matricula)
        cursor.execute(sql)
        datos = cursor.fetchone()
        if datos != None:
            alumno = {'nombre':datos[0], 'apellido1':datos[1], 'matricula': datos[2]}
            return jsonify({'alumno':alumno, 'mensaje':"alumno encontrado!"})
    except Exception as ex:
        return jsonify({'mensaje':"alumno no encontrado!"})  

@app.route('/pagos/<matricula>', methods=['GET'])
def consultar_pagos(matricula):
    try:
        cursor = conexion.connection.cursor()
        
        # Consultar el ID del alumno, nombre y apellido a partir de la matrícula
        sql_id_alumno = "SELECT alumno_id, nombre, apellido1 FROM alumnos WHERE matricula = '{0}'".format(matricula)
        cursor.execute(sql_id_alumno)
        datos_id_alumno = cursor.fetchone()
        
        if datos_id_alumno is not None:
            alumno_id = datos_id_alumno[0]
            nombre = datos_id_alumno[1]
            apellido1 = datos_id_alumno[2]
            
            # Consultar los pagos del alumno a partir de su ID
            sql_pagos = "SELECT fecha_pago, monto, estado_pago FROM pagos WHERE alumno_id = '{0}'".format(alumno_id)
            cursor.execute(sql_pagos)
            datos_pagos = cursor.fetchall()
            
            # Crear lista de pagos
            pagos = []
            for pago in datos_pagos:
                pagos.append({'fecha_pago': pago[0], 'monto': pago[1], 'estado_pago': pago[2]})
            
            # Crear objeto JSON de respuesta
            respuesta = {'alumno_id': alumno_id, 'nombre': nombre, 'apellido1': apellido1, 'pagos': pagos}
            return jsonify(respuesta)
        
        else:
            return jsonify({'mensaje': "Alumno no encontrado"})
    
    except Exception as ex:
        return jsonify({'mensaje': "Error al consultar los pagos del alumno"})


@app.route('/pagos_mes_actual/<matricula>', methods=['GET'])
def pagos_mes_actual(matricula):
    try:
        cursor = conexion.connection.cursor()
        
        # Obtener el primer día del mes actual
        primer_dia_mes_actual = datetime.datetime.today().replace(day=1)
        
        # Obtener el último día del mes actual
        ultimo_dia_mes_actual = primer_dia_mes_actual.replace(day=28) + datetime.timedelta(days=4)
        ultimo_dia_mes_actual = ultimo_dia_mes_actual - datetime.timedelta(days=ultimo_dia_mes_actual.day)
        
        # Consultar los pagos del alumno para el mes actual
        sql = """
            SELECT fecha_pago, monto, estado_pago
            FROM pagos
            WHERE alumno_id = (SELECT alumno_id FROM alumnos WHERE matricula = '{0}')
            AND fecha_pago >= '{1}' AND fecha_pago <= '{2}'
        """.format(matricula, primer_dia_mes_actual, ultimo_dia_mes_actual)
        
        cursor.execute(sql)
        datos_pagos = cursor.fetchall()
        
        # Crear lista de pagos del alumno
        pagos = [{'fecha_pago': pago[0], 'monto': pago[1], 'estado_pago': pago[2]} for pago in datos_pagos]
        
        # Crear objeto JSON de respuesta
        respuesta = {'pagos_mes_actual': pagos, 'mensaje': f"Pagos del alumno con matrícula {matricula} para el mes actual"}
        return jsonify(respuesta)

    except Exception as ex:
        return jsonify({'mensaje': "Error al consultar los pagos"})

#EN CASO QUE EL USUARIO ACCEDA A UNA RUTA NO ENCONTRADA
def pagina_no_encontrada(error):
    return "<h1>La pagina que intentas buscar no existe...</h1>",404 #Devuelve el mensaje y ademas el codigo de error a la peticion http


if  __name__ == '__main__':
    app.config.from_object(config['development'])
    app.register_error_handler(404,pagina_no_encontrada)
    app.run()