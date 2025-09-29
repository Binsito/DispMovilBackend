from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from config.db import get_db_connection

#Creamos el blueprint
ejercicios_bp = Blueprint('ejercicios', __name__)

#Crear endpoint con GET
@ejercicios_bp.route('/obtener', methods=['GET'])
@jwt_required()
def get():

    # Obtenemos la identidad del dueño del token
    current_user = get_jwt_identity()
    
    # Conectamos a la bd
    cursor = get_db_connection()

    # Ejecutar la consulta
    query = '''
               SELECT a.id_usuario,a.nombre , a.descripcion, b.nombre, b.email, a.id_ejercicio, a.id_rutina
               FROM ejercicios as a 
               INNER JOIN usuarios as b on a.id_usuario = b.id_usuario
               WHERE a.id_usuario = %s
            '''
    
    cursor.execute(query, (current_user,))
    lista = cursor.fetchall()

    cursor.close()

    if not lista:
        return jsonify({"error":"El usuario no tiene ejercicios"}),404
    else:
        return jsonify({"lista":lista}),200

    

# Crear endpoint con post recibiendo datos desde el body
@ejercicios_bp.route('/crear', methods=['POST'])
@jwt_required()
def crear():

    # Obtener la identidad del dueño del token
    current_user = get_jwt_identity()

    # Obtener los datos del body
    data = request.get_json()
    nombre = data.get('nombre')
    descripcion = data.get('descripcion')
    id_rutina = data.get('id_rutina')

    if not descripcion or not nombre:
        return jsonify({"error":"Debes teclear una descripcion y un nombre"}),400
    
    if not id_rutina:
        return jsonify({"error":"Debes teclear una rutina"}),400
    
    # Obtenemos el cursor
    cursor = get_db_connection()

    # Hacemos el insert
    try:
        cursor.execute('INSERT INTO ejercicios (nombre, descripcion, id_usuario, id_rutina) values (%s,%s,%s,%s)', 
                       (nombre,descripcion,current_user,id_rutina))
        cursor.connection.commit()
        return jsonify({"message":"ejercicio creado!"}),201
    except Exception as e:
        return jsonify({"Error":f"No se pudo crear la ejercicio: {str(e)}"})
    finally:
        # Cierro el cursor y la conexion
        cursor.close()


# Crear endpoint usando PUT y pasando datos por el body y el url
@ejercicios_bp.route('/modificar/<int:id_ejercicio>', methods=['PUT'])
@jwt_required()
def modificar(id_ejercicio):

    #Obtener la identidad del dueño del token
    current_user = get_jwt_identity()

    # Obtenemos los datos del body
    data = request.get_json()

    nombre = data.get('nombre')
    descripcion = data.get('descripcion')
    id_rutina = data.get('id_rutina')

    cursor = get_db_connection()

    # Verificamos que la ejercicio exista
    query = "SELECT * FROM ejercicios WHERE id_ejercicio = %s"
    cursor.execute(query, (id_ejercicio,))
    ejercicio = cursor.fetchone()
    
    # 
    if not ejercicio:
        cursor.close()
        return jsonify({"error":"Esa ejercicio no existe"}), 404
    
    
    # Verificamos que la ejercicio pertenezca al usuario
    if not ejercicio[3] == int(current_user):
        cursor.close()
        return jsonify({"error": "Credenciales Incorrectas"}), 401
    
    # Actualizamos la ejercicio
    try:
        cursor.execute("UPDATE ejercicios SET descripcion = %s WHERE id_ejercicio = %s", 
                       (descripcion, id_ejercicio))
        cursor.execute("UPDATE ejercicios SET nombre = %s WHERE id_ejercicio = %s", 
                       (nombre, id_ejercicio))
        cursor.execute("UPDATE ejercicios SET id_rutina = %s WHERE id_ejercicio = %s", 
                       (id_rutina, id_ejercicio))
        
        cursor.connection.commit()
        return jsonify({"mensaje":"Datos actualizados correctamente"}),200
    except Exception as e:
        return jsonify({"error":f"Error al actualizar los datos: {str(e)}"})
    finally:
        cursor.close()

# Crear endpoint usando DELETE y pasando datos por el URL
@ejercicios_bp.route('/eliminar/<int:id_ejercicio>', methods=['DELETE'])
@jwt_required()
def eliminar(id_ejercicio):
    #Obtener la identidad del dueño del token
    current_user = get_jwt_identity()

    cursor = get_db_connection()

    # Verificamos que la ejercicio exista
    query = "SELECT * FROM ejercicios WHERE id_ejercicio = %s"
    cursor.execute(query, (id_ejercicio,))
    ejercicio = cursor.fetchone()

    if not ejercicio:
        cursor.close()
        return jsonify({"error":"Esa ejercicio no existe"}), 404

    # Verificamos que la ejercicio pertenezca al usuario
    if not ejercicio[3] == int(current_user):
        cursor.close()
        return jsonify({"error": "Credenciales Incorrectas"}), 401

    # Eliminamos la ejercicio
    try:
        cursor.execute("DELETE FROM ejercicios WHERE id_ejercicio = %s", (id_ejercicio,))
        cursor.connection.commit()
        return jsonify({"mensaje":"Ejercicio eliminado correctamente"}),200
    except Exception as e:
        return jsonify({"error":f"Error al eliminar la ejercicio: {str(e)}"}),500
    finally:
        cursor.close()

