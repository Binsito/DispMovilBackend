from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from config.db import get_db_connection

#Creamos el blueprint
rutinas_bp = Blueprint('rutinas', __name__)

#Crear endpoint que crea una rutina
@rutinas_bp.route('/crear', methods=['POST'])
@jwt_required()
def crear():
    # Obtener la identidad del dueño del token
    current_user = get_jwt_identity()

    # Obtener los datos del body
    data = request.get_json()
    nombre = data.get('nombre')

    if not nombre:
        return jsonify({"error":"Debes teclear un nombre"}), 400

    # Obtenemos el cursor
    cursor = get_db_connection()

    try:
        # Verificar si ya existe una rutina con ese nombre para este usuario
        cursor.execute(
            "SELECT id_rutina FROM rutinas WHERE id_usuario = %s AND nombre = %s",
            (current_user, nombre)
        )
        existente = cursor.fetchone()
        if existente:
            return jsonify({"error": "Ya tienes una rutina con ese nombre"}), 400

        # Insertar el registro de la nueva rutina en la base de datos
        cursor.execute(
            "INSERT INTO rutinas (id_usuario, nombre) VALUES (%s, %s)",
            (current_user, nombre)
        )

        # Guardamos el nuevo registro
        cursor.connection.commit()

        return jsonify({"mensaje": "La rutina se creó correctamente"}), 201

    except Exception as e:
        return jsonify({"error": f"Error al crear la rutina: {str(e)}"}), 500

    finally:
        cursor.close()


#Crear endpoint que obtiene las rutinas del usuario
@rutinas_bp.route('/obtener', methods=['GET'])
@jwt_required()
def get():
    # Obtenemos la identidad del dueño del token
    current_user = get_jwt_identity()
    
    # Conectamos a la bd
    cursor = get_db_connection()

    # Ejecutar la consulta
    query = '''
               SELECT a.id_usuario, a.nombre, b.nombre, b.email, a.id_rutina
               FROM rutinas as a 
               INNER JOIN usuarios as b on a.id_usuario = b.id_usuario
               WHERE a.id_usuario = %s
            '''
    
    cursor.execute(query, (current_user,))
    lista = cursor.fetchall()

    cursor.close()

    if not lista:
        return jsonify({"error":"El usuario no tiene rutinas"}),404
    else:
        return jsonify({"lista":lista}),200
    


#Crear endpoint que elimina una rutina
@rutinas_bp.route('/eliminar/<int:id_rutina>', methods=['DELETE'])
@jwt_required()
def eliminar(id_rutina):
    # Obtener la identidad del dueño del token
    current_user = get_jwt_identity()

    # Obtenemos el cursor
    cursor = get_db_connection()

    # Verificamos que la rutina exista y pertenezca al usuario
    cursor.execute("SELECT id_usuario FROM rutinas WHERE id_rutina = %s", (id_rutina,))
    rutina = cursor.fetchone()

    if not rutina:
        cursor.close()
        return jsonify({"error":"Esa rutina no existe"}), 404
    
    if not rutina[0] == int(current_user):
        cursor.close()
        return jsonify({"error": "Credenciales Incorrectas"}), 401

    try:
        # Hacemos el delete
        cursor.execute("DELETE FROM rutinas WHERE id_rutina = %s", (id_rutina,))
        cursor.connection.commit()
        return jsonify({"mensaje":"Rutina eliminada correctamente"}),200
    except Exception as e:
        return jsonify({"error":f"No se pudo eliminar la rutina: {str(e)}"}),500
    finally:
        cursor.close()


#Crear endpoint que actualiza una rutina
@rutinas_bp.route('/actualizar/<int:id_rutina>', methods=['PUT'])
@jwt_required()
def actualizar(id_rutina):
    # Obtener la identidad del dueño del token
    current_user = get_jwt_identity()

    # Obtener los datos del body
    data = request.get_json()
    nombre = data.get('nombre')

    if not nombre:
        return jsonify({"error": "Debes teclear un nombre"}), 400
    
    # Obtener el cursor
    cursor = get_db_connection()

    # Verificar que la rutina exista y pertenezca al usuario
    cursor.execute("SELECT id_usuario FROM rutinas WHERE id_rutina = %s", (id_rutina,))
    rutina = cursor.fetchone()

    if not rutina:
        cursor.close()
        return jsonify({"error": "Esa rutina no existe"}), 404
    
    if rutina[0] != int(current_user):
        cursor.close()
        return jsonify({"error": "Credenciales Incorrectas"}), 401

    try:
        # Verificar si el nuevo nombre ya existe para este usuario en otra rutina
        cursor.execute(
            "SELECT id_rutina FROM rutinas WHERE id_usuario = %s AND nombre = %s AND id_rutina != %s",
            (current_user, nombre, id_rutina)
        )
        duplicado = cursor.fetchone()
        if duplicado:
            return jsonify({"error": "Ya tienes otra rutina con ese nombre"}), 400

        # Hacer el update
        cursor.execute(
            "UPDATE rutinas SET nombre = %s WHERE id_rutina = %s",
            (nombre, id_rutina)
        )
        cursor.connection.commit()
        return jsonify({"mensaje": "Rutina actualizada correctamente"}), 200

    except Exception as e:
        return jsonify({"error": f"No se pudo actualizar la rutina: {str(e)}"}), 500
    finally:
        cursor.close()



#Crear endpoint que obtiene los ejercicios de las rutinas del usuario
@rutinas_bp.route('/obtenerrutina/<int:id_rutina>', methods=['GET'])
@jwt_required()
def get_ejercicios_rutina(id_rutina):
    # Obtenemos la identidad del dueño del token
    current_user = get_jwt_identity()
    
    # Conectamos a la bd
    cursor = get_db_connection()

    # Ejecutar la consulta
    query = '''
               SELECT a.id_usuario, a.nombre, b.nombre, b.email, c.nombre, c.descripcion, c.id_ejercicio
               FROM rutinas as a 
               INNER JOIN usuarios as b on a.id_usuario = b.id_usuario
               INNER JOIN ejercicios as c on a.id_rutina = c.id_rutina
               WHERE a.id_usuario = %s AND a.id_rutina = %s
            '''
    
    cursor.execute(query, (current_user, id_rutina))
    lista = cursor.fetchall()

    cursor.close()

    if not lista:
        return jsonify({"error":"El usuario no tiene ejercicios en esa rutina"}),404
    else:
        return jsonify({"lista":lista}),200
    