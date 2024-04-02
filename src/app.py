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
        sql = "SELECT nombre, apellido1, matricula, telefono FROM alumnos"
        cursor.execute(sql)
        datos = cursor.fetchall()
        alumnos = []
        #AGREGAR LOS DATOS DE LOS ALUMNOS A UN JSON
        for fila in datos:
            alumno = {'nombre':fila[0], 'apellido1':fila[1], 'matricula': fila[2],'telefono': fila[3]}
            alumnos.append(alumno)
        return jsonify({'alumnos':alumnos})
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

@app.route('/alumnos_con_pago_mes_actual', methods=['GET'])
def alumnos_con_pago_mes_actual():
    try:
        cursor = conexion.connection.cursor()
        
        # Obtener el primer día del mes actual
        primer_dia_mes_actual = datetime.datetime.today().replace(day=1)
        
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
        return jsonify({'mensaje': "Error al consultar las matrículas de alumnos con pago este mes"})

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

#EN CASO QUE EL USUARIO ACCEDA A UNA RUTA NO ENCONTRADA
def pagina_no_encontrada(error):
    return "<h1>La pagina que intentas buscar no existe...</h1>",404 #Devuelve el mensaje y ademas el codigo de error a la peticion http


if  __name__ == '__main__':
    app.config.from_object(config['development'])
    app.register_error_handler(404,pagina_no_encontrada)
    app.run()