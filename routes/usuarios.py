from flask import Blueprint, request, jsonify,send_file,make_response
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt, get_jwt_identity
from flask_bcrypt import Bcrypt
import datetime
from werkzeug.utils import secure_filename

import io

from config.db import get_db_connection

import os
from dotenv import load_dotenv

#Cargamos las variables de entorno
load_dotenv()

#Creamos el blueprint
usuarios_bp = Blueprint('usuarios', __name__)

# Inicializamos a Bcrypt
bcrypt = Bcrypt()

@usuarios_bp.route('/registrar', methods=['POST'])
def registrar():

    # Obtener del body los datos
    data = request.get_json()

    nombre = data.get('nombre')
    email = data.get('email')
    password = data.get('password')

    # Validacion
    if not nombre or not email or not password:
        return jsonify({"error":"Faltan datos"}), 400
    
    # Obtener el cursor de la bd
    cursor = get_db_connection()

    try:
        # Verificamos que el usuario no exista
        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            return jsonify({"error":"Ese usuario ya existe"}),400
        
        # Hacemos hash al password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Insertar el registro del nuevo usuario en la base de datos
        cursor.execute('''INSERT INTO usuarios (nombre, email, password) values (%s,%s,%s)''',
                       (nombre, email, hashed_password))
        
        # Guardamos el nuevo registro
        cursor.connection.commit()

        return jsonify({"mensaje":"El usuario se creo correctamente"}), 201

    except Exception as e:
        return jsonify({"error":f"Error al registrar al usuario: {str(e)}"}),500

    finally:
        # Nos aseguramos de cerrar el cursor
        cursor.close()

@usuarios_bp.route('/login', methods=['POST'])
def login():

    data = request.get_json()

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error":"Faltan datos"}), 400
    
    cursor = get_db_connection()

    query = "SELECT password, id_usuario FROM usuarios WHERE email = %s"
    cursor.execute(query, (email,))

    usuario = cursor.fetchone()

    if usuario and bcrypt.check_password_hash(usuario[0], password):
        #Generamos el JWT
        expires = datetime.timedelta(minutes=60)

        acces_token = create_access_token(
            identity=str(usuario[1]),
            expires_delta=expires
        )
        cursor.close()
        return jsonify({"access_token": acces_token}),200
    else:
        return jsonify({"error":"Credenciales Incorrectas"}),401


@usuarios_bp.route('/datos', methods=['GET'])
@jwt_required()
def datos():

    current_user = get_jwt_identity()

    cursor = get_db_connection()

    query = "SELECT id_usuario, nombre, email FROM usuarios where id_usuario = %s"
    cursor.execute(query, (current_user,))
    usuario = cursor.fetchone()

    cursor.close()

    if usuario:
        user_info = {
            "id_usuario":usuario[0],
            "nombre":usuario[1],
            "email":usuario[2],
        }
        return jsonify({"datos":user_info}), 200
    else:
        return jsonify({"error":"Usuario no encontrado"}),404


@usuarios_bp.route('/actualizar', methods=['POST'])
@jwt_required()
def perfil():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({"error":"Usuario no autenticado"}),401

    nombre = request.form.get('nombre')
    foto_perfil = request.files.get('foto_perfil')
    print(foto_perfil)
    print(nombre)

    
    
    if not foto_perfil or not nombre:
        return jsonify({"error":"Faltan datos"}),400
    
    
    file_bytes = foto_perfil.read()
    cursor = get_db_connection()
    try:
        query = "UPDATE usuarios SET foto_perfil = %s, nombre = %s WHERE id_usuario = %s"
        cursor.execute(query, (file_bytes, nombre, current_user))
        cursor.connection.commit()
        return jsonify({"mensaje":"Perfil actualizado correctamente"}),200
    except Exception as e:
        return jsonify({"error":f"Error al actualizar el perfil: {str(e)}"}),500
    finally:
        cursor.close()


@usuarios_bp.route('/foto/<int:id_usuario>', methods=['GET'])
@jwt_required()
def get_foto(id_usuario):
    current_user = get_jwt_identity()
    if not current_user or int(current_user) != id_usuario:
        return jsonify({"error":"Credenciales Incorrectas"}),401
    
    cursor = get_db_connection()
    cursor.execute("SELECT foto_perfil FROM usuarios WHERE id_usuario = %s", (id_usuario,))
    row = cursor.fetchone()
    cursor.close()

    if not row or not row[0]:
        return "No hay foto", 404

    image_bytes = row[0]  # el BLOB
    return send_file(io.BytesIO(image_bytes), mimetype='image/jpeg')