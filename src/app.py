from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
from config import config
app = Flask(__name__)

conexion = MySQL(app)

@app.route('/cursos', methods=['GET'])
def listar_cursos():
    try:
        cursor = conexion.connection.cursor()
        sql = "SELECT codigo, nombre, creditos FROM curso"
        cursor.execute(sql)
        datos = cursor.fetchall()
        cursos = []
        #AGREGAR LOS DATOS DEL CURSO A UN JSON
        for fila in datos:
            curso = {'codigo':fila[0], 'nombre':fila[1], 'creditos': fila[2]}
            cursos.append(curso)
        return jsonify({'cursos':cursos, 'mensaje':"Cursos listados!"})
    except Exception as ex:
        return jsonify({'mensaje':"Error"})

 #LEE UN SOLO CURSO Y LO MUESTRA    
@app.route('/cursos/<codigo>', methods=['GET'])
def leer_curso(codigo):
    try:
        cursor = conexion.connection.cursor()
        sql = "SELECT codigo, nombre, creditos FROM curso WHERE codigo = '{0}'".format(codigo)
        cursor.execute(sql)
        datos = cursor.fetchone()
        if datos != None:
            curso = {'codigo':datos[0], 'nombre':datos[1], 'creditos': datos[2]}
            return jsonify({'curso':curso, 'mensaje':"Curso encontrado!"})
    except Exception as ex:
        return jsonify({'mensaje':"Curso no encontrado!"})  
    
#REGISTRA UN NUEVO CURSO
@app.route('/cursos', methods=['POST'])
def registrar_curso():
    #print(request.json)
    try:
        cursor = conexion.connection.cursor()

        #TAREA COMPROBAR SI EL CURSO YA EXISTE PARA EVITAR ERRORES EN LA PETICION

        sql="""INSERT INTO curso (codigo, nombre, creditos) 
        VALUES ('{0}','{1}','{2}')""".format(request.json['codigo'], #INSERTA LOS VALORES DIRECTAMENTE DEL JSON
        request.json['nombre'], request.json['creditos'])
        cursor.execute(sql)
        conexion.connection.commit() #confirma la acción de inserción
        return jsonify({'mensaje':"Curso registrado!"})
    except Exception as ex:
        return jsonify({'mensaje':"Error"})

@app.route('/cursos/<codigo>', methods=['PUT'])
def actualizar_curso(codigo):
    try:
        cursor = conexion.connection.cursor()

        sql="""UPDATE curso SET nombre = '{0}', creditos = '{1}'
        WHERE  codigo = '{2}'""".format(request.json['nombre'], request.json['creditos'], codigo)
        cursor.execute(sql)
        conexion.connection.commit() #confirma la acción de inserción
        return jsonify({'mensaje':"Curso actualizado!"})
    except Exception as ex:
        return jsonify({'mensaje':"Error"})
    
#ELIMINA UN CURSO, SIMILAR A AGREGAR
@app.route('/cursos/<codigo>', methods=['DELETE'])
def eliminar_curso(codigo):
    try:
        cursor = conexion.connection.cursor()

        #TAREA COMPROBAR SI EL CURSO NO EXISTE PARA EVITAR EJECUTAR LA PETICION

        sql="DELETE FROM curso WHERE codigo = '{0}'".format(codigo)
        cursor.execute(sql)
        conexion.connection.commit() #confirma la acción de inserción
        return jsonify({'mensaje':"Curso eliminado"})
    except Exception as ex:
        return jsonify({'mensaje':"Error"})

 

#EN CASO QUE EL USUARIO ACCEDA A UNA RUTA NO ENCONTRADA
def pagina_no_encontrada(error):
    return "<h1>La pagina que intentas buscar no existe...</h1>",404 #Devuelve el mensaje y ademas el codigo de error a la peticion http


if  __name__ == '__main__':
    app.config.from_object(config['development'])
    app.register_error_handler(404,pagina_no_encontrada)
    app.run()