from flask import Flask
import os
from dotenv import load_dotenv
from config.db import init_db, mysql
from flask_jwt_extended import JWTManager

#Importamos las rutas de los blueprint
from routes.ejercicios import ejercicios_bp
from routes.usuarios import usuarios_bp
from routes.rutinas import rutinas_bp
from routes.pesos import pesos_bp

#Cargar las variables de entorno
load_dotenv()


def create_app():  #Funcion para crear la app

    #Instancia de la app
    app = Flask(__name__)

    #Configurar la base de datos
    init_db(app)

    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    jwt = JWTManager(app)

    #Registrar el blueprint
    app.register_blueprint(ejercicios_bp, url_prefix='/ejercicios')
    app.register_blueprint(usuarios_bp, url_prefix='/usuarios')
    app.register_blueprint(rutinas_bp, url_prefix='/rutinas')
    app.register_blueprint(pesos_bp, url_prefix='/pesos')

    return app


#Crear la app
app = create_app()

if __name__ == "__main__":

    #Obtenemos el puerto
    port = int(os.getenv("PORT",8080))

    #Corremos la app
    app.run(host="0.0.0.0", port=port, debug=True)