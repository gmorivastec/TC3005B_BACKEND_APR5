# este es un comentario
#1ero - importar código necesario
from flask import Flask, jsonify
from markupsafe import escape
from flask_db2 import DB2
import sys 
from flask_cors import CORS, cross_origin
import sqlalchemy
from sqlalchemy import *
import ibm_db_sa
import flask_login
import secrets 
import flask
from argon2 import PasswordHasher
import time

# 2do - creamos un objeto de tipo flask
app = Flask(__name__)

# APLICAR CONFIG DE DB2
app.config['DB2_DATABASE'] = 'testdb'
app.config['DB2_HOSTNAME'] = 'localhost'
app.config['DB2_PORT'] = 50000
app.config['DB2_PROTOCOL'] = 'TCPIP'
app.config['DB2_USER'] = 'db2inst1'
app.config['DB2_PASSWORD'] = 'hola'

db = DB2(app)

CORS(app)

# CÓDIGO PARA LOGIN 
# necesitamos una llave secreta 
app.secret_key = secrets.token_urlsafe(16)
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

# PSEUDO BASE DE DATOS DE USUARIOS
usuarios = {"a@a.com" : {"pass" : "hola"}}

# definir una clase para contener la descripción de nuestros usuarios
class Usuario(flask_login.UserMixin):
    pass

# pass - keyword en python que significa que no haga nada.

# 2 callbacks necesarios para la lógica de control de usuarios
# user_loader
# request_loader
# los 2 usan el patron decorator 

@login_manager.user_loader
def user_loader(email):
    # verificar vs fuente de datos 
    if email not in usuarios:
        return
    
    usuario = Usuario()
    usuario.id = email
    return usuario

# método que se invoca para obtención de usuarios cuando se hace request
@login_manager.request_loader
def request_loader(request):

    # recibimos token de encabezado

    # verificamos vs base de datos validez de token

    # regresamos objeto si hubo Y token valido 

    # None si no 
    
    # obtener información que nos mandan en encabezado
    key = request.headers.get('Authorization')
    print(key, file=sys.stdout)


    if key == ":":
        return None

    processed = key.split(":")

    if processed[0] in usuarios and processed[1] == usuarios[processed[0]]['pass']:
        user = Usuario()
        user.id = processed[0]
        return user

    return None

@app.route('/login', methods=['POST'])
def login():
    
    # intro al password hasher
    ph = PasswordHasher()

    # como hashear
    hash = ph.hash("HOLA")
    print(hash, file=sys.stdout)

    hash = ph.hash("HOLA")
    print(hash, file=sys.stdout)

    hash = ph.hash("HOLA")
    print(hash, file=sys.stdout)

    # como comprobar que un valor es el mismo que uno ya hasheado
    try:
        print(ph.verify(hash, "ADIOS"), file=sys.stdout)
    except:
        print("NO ES IGUAL", file=sys.stdout)

    email = flask.request.form['email']

    # 1. verificar existencia de usuario
    cur = db.connection.cursor()

    query = "SELECT * FROM users WHERE email=?"
    
    # vamos a usar prepared statements
    # nos permite parametrizar un query
    # evita inyecciones de SQL

    # tupla de python - estructura de datos lineal que contiene 
    # datos heterogéneos
    params = (email, )

    cur.execute(query, params)
    data = cur.fetchone()
    cur.close()

    if(data == None):
        return "USUARIO NO VALIDO", 401

    print(data, file=sys.stdout)
    print(len(data), file=sys.stdout)

    # 2. verificar validez de password
    try:
        ph.verify(data[2], flask.request.form['pass'])
    except:
        # 3. password invalido - no login
        return "PASSWORD NO VALIDO", 401

    # 4. password valido - actualizar token y regresarlo
    token = secrets.token_urlsafe(32)
    # así se obtiene el timestamp del momento actual
    last_date = time.time()
    
    # 5. actualizar BD con entrada de usuario
    cur = db.connection.cursor()
    query = "UPDATE users SET token=?, last_date=? WHERE email=?"
    params = (ph.hash(token), last_date, email)
    cur.execute(query, params)
    cur.close()
    
    # si no jaló mostrar error
    return token, 200

@app.route('/protegido')
@cross_origin()
def protegido():
    return jsonify(protegido=flask_login.current_user.is_authenticated)

@login_manager.unauthorized_handler
def handler():
    return 'No autorizado', 401

@app.route('/logout')
def logout():
    flask_login.logout_user()
    return 'saliste'

# 3ero - al objeto de tipo flask le agregamos rutas
# @ en python significa que vamos a usar un decorator
# https://en.wikipedia.org/wiki/Decorator_pattern

@app.route("/")
def servicio_default():

    # lo primero es obtener cursor 
    cur = db.connection.cursor()

    # con cursor hecho podemos ejecutar queries
    cur.execute("SELECT * FROM gatitos")

    # obtenemos datos
    data = cur.fetchall()

    # acuerdate de cerrar el cursor
    cur.close()

    print(data, file=sys.stdout)

    # puedes checar alternativas para mapeo de datos
    # por hoy vamos a armar un objeto jsoneable para regresar 
    resultado = []
    for current in data:
        actual = {
            "id" : current[0],
            "nombre" : current[1],
            "peso" : current[2]
        }
        resultado.append(actual)

    return jsonify(resultado)

# podemos tener todas las rutas
@app.route("/segunda")
def segunda_ruta():
    engine = sqlalchemy.create_engine("ibm_db_sa://db2inst1:hola@localhost:50000/testdb")
    connection = engine.connect()
    metadata = sqlalchemy.MetaData()
    gatitos = Table('gatitos', metadata,
        Column('id', Integer, primary_key=True),
        Column('nombre', String(150), nullable=False),
        Column('peso', Integer, nullable=False)
    )

    query = sqlalchemy.select([gatitos])
    cursor = connection.execute(query)
    resultados = cursor.fetchall()

    print(resultados, file=sys.stdout)

    return "<h1>UNA SEGUNDA RUTA</h1>"

# podemos recibir variables a través de URL
# f-string formatting
# &eacute; & e acute; - e con acento agudo
# ataque por inyección de código
@app.route("/nombre/<el_nombre>/<el_apellido>")
def nombre(el_nombre, el_apellido):
    return f"Hola {escape(el_nombre)} {escape(el_apellido)}, espero que est&eacute;s bien."

# converters 
@app.route("/entero/<int:valor>")
def entero(valor):
    return f"el valor que mandaste fue: {escape(valor)}"

@app.route("/ruta/<path:valor>")
def ruta(valor):
    return f"la ruta que mandaste fue: {escape(valor)}"

# LO QUE VAMOS A REGRESAR GENERALMENTE VA A SER JSON
# ventaja de flask - regresar un diccionario de python se jsonifica

diccionario = {
    "nombre" : "Garfiol",
    "edad" : 30,
    "peso" : 64
}

@app.route("/json")
def json():
    return diccionario

# se puede discriminar por medio de método de request de HTTP
# (GET, POST, PUT, DELETE)

@app.route("/metodo", methods=["GET", "POST"])
def metodo_get_post():
    return "REQUEST HECHA POR GET O POST"

@app.route("/metodo", methods=["PUT", "DELETE"])
def metodo_put_delete():
    return "REQUEST HECHA POR PUT O DELETE"

# EXTENSION DE VS CODE - THUNDERCLIENT