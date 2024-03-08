from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
from config import config
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

#EN CASO QUE EL USUARIO ACCEDA A UNA RUTA NO ENCONTRADA
def pagina_no_encontrada(error):
    return "<h1>La pagina que intentas buscar no existe...</h1>",404 #Devuelve el mensaje y ademas el codigo de error a la peticion http


if  __name__ == '__main__':
    app.config.from_object(config['development'])
    app.register_error_handler(404,pagina_no_encontrada)
    app.run()