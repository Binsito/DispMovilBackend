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

    # Ejecutar la consulta, ahora incluyendo el nombre de la rutina
    query = '''
        SELECT 
            e.id_usuario,
            e.nombre AS nombre_ejercicio,
            e.descripcion,
            u.nombre AS nombre_usuario,
            u.email,
            e.id_ejercicio,
            e.id_rutina,
            r.nombre AS nombre_rutina
        FROM ejercicios AS e
        INNER JOIN usuarios AS u ON e.id_usuario = u.id_usuario
        LEFT JOIN rutinas AS r ON e.id_rutina = r.id_rutina
        WHERE e.id_usuario = %s
    '''
    
    cursor.execute(query, (current_user,))
    lista = cursor.fetchall()

    cursor.close()

    if not lista:
        return jsonify({"error":"El usuario no tiene ejercicios"}), 404
    else:
        return jsonify({"lista": lista}), 200


    

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
    nombre_rutina = data.get('nombre_rutina')

    if not nombre or not descripcion:
        return jsonify({"error": "Debes teclear una descripcion y un nombre"}), 400
    
    if not nombre_rutina:
        return jsonify({"error": "Debes teclear una rutina"}), 400

    cursor = get_db_connection()
    
    try:
        
            # Buscamos el id de la rutina por nombre y usuario
            cursor.execute('SELECT id_rutina FROM rutinas WHERE nombre=%s AND id_usuario=%s', 
                           (nombre_rutina, current_user))
            rutina = cursor.fetchone()
            
            if not rutina:
                return jsonify({"error": "La rutina no existe o no pertenece al usuario"}), 404
            
            id_rutina = rutina[0]

            # Insertamos el ejercicio
            cursor.execute(
                'INSERT INTO ejercicios (nombre, descripcion, id_usuario, id_rutina) VALUES (%s, %s, %s, %s)',
                (nombre, descripcion, current_user, id_rutina)
            )
            cursor.connection.commit()

            return jsonify({"message": "Ejercicio creado!"}), 201

    except Exception as e:
        return jsonify({"error": f"No se pudo crear el ejercicio: {str(e)}"}), 500

    finally:
        cursor.close()



# Crear endpoint usando PUT y pasando datos por el body y el url
@ejercicios_bp.route('/modificar/<int:id_ejercicio>', methods=['PUT'])
@jwt_required()
def modificar(id_ejercicio):

    # Obtener la identidad del dueño del token
    current_user = get_jwt_identity()

    # Obtenemos los datos del body
    data = request.get_json()
    nombre = data.get('nombre')
    descripcion = data.get('descripcion')
    nombre_rutina = data.get('nombre_rutina')
    

    cursor = get_db_connection()

    # Verificamos que el ejercicio exista
    query = "SELECT * FROM ejercicios WHERE id_ejercicio = %s"
    cursor.execute(query, (id_ejercicio,))
    ejercicio = cursor.fetchone()
    
    if not ejercicio:
        cursor.close()
        return jsonify({"error":"Ese ejercicio no existe"}), 404
    
    # Verificamos que el ejercicio pertenezca al usuario
    if ejercicio[3] != int(current_user):
        cursor.close()
        return jsonify({"error": "Credenciales Incorrectas"}), 401

    # Obtenemos el id_rutina a partir del nombre_rutina
    cursor.execute("SELECT id_rutina FROM rutinas WHERE nombre = %s AND id_usuario = %s", 
                   (nombre_rutina, current_user))
    rutina = cursor.fetchone()

    if not rutina:
        cursor.close()
        return jsonify({"error": "La rutina indicada no existe"}), 404

    id_rutina = rutina[0]

    # Actualizamos el ejercicio
    try:
        cursor.execute("""
            UPDATE ejercicios 
            SET nombre = %s, descripcion = %s, id_rutina = %s
            WHERE id_ejercicio = %s
        """, (nombre, descripcion, id_rutina, id_ejercicio))
        
        cursor.connection.commit()
        return jsonify({"mensaje":"Datos actualizados correctamente"}), 200
    except Exception as e:
        return jsonify({"error": f"Error al actualizar los datos: {str(e)}"}), 500
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

