# este es un comentario
#1ero - importar código necesario
from flask import Flask
from markupsafe import escape

# 2do - creamos un objeto de tipo flask
app = Flask(__name__)

# 3ero - al objeto de tipo flask le agregamos rutas
# @ en python significa que vamos a usar un decorator
# https://en.wikipedia.org/wiki/Decorator_pattern

@app.route("/")
def servicio_default():
    return "HOLA A TODOS <a href='/segunda'>segunda</a>"

# podemos tener todas las rutas
@app.route("/segunda")
def segunda_ruta():
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