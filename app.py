from flask import Flask
import os
from dotenv import load_dotenv
from config.db import init_db,mysql

#importamos los blueprints
from routes.tareas import tareas_bp
from routes.usuarios import usuarios_bp

#Cargar variables de entorno desde el archivo .env
load_dotenv()

def create_app():
    app = Flask(__name__)

    #configurar la base de datos
    init_db(app)

    #Registrar blueprints
    app.register_blueprint(tareas_bp, url_prefix='/tareas')
    app.register_blueprint(usuarios_bp, url_prefix='/usuarios')

    return app
   
#Crear la aplicación Flask
app=create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))  # Obtener el puerto desde la variable de entorno o usar 5000 por defecto
    
    
    #Correr la aplicación en el puerto especificado
    app.run(host='0.0.0.0', port=port, debug=True)