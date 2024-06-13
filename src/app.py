from flask import Flask, jsonify, request, redirect, url_for, flash, render_template
from flask_mysqldb import MySQL
from models import db, ma, Alumnos, Pagos, alumnoSchema, pagoSchema
from config import config
import datetime
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root@localhost/prefeco_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#settings
app.secret_key = 'mysecretkey'
conexion = MySQL(app)
db.init_app(app)
ma.init_app(app)

alumno_schema =  alumnoSchema()
alumnos_schema =  alumnoSchema(many=True)

pago_schema =  pagoSchema()
pagos_schema =  pagoSchema(many=True)
#RUTAS DE VISTA DE USUARIO

#RUTAS DE TABLAS
#devuelve la ruta con la tabla
@app.route('/tabla-alumnos')
def mostrar_tabla_alumnos():
    return render_template('tabla-alumnos.html', title='Alumnos')

@app.route('/tabla-pagos')
def mostrar_tabla_pagos():
    return render_template('tabla-pagos.html', title ='Pagos')

#devuelve la informacion de los alumnos
@app.route('/api/data/alumnos')
def data_alumnos():
    return {'data': [alumno.to_dict() for alumno in Alumnos.query]}

@app.route('/api/data/pagos')
def data_pagos():
    return {'data': [pagos.to_dict() for pagos in Pagos.query]}
#RUTA INICIO, aparecerá la pantalla para mostrar o registrar alumnos
@app.route('/')
def index():
    #SE OBTIENEN LOS DATOS DE LA BD Y SE RETORNAN PLASMADOS EN index.html
    try:
        resultados = obtener_datos_de_alumnos()
        datos_formulario = request.args.get('datos_formulario', None)
        return render_template('index.html', alumnos = resultados, datos_formulario=datos_formulario)
    except Exception as e:
        flash(e)
        return redirect(url_for('index'))

#FUNION PARA OBTENER LOS DATOS DE LOS ALUMNOS
def obtener_datos_de_alumnos():
    try:
        all_alumnos = Alumnos.query.all()
        resultados = alumnos_schema.dump(all_alumnos)
        return resultados
    except Exception as e:
        flash(e)
        return redirect(url_for('index'))
    
#RUTA PARA AÑADIR ALUMNOS NUEVOS
@app.route('/add_alumno', methods=['POST'])
def add_alumno():
    if request.method == 'POST':
        try:
            alumno = Alumnos.query.filter_by(matricula=request.form['matricula']).first()
            if not alumno:
                alumno = Alumnos(
                    nombre=request.form['nombres'],
                    apellido1=request.form['apellido1'],
                    apellido2=request.form['apellido2'],
                    fecha_nacimiento=request.form['fecha_nacimiento'],
                    grado=request.form['grado'],
                    grupo=request.form['grupo'],
                    matricula=request.form['matricula'],
                    direccion=request.form['direccion'],
                    telefono=request.form['telefono']
                )
                db.session.add(alumno)
                db.session.commit()

                flash('Alumno agregado satisfactoriamente')
                return redirect(url_for('index'))
            else:
                flash(f"La matricula {alumno.matricula} ya está registrada en la base de datos")
                alumnos = obtener_datos_de_alumnos()
                return render_template('index.html', alumnos = alumnos, datos_formulario=request.form)
        except Exception as e:
            flash(e)
            return redirect(url_for('index'))
    #SOLICITAR LOS DATOS DEL FORMULARIO DE index.html
    if request.method == 'POST':
        try:
            #COMPRUEBA SI YA EXISTE UN ALUMNO EN LA BD
            alumno = Alumnos.query.filter_by(matricula = request.form['matricula']).first()
            if not alumno:
                # Crear una instancia de la clase Alumnos con atributos asignados
                alumno = Alumnos(
                    nombre          = request.form['nombres'],
                    apellido1       = request.form['apellido1'],
                    apellido2       = request.form['apellido2'],
                    fecha_nacimiento= request.form['fecha_nacimiento'],
                    grado           = request.form['grado'],
                    grupo           = request.form['grupo'],
                    matricula       = request.form['matricula'],
                    direccion       = request.form['direccion'],
                    telefono        = request.form['telefono']
                )
                
                db.session.add(alumno)
                db.session.commit()

                flash('Contacto agregado satisfactoriamente')
                return redirect(url_for('index'))
            else:
                flash(f"La matricula {alumno.matricula} ya está registrada en la base de datos")
                return redirect(url_for('index'))
        except Exception as e:
            flash(e)
            return redirect(url_for('index'))
        
#EJECUTA LA CONSULTA SQL PARA OBTENER UN ALUMNO PARA EDITAR
@app.route('/edit-alumno/<id>')
def get_alumno(id):
        try:
            alumno_bd = Alumnos.query.filter_by(alumno_id = id).first()
            return render_template('editar-alumno.html',alumno = alumno_bd)
        except Exception as e:
            flash(e)

#SE ENCARGA DE ENVIAR LOS DATOS ACTUALIZADOS DEL FORMULARIO A LA BD
@app.route('/update-alumno/<id>', methods = ['POST'])
def update_alumno(id):
    #SOLICITAR LOS DATOS DEL FORMULARIO DE editar-alumno.html
    if request.method == 'POST':
        try:
            alumno = Alumnos.query.get(id) 
            alumno.nombre = request.form['nombres']
            alumno.apellido1 = request.form['apellido1']
            alumno.apellido2 = request.form['apellido2']
            alumno.fecha_nacimiento = request.form['fecha_nacimiento']
            alumno.grado = request.form['grado']
            alumno.grupo = request.form['grupo']
            alumno.matricula = request.form['matricula']
            alumno.direccion = request.form['direccion']
            alumno.telefono = request.form['telefono']
            
            db.session.commit()
            flash('Alumno actualizado satisfactoriamente.')
            return(redirect(url_for('index')))
        except Exception as e:
            flash(e)
            return redirect(url_for('index'))
            
#ELIMINA UN ALUMNO A APARTIR DE SI ID
@app.route('/delete-alumno/<int:id>', methods=['DELETE'])
def delete_alumno(id):
    try:
        # Buscar el alumno por ID
        alumno = Alumnos.query.filter_by(alumno_id=id).first()
        
        # Verificar si el alumno existe
        if alumno:
            db.session.delete(alumno)
            db.session.commit()
            return jsonify({"message": "Alumno eliminado exitosamente"}), 200
        else:
            return jsonify({"error": "Alumno no encontrado"}), 404
    
    except Exception as e:
        # Loguear la excepción para depuración
        app.logger.error(f"Error al eliminar el alumno: {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500
#RUTA INICIO, aparecerá la pantalla para mostrar o registrar pagos
@app.route('/pagos')
def index_pagos():
    #SE OBTIENEN LOS DATOS DE LA BD Y SE RETORNAN PLASMADOS EN pagos.html
    try:
        all_pagos = Pagos.query.all()
        resultados = pagos_schema.dump(all_pagos)
        return render_template('pagos.html', pagos = resultados)
    except Exception as e:
        flash(e)
        return redirect(url_for('index'))

#RUTA PARA AÑADIR ALUMNOS NUEVOS
@app.route('/add_pago', methods=['POST'])
def add_pago():
    #SOLICITAR LOS DATOS DEL FORMULARIO DE index.html
    if request.method == 'POST':
        try:
            alumno = Alumnos.query.filter_by(matricula = request.form['matricula']).first()
            if alumno:
                # Crear una instancia de la clase Alumnos con atributos asignados
                pago = Pagos(
                    matricula     = request.form['matricula'],
                    alumno_id     = alumno.alumno_id,
                    fecha_pago    = request.form['fecha_pago'],
                    monto         = request.form['monto'],
                    metodo_pago   = request.form['metodo_pago'],
                    estado_pago   = request.form['estado_pago'],
                    concepto_pago = request.form['concepto_pago'],
                )
                
                db.session.add(pago)
                db.session.commit()

                flash('Pago agregado satisfactoriamente')
                return redirect(url_for('index_pagos'))
            else:
                flash('Matricula no encontrada!!!!!')
                return redirect(url_for('index_pagos'))
        except Exception as e:
            flash(e)
            return redirect(url_for('index_pagos'))

#EJECUTA LA CONSULTA SQL PARA OBTENER UN ALUMNO PARA EDITAR
@app.route('/editar-pago/<id>')
def get_pago(id):
        try:
            print(id)
            pago_bd = Pagos.query.filter_by(pago_id = id).first()
            return render_template('editar-pago.html', pago = pago_bd)
        except Exception as e:
            flash(e)

#SE ENCARGA DE ENVIAR LOS DATOS ACTUALIZADOS DEL FORMULARIO A LA BD
@app.route('/update-pago/<id>', methods = ['POST'])
def update_pago(id):
    #SOLICITAR LOS DATOS DEL FORMULARIO DE editar-alumno.html
    if request.method == 'POST':
        try:
            pago = Pagos.query.get(id)
            pago.matricula = request.form['matricula']
            pago.fecha_pago = request.form['fecha_pago']
            pago.monto = request.form['monto']
            pago.metodo_pago = request.form['metodo_pago']
            pago.estado_pago = request.form['estado_pago']
            pago.concepto_pago = request.form['concepto_pago']
            
            db.session.commit()
            flash('Pago actualizado satisfactoriamente.')
            return(redirect(url_for('index_pagos')))
        except Exception as e:
            flash(e)
            return redirect(url_for('index_pagos')) 

#ELIMINA UN ALUMNO A APARTIR DE SI ID
@app.route('/borrar-pago/<int:id>', methods=['DELETE'])
def delete_pago(id):
    try:
        # Buscar el pago por ID
        pago = Pagos.query.filter_by(pago_id=id).first()
        
        # Verificar si el pago existe
        if pago:
            db.session.delete(pago)
            db.session.commit()
            return jsonify({"message": "Pago eliminado exitosamente"}), 200
        else:
            return jsonify({"error": "Pago no encontrado"}), 404
    
    except Exception as e:
        # Loguear la excepción para depuración
        app.logger.error(f"Error al eliminar el pago: {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500
#######################################
#ENDOPOINTS PARA CONSULTAR INFORMACIÓN#
#######################################

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