from flask_mysqldb import MySQL
import os
from dotenv import load_dotenv

load_dotenv()  # Cargar variables de entorno desde el archivo .env

#crear instance de MySQL
mysql = MySQL()

#funcion para obtener la conexion a la base de datos
def init_db(app):
    # Configurar la conexión a la base de datos MySQL
    app.config['MYSQL_HOST'] = os.getenv('DB_HOST')
    app.config['MYSQL_USER'] = os.getenv('DB_USER')
    app.config['MYSQL_PASSWORD'] = os.getenv('DB_PASSWORD')
    app.config['MYSQL_DB'] = os.getenv('DB_NAME')
    app.config['MYSQL_PORT'] = int(os.getenv('DB_PORT'))

    # Inicializar la extensión MySQL
    mysql.init_app(app)


def get_db_connection():
    #devvuelve un cursor para ejecutar consultas
    try:
        connection = mysql.connection
        return connection.cursor()
    except Exception as e:
        raise RuntimeError("Error al conectar a la base de datos: " + str(e))