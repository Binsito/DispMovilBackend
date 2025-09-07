from flask import Blueprint,request,jsonify
from config.db import get_db_connection


# crear el blueprint
tareas_bp = Blueprint('tareas', __name__)

#Crear un endpoint
@tareas_bp.route('/obtener', methods=['GET'])
def get():
    return jsonify({"mensaje": "esta es la ruta de tareas"})

#Crear otro endpoint con post recibiendo datos desde el body
@tareas_bp.route('/crear', methods=['POST'])
def post():
    #obtener datos del body
    data = request.get_json()

    descripcion = data.get('descripcion')
    if not descripcion:
        return jsonify({"error": "La descripción es requerida"}), 400

    #obtener cursor
    cursor = get_db_connection()

    #hacemos el insert
    try:
        cursor.execute("INSERT INTO tareas (descripcion) VALUES (%s)", (descripcion,))
        cursor.connection.commit() #commit para guardar los cambios
        return jsonify({"mensaje": "Tarea creada exitosamente"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        #cerrar el cursor
        cursor.close()


#Crear otro endpoint usando PUT y pasando datos el  body y por la URL
@tareas_bp.route('/modificar/<int:user_id>', methods=['PUT'])
def put(user_id):
    #Obtener datos del body
    data = request.get_json()
    nombre = data.get('nombre')
    apellido = data.get('apellido')
    mensaje = f"Usuario con id: {user_id} y nombre:  {nombre} {apellido}"
    return jsonify({"saludo": mensaje})

#Crear otro endpoint usando DELETE y pasando datos por la URL
