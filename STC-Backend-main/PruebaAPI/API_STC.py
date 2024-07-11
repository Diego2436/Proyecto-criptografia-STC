# Importación de librerías
from flask import Flask, jsonify, request, after_this_request, make_response
from flask_cors import CORS, cross_origin
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from Functions.Functions import *
from Config.Config import *

# Inicialización del servidor
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config.from_object(Config)

# Conexión con la base de datos
client = MongoClient(app.config['MONGO_URI'], server_api=ServerApi('1'))
try:
    client.admin.command('ping')
    db = client.get_database(app.config['MONGO_DB'])
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# Obtenemos todas las colecciones de la base
collection_usuarios = db.Usuarios    # Usuarios
collection_equipos = db.Equipos      # Equipos

def _build_cors_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")
    return response

# Función para revisar el Token (sesión iniciada)
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'No se ha iniciado sesión'}), 403

        try:
            token = token.split(" ")[1]  # Bearer <token>
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = collection_usuarios.find_one({'username': data['username']})
            if not current_user:
                return jsonify({'error': 'Sesión inválida'}), 403
        except Exception as e:
            return jsonify({'error': 'Sesión inválida', 'message': str(e)}), 403

        return f(current_user, *args, **kwargs)

    return decorated

# Endpoint para visualizar a los usuarios
@app.route('/usuarios/ver', methods=['GET'])
def ver_usuarios():
    users = collection_usuarios.find()
    result = []
    for user in users:
        user['_id'] = str(user['_id'])  # Convertir ObjectId a string
        result.append({
            'username': user['username'],
            'email': user['email'],
            'password': user['password']
        })
    return jsonify(result)

# Endpoint para el registro de los usuarios
@app.route('/usuarios/registrar', methods=['POST'])
def registrar_usuarios():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not password or not email:
        return jsonify({'error': 'Hay campos vacíos'}), 400

    if collection_usuarios.find_one({'email': email}):
        return jsonify({'error': 'Este email ya está registrado'}), 400
    if collection_usuarios.find_one({'username': username}):
        return jsonify({'error': 'Este nombre de usuario ya está en uso'}), 400

    hashed_password = hash_password(password)
    collection_usuarios.insert_one({
        'username': username,
        'email': email,
        'password': hashed_password
    })
    return jsonify({'message': 'Usuario registrado exitosamente'}), 201

# Endpoint para el inicio de sesión
@app.route('/usuarios/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Hay campos vacíos'}), 400

    user = collection_usuarios.find_one({'username': username})
    if not user or not check_password(user['password'], password):
        return jsonify({'error': 'Usuario o contraseña inválidos'}), 401

    token = jwt.encode({'username': username}, app.config['SECRET_KEY'], algorithm="HS256")
    return jsonify({'token': token}), 200

# Endpoint para crear un equipo de trabajo
@app.route('/equipos/crear', methods=['POST'])
@token_required
def crear_equipo(current_user):
    data = request.get_json()
    team_name = data.get('team_name')
    team_desc = data.get('team_desc')
    team_pw = data.get('team_pw')
    members = data.get('members', [])
    has_key = data.get('has_key', [])

    if not team_name or not team_desc or not team_pw:
        return jsonify({'error': 'Hay campos vacíos'}), 400

    # Agregar al usuario actual como el primer miembro del equipo
    members.insert(0, current_user['username'])

    if collection_equipos.find_one({'team_name': team_name}):
        return jsonify({'error': 'Este nombre de equipo ya está en uso'}), 400
    
    hashed_password = hash_password(team_pw)
    collection_equipos.insert_one({
        'team_name': team_name,
        'team_desc': team_desc,
        'team_pw': hashed_password,
        'members': members,
        'has_key': has_key
    })
    return jsonify({'message': 'Equipo creado exitosamente'}), 201

# Endpoint para agregar miembros al equipo
@app.route('/equipos/agregar', methods=['POST'])
@token_required
def agregar_miembro(current_user):
    data = request.get_json()
    team_name = data.get('team_name')
    username = data.get('username')

    if not team_name or not username:
        return jsonify({'error': 'Hay campos vacíos'}), 400
    
    # Buscamos al equipo
    team = collection_equipos.find_one({'team_name': team_name})
    if not team:
        return jsonify({'error': 'No se encontró al equipo'}), 404
    # Buscamos al usuario a añadir
    user = collection_usuarios.find_one({'username': username})
    if not user:
        return jsonify({'error': 'No se encontró al usuario'}), 404

    # Verificamos si el usuario ya es miembro del equipo
    if username in team['members']:
        return jsonify({'error': 'El usuario ya es miembro del equipo'}), 400

    # Añadimos al usuario a la lista de miembros
    collection_equipos.update_one(
        {'team_name': team_name},
        {'$push': {'members': username}}
    )
    
    return jsonify({'message': 'Usuario añadido exitosamente'}), 201

# Endpoint para obtener la lista de equipos
@app.route('/equipos/listar', methods=['GET'])
@token_required
def obtener_equipos(current_user):
    equipos = collection_equipos.find({'members': current_user['username']})
    result = []
    for equipo in equipos:
        equipo['_id'] = str(equipo['_id'])
        result.append({
            'team_name': equipo['team_name'],
            'team_desc': equipo['team_desc'],
        })
    return jsonify(result), 200

# Endpoint para generar fragmentos de secreto y guardarlos en MongoDB
@app.route('/equipos/generar_fragmentos', methods=['POST'])
@token_required
def generar_fragmentos(current_user):
    # Obtener datos del formulario
    data = request.get_json()
    team_name = data.get('team_name')
    team_password = data.get('team_password')

    if not team_name or not team_password:
        return jsonify({'error': 'Hay campos vacíos'}), 400

    # Verificar si el equipo existe y la contraseña es correcta
    equipo = collection_equipos.find_one({'team_name': team_name})
    if equipo:
        check = check_password(equipo['team_pw'], team_password)
        if not check:
            return jsonify({'error': 'Contraseña incorrecta'}), 404
    if not equipo:
        return jsonify({'error': 'Equipo no encontrado'}), 404

    # Verificar si el usuario actual es miembro del equipo
    if current_user['username'] not in equipo['members']:
        return jsonify({'error': 'No tienes permiso para generar fragmentos para este equipo'}), 403

    # Generar el secreto y los fragmentos
    secret_key = SigningKey.generate(curve=BRAINPOOLP512t1)
    secret = secret_key.privkey.secret_multiplier
    fragments = generate_shares(len(equipo['members']), len(equipo['members']), secret)

    # Guardar los fragmentos en la base de datos dentro de la colección del equipo
    equipo_fragments = [{'username': member, 'fragment': base64.b64encode(str(fragments[i][1]).encode()).decode()} for i, member in enumerate(equipo['members'])]

    collection_equipos.update_one(
        {'team_name': team_name},
        {'$set': {'fragments': equipo_fragments, 'has_key': True}}
    )

    return jsonify({'message': f'Fragmentos generados y listos para su descarga'}), 201

# Endpoint para descargar tu clave
@app.route('/equipos/descargar_fragmentos/<team_name>', methods=['GET'])
@token_required
def descargar_fragmento(current_user, team_name):
    # Verificar si el equipo existe
    equipo = collection_equipos.find_one({'team_name': team_name})
    if not equipo:
        return jsonify({'error': 'Equipo no encontrado'}), 404

    # Verificar si el usuario actual es miembro del equipo
    if current_user['username'] not in equipo['members']:
        return jsonify({'error': 'No tienes permiso para descargar fragmentos para este equipo'}), 403

    # Buscar el fragmento del usuario en la base de datos
    fragmento = next((f for f in equipo['fragments'] if f['username'] == current_user['username']), None)
    if not fragmento:
        return jsonify({'error': 'Fragmento no encontrado'}), 404

    # Decodificar el fragmento
    fragment_data = base64.b64decode(fragmento['fragment'].encode())

    @after_this_request
    def remove_fragment(response):
        # Eliminar el fragmento del usuario después de enviarlo
        collection_equipos.update_one(
            {'team_name': team_name},
            {'$pull': {'fragments': {'username': current_user['username']}}}
        )
        return response
    
    usernameEnd = current_user['username']
    response = make_response(fragment_data)
    response.headers['Content-Disposition'] = f'attachment; filename="{team_name}_{usernameEnd}_fragment.pem"'
    response.headers['Content-Type'] = 'application/x-pem-file'

    return response

@app.route('/equipos/subir_fragmentos/<team_name>', methods=['POST'])
@token_required
def subir_fragmento(current_user, team_name):
    _build_cors_preflight_response()
    # Verificar si el equipo existe
    equipo = collection_equipos.find_one({'team_name': team_name})
    if not equipo:
        return jsonify({'error': 'Equipo no encontrado'}), 404

    # Verificar si el usuario actual es miembro del equipo
    if current_user['username'] not in equipo['members']:
        return jsonify({'error': 'No tienes permiso para subir fragmentos para este equipo'}), 403

    # Verificar si se ha enviado el contenido del archivo
    if 'content' not in request.json:
        return jsonify({'error': 'No se ha enviado contenido de archivo'}), 400

    file_content = request.json['content']
    
    # Codificar el contenido en base64
    fragment_base64 = base64.b64encode(file_content.encode()).decode()

    # Verificar si el fragmento del usuario ya existe en la base de datos
    existing_fragment = collection_equipos.find_one(
        {'team_name': team_name, 'fragments.username': current_user['username']}
    )

    if existing_fragment:
        return jsonify({'error': 'Ya has subido tu fragmento'}), 400

    # Almacenar el fragmento en la base de datos
    collection_equipos.update_one(
        {'team_name': team_name},
        {'$push': {'fragments': {'username': current_user['username'], 'fragment': fragment_base64}}}
    )

    return jsonify({'message': 'Fragmento subido exitosamente'}), 201

# Endpoint para obtener la lista de miembros de un equipo y quien ha subido fragmentos
@app.route('/equipos/miembros/<team_name>', methods=['GET'])
@token_required
def obtener_miembros(current_user, team_name):
    # Verificar si el equipo existe
    equipo = collection_equipos.find_one({'team_name': team_name})
    if not equipo:
        return jsonify({'error': 'Equipo no encontrado'}), 404

    # Verificar si el usuario actual es miembro del equipo
    if current_user['username'] not in equipo['members']:
        return jsonify({'error': 'No tienes permiso para ver los miembros de este equipo'}), 403

    # Obtener la lista de miembros del equipo
    members = equipo['members']
    fragments = equipo['fragments']

    return jsonify({'members': members, 'fragments': fragments}), 200


# Endpoint para cifrar un documento
@app.route('/equipos/cifrar_documento/<team_name>', methods=['POST'])
@token_required
def cifrar_documento(current_user, team_name):
    _build_cors_preflight_response()
    
    # Verificar si el equipo existe
    equipo = collection_equipos.find_one({'team_name': team_name})
    if not equipo:
        return jsonify({'error': 'Equipo no encontrado'}), 404

    # Verificar si el usuario actual es miembro del equipo
    if current_user['username'] not in equipo['members']:
        return jsonify({'error': 'No tienes permiso para cifrar documentos para este equipo'}), 403

    # Verificar si se ha enviado un archivo
    if 'file' not in request.files:
        return jsonify({'error': 'No se ha enviado ningún archivo'}), 400
    
    file = request.files['file']
    filename = file.filename

    # Leer el contenido del archivo
    file_data = file.read()

    # Obtener todos los fragmentos del equipo y ordenarlos alfabéticamente según los usuarios a quienes les pertenecen
    equipo = collection_equipos.find_one({'team_name': team_name})
    if not equipo or 'fragments' not in equipo:
        return jsonify({'error': 'No se encontraron fragmentos para este equipo'}), 404

    fragments = sorted(equipo['fragments'], key=lambda x: x['username'])

    # Verificar que la cantidad de fragmentos sea igual o mayor que la cantidad de usuarios en el equipo
    if len(fragments) < len(equipo['members']):
        return jsonify({'error': 'La cantidad de fragmentos disponibles es menor que la cantidad de miembros del equipo'}), 400

    # Decodificar y convertir los fragmentos a enteros
    fragment_integers = []
    for fragment in fragments:
        fragment_data = int(base64.b64decode(fragment['fragment'].encode()))
        fragment_integers.append(fragment_data)

    # Generamos los fragmentos compartidos
    shares = []
    for i, fragment in enumerate(fragment_integers):
        shares.append((i + 1, fragment))

    # Reconstruimos el secreto a partir de las claves
    reconstructed_secret = reconstruct_secret(random.sample(shares, len(equipo['members'])))
    # Generación de claves AES
    inicial = str(reconstructed_secret)
    mitad = len(inicial) // 2
    proto_AES_key = int(inicial[:mitad])
    proto_AES_IV = int(inicial[mitad:])
    print(proto_AES_key)
    print(proto_AES_IV)

    # Generar clave AES y IV aplicando SHA-256
    aes_key = hashlib.sha256(proto_AES_key.to_bytes((proto_AES_key.bit_length() + 7) // 8, 'big')).digest()
    iv_full = hashlib.sha256(proto_AES_IV.to_bytes((proto_AES_IV.bit_length() + 7) // 8, 'big')).digest()
    aes_iv = iv_full[:16]

    # Ciframos el archivo enviado
    cipher = AES.new(aes_key, AES.MODE_CBC, aes_iv)
    cipher_data = cipher.encrypt(pad(file_data, AES.block_size))

    # Convertir los datos cifrados a base64 para almacenarlos en la base de datos
    cipher_base64 = base64.b64encode(cipher_data).decode()

    # Intentar actualizar el archivo cifrado existente
    result = collection_equipos.update_one(
        {'team_name': team_name, 'encrypted_files.filename': filename},
        {'$set': {'encrypted_files.$.data': cipher_base64}}
    )

    # Si no se actualizó ningún documento, agregar un nuevo archivo cifrado
    if result.matched_count == 0:
        collection_equipos.update_one(
            {'team_name': team_name},
            {'$push': {'encrypted_files': {'filename': filename, 'data': cipher_base64}}}
        )

    return jsonify({'message': 'Archivo cifrado y almacenado en la nube'}), 200

# Endpoint para descargar y descifrar un archivo
@app.route('/equipos/descargar_documento/<team_name>/<filename>', methods=['GET'])
@token_required
def descargar_documento(current_user, team_name, filename):
    # Verificar si el equipo existe
    equipo = collection_equipos.find_one({'team_name': team_name})
    if not equipo:
        return jsonify({'error': 'Equipo no encontrado'}), 404

    # Verificar si el usuario actual es miembro del equipo
    if current_user['username'] not in equipo['members']:
        return jsonify({'error': 'No tienes permiso para descargar documentos de este equipo'}), 403

    # Buscar el archivo cifrado en la base de datos
    encrypted_file = next((f for f in equipo.get('encrypted_files', []) if f['filename'] == filename), None)
    if not encrypted_file:
        return jsonify({'error': 'Archivo no encontrado'}), 404

    # Obtener todos los fragmentos del equipo y ordenarlos alfabéticamente según los usuarios a quienes les pertenecen
    fragments = sorted(equipo['fragments'], key=lambda x: x['username'])

    # Verificar que la cantidad de fragmentos sea igual o mayor que la cantidad de usuarios en el equipo
    if len(fragments) < len(equipo['members']):
        return jsonify({'error': 'La cantidad de fragmentos disponibles es menor que la cantidad de miembros del equipo'}), 400

    # Decodificar y convertir los fragmentos a enteros
    fragment_integers = []
    for fragment in fragments:
        fragment_data = int(base64.b64decode(fragment['fragment'].encode()))
        fragment_integers.append(fragment_data)

    # Generamos los fragmentos compartidos
    shares = []
    for i, fragment in enumerate(fragment_integers):
        shares.append((i + 1, fragment))

    # Reconstruimos el secreto a partir de las claves
    reconstructed_secret = reconstruct_secret(random.sample(shares, len(equipo['members'])))
    # Generación de claves AES
    inicial = str(reconstructed_secret)
    mitad = len(inicial) // 2
    proto_AES_key = int(inicial[:mitad])
    proto_AES_IV = int(inicial[mitad:])

    # Generar clave AES y IV aplicando SHA-256
    aes_key = hashlib.sha256(proto_AES_key.to_bytes((proto_AES_key.bit_length() + 7) // 8, 'big')).digest()
    iv_full = hashlib.sha256(proto_AES_IV.to_bytes((proto_AES_IV.bit_length() + 7) // 8, 'big')).digest()
    aes_iv = iv_full[:16]

    # Decodificar los datos cifrados
    cipher_data = base64.b64decode(encrypted_file['data'])
    
    # Descifrar el archivo
    cipher = AES.new(aes_key, AES.MODE_CBC, aes_iv)
    plaintext_data = unpad(cipher.decrypt(cipher_data), AES.block_size)

    # Crear una respuesta para descargar el archivo descifrado
    response = make_response(plaintext_data)
    response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
    response.headers['Content-Type'] = 'application/octet-stream'

    return response

# Endpoint para obtener el valor de has_key de un equipo
@app.route('/equipos/has_key/<team_name>', methods=['GET'])
@token_required
def obtener_has_key(current_user, team_name):
    # Verificar si el equipo existe
    equipo = collection_equipos.find_one({'team_name': team_name})
    if not equipo:
        return jsonify({'error': 'Equipo no encontrado'}), 404

    # Verificar si el usuario actual es miembro del equipo
    if current_user['username'] not in equipo['members']:
        return jsonify({'error': 'No tienes permiso para ver este equipo'}), 403

    # Obtener el valor de has_key
    has_key = equipo.get('has_key', False)

    return jsonify({'has_key': has_key}), 200

# Endpoint para obtener los nombres de archivo cifrados de un equipo
@app.route('/equipos/encrypted_files/nombres/<team_name>', methods=['GET'])
@token_required
def obtener_nombres_archivos_cifrados(current_user, team_name):
    # Verificar si el equipo existe
    equipo = collection_equipos.find_one({'team_name': team_name})
    if not equipo:
        return jsonify({'error': 'Equipo no encontrado'}), 404

    # Verificar si el usuario actual es miembro del equipo
    if current_user['username'] not in equipo['members']:
        return jsonify({'error': 'No tienes permiso para ver los archivos cifrados de este equipo'}), 403

    # Obtener los nombres de archivo cifrados del equipo
    encrypted_files = equipo.get('encrypted_files', [])
    filenames = [file['filename'] for file in encrypted_files]

    return jsonify({'filenames': filenames}), 200


# Iniciamos el server
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
