from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from config.db import get_db_connection

#Creamos el blueprint
pesos_bp = Blueprint('pesos', __name__)

#Crear endpoint que crea un ejercicio
@pesos_bp.route('/registrar', methods=['POST'])
@jwt_required()


#peso, unidad_medida, repeticiones, series, id_ejercicio
def registrar():
    # Obtener la identidad del dueño del token (id_usuario)
    current_user = get_jwt_identity()

    # Obtener los datos del body
    data = request.get_json()
    id_ejercicio = data.get('id_ejercicio')
    peso = data.get('peso')
    unidad_medida = data.get('unidad_medida')
    repeticiones = data.get('repeticiones')
    series = data.get('series')

    fecha = data.get('fecha')  # Fecha en formato 'YYYY-MM-DD'
    if not fecha:
        from datetime import datetime
        fecha = datetime.now().strftime('%Y-%m-%d')  # Fecha actual si no se proporciona

    if not id_ejercicio or not peso or not unidad_medida or not repeticiones or not series:
        return jsonify({"error":"Faltan datos"}),400
    if unidad_medida not in ['kg', 'lbs']:
        return jsonify({"error":"Unidad de medida no valida, solo se acepta 'kg' o 'lbs'"}),400
    
    # Obtenemos el cursor
    cursor = get_db_connection()

    try:
        # Insertar el registro en la base de datos
        cursor.execute('''INSERT INTO registro_ejercicio (id_usuario, id_ejercicio,peso,unidad_medida,repeticiones,series,fecha) values (%s,%s,%s,%s,%s,%s,%s)''',
                       (current_user, id_ejercicio,peso,unidad_medida,repeticiones,series,fecha))
        # Guardamos el nuevo registro
        cursor.connection.commit()

        return jsonify({"mensaje":"El ejercicio se registro correctamente"}), 201

    except Exception as e:
        return jsonify({"error":f"Error al registrar ejecicio: {str(e)}"}),500

    finally:
        cursor.close()

#Crear endpoint que obtiene los registros por ejercicio
@pesos_bp.route('/obtener/<int:id_ejercicio>', methods=['GET'])
@jwt_required()
def get(id_ejercicio):
    # Obtenemos la identidad del dueño del token
    current_user = get_jwt_identity()
    
    # Conectamos a la bd
    cursor = get_db_connection()

    # Ejecutar la consulta
    query = '''
                SELECT a.id_registro, a.id_usuario, a.id_ejercicio, a.peso, a.unidad_medida, a.repeticiones, a.series, a.fecha, b.nombre, b.email
                FROM registro_ejercicio as a
                INNER JOIN usuarios as b on a.id_usuario = b.id_usuario
                WHERE a.id_usuario = %s AND a.id_ejercicio = %s
            '''
    
    cursor.execute(query, (current_user,id_ejercicio))
    lista = cursor.fetchall()

    cursor.close()

    if not lista:
        return jsonify({"error":"El usuario no registros"}),404
    else:
        return jsonify({"lista":lista}),200


#Crear endpoint que elimina un registro
@pesos_bp.route('/eliminar/<int:id_registro>', methods=['DELETE'])
@jwt_required()
def eliminar(id_registro):
    # Obtener la identidad del dueño del token
    current_user = get_jwt_identity()

    # Obtenemos el cursor
    cursor = get_db_connection()

    # Verificamos que el registro exista y pertenezca al usuario
    cursor.execute("SELECT id_usuario FROM registro_ejercicio WHERE id_registro = %s", (id_registro,))
    registro = cursor.fetchone()

    if not registro:
        cursor.close()
        return jsonify({"error":"Este registro no existe"}), 404
    
    if not registro[0] == int(current_user):
        cursor.close()
        return jsonify({"error": "Credenciales Incorrectas"}), 401

    try:
        # Hacemos el delete
        cursor.execute("DELETE FROM registro_ejercicio WHERE id_registro = %s", (id_registro,))
        cursor.connection.commit()
        return jsonify({"mensaje":"Registro eliminado correctamente"}),200
    except Exception as e:
        return jsonify({"error":f"No se pudo eliminar el registro: {str(e)}"}),500
    finally:
        cursor.close()


#Crear endpoint que actualiza un registro
@pesos_bp.route('/actualizar/<int:id_registro>', methods=['PUT'])
@jwt_required()
def actualizar(id_registro):
    # Obtener la identidad del dueño del token
    current_user = get_jwt_identity()

    # Obtenemos los datos del body
    data = request.get_json()
    id_ejercicio = data.get('id_ejercicio')
    peso = data.get('peso')
    unidad_medida = data.get('unidad_medida')
    repeticiones = data.get('repeticiones')
    series = data.get('series')
    # fecha = data.get('fecha')  # Fecha en formato 'YYYY-MM-DD'

    if not id_ejercicio or not peso or not unidad_medida or not repeticiones or not series:
        return jsonify({"error":"Faltan datos"}),400
    if unidad_medida not in ['kg', 'lbs']:
        return jsonify({"error":"Unidad de medida no valida, solo se acepta 'kg' o 'lbs'"}),400
    
        
    
    
    # Obtenemos el cursor
    cursor = get_db_connection()

    # Verificamos que el registro exista y pertenezca al usuario
    cursor.execute("SELECT id_usuario FROM registro_ejercicio WHERE id_registro = %s", (id_registro,))
    registro = cursor.fetchone()

    if not registro:
        cursor.close()
        return jsonify({"error":"Esa registro no existe"}), 404
    
    if not registro[0] == int(current_user):
        cursor.close()
        return jsonify({"error": "Credenciales Incorrectas"}), 401

    try:
        # Hacemos el update
     
        cursor.execute("UPDATE registro_ejercicio SET peso = %s WHERE id_registro = %s", 
                        (peso, id_registro))
        cursor.execute("UPDATE registro_ejercicio SET unidad_medida = %s WHERE id_registro = %s",
                        (unidad_medida, id_registro))
        cursor.execute("UPDATE registro_ejercicio SET repeticiones = %s WHERE id_registro = %s",
                        (repeticiones, id_registro))
        cursor.execute("UPDATE registro_ejercicio SET series = %s WHERE id_registro = %s",
                        (series, id_registro))
        cursor.execute("UPDATE registro_ejercicio SET id_ejercicio = %s WHERE id_registro = %s",
                        (id_ejercicio, id_registro))
        
        cursor.connection.commit()
        return jsonify({"mensaje":"Registro actualizado correctamente"}),200
    except Exception as e:
        return jsonify({"error":f"No se pudo actualizar el registro: {str(e)}"}),500
    finally:
        cursor.close()

