from flask import Blueprint,request,jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt
from flask_bcrypt import Bcrypt

#importamos la conexion a la base de datos
from config.db import get_db_connection

import os 
from dotenv import load_dotenv
load_dotenv()  # Cargar variables de entorno desde el archivo .env

# crear el blueprint
usuarios_bp = Blueprint('usuarios', __name__)

#inicializar Bcrypt
bcrypt = Bcrypt()

#Crear un endpoint para registrar usuarios
@usuarios_bp.route('/registrar', methods=['POST'])
def registrar():
    #obtener datos del body
    data = request.get_json()

    nombre = data.get('nombre')
    email = data.get('email')
    password = data.get('password')

    #validar que los campos no esten vacios
    if not nombre or not email or not password:
        return jsonify({"error": "Nombre, email y contraseña son requeridos"}), 400

    
    #obtener cursor
    cursor = get_db_connection()

    


    #hacemos el insert
    try:
        #verificar si el usuario ya existe\
        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        existing_user = cursor.fetchone()
        if existing_user:
            return jsonify({"error": "El usuario con este email ya existe"}), 400
        
        #hashear la contraseña
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        #insertar el nuevo usuario
        cursor.execute("INSERT INTO usuarios (nombre, email, password) VALUES (%s, %s, %s)", 
                       (nombre, email, hashed_password))
        cursor.connection.commit() #commit para guardar los cambios
        return jsonify({"mensaje": "Usuario registrado exitosamente"}), 201
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        #cerrar el cursor
        cursor.close()

#Crear un endpoint para login de usuarios
@usuarios_bp.route('/login', methods=['POST'])
def login():
    #obtener datos del body
    data = request.get_json()

    email = data.get('email')
    password = data.get('password')

    #validar que los campos no esten vacios
    if not email or not password:
        return jsonify({"error": "Email y contraseña son requeridos"}), 400

    #obtener cursor
    cursor = get_db_connection()
    
#==========================Aqui quedo pendiente=================================
    # try:
    #     #verificar si el usuario existe
    #     cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
    #     user = cursor.fetchone()
    #     if not user:
    #         return jsonify({"error": "Credenciales inválidas"}), 401
        
    #     #verificar la contraseña
    #     stored_password = user[3]  # Asumiendo que la contraseña está en la cuarta columna
    #     if not bcrypt.check_password_hash(stored_password, password):
    #         return jsonify({"error": "Credenciales inválidas"}), 401

    #     #crear el token JWT
    #     access_token = create_access_token(identity={"id": user[0], "nombre": user[1], "email": user[2]})
    #     return jsonify({"access_token": access_token}), 200

    # except Exception as e:
    #     return jsonify({"error": str(e)}), 500
    # finally:
    #     #cerrar el cursor
    #     cursor.close()