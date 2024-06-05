from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
db = SQLAlchemy()
ma = Marshmallow()

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
    #De aqui obtngo el diccionario
    def to_dict(self):
        return {
            'alumno_id':self.alumno_id,
            'nombre': self.nombre,
            'apellido1': self.apellido1,
            'apellido2': self.apellido2,
            'telefono': self.telefono,
            'direccion': self.direccion
        }

class alumnoSchema(ma.Schema):
    class Meta:
        fields = ('alumno_id','nombre', 'apellido1','apellido2','fecha_nacimiento','grado','grupo','matricula','direccion','telefono')

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
