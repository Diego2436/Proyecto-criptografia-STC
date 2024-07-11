from flask import Flask, jsonify, request
from Functions.Functions import *

app = Flask(__name__)

# Datos ficticios de ejemplo
items = [
    {"id": 1, "name": "Item 1"},
    {"id": 2, "name": "Item 2"},
    {"id": 3, "name": "Item 3"}
]
next_id = 4

# Ruta para obtener todos los elementos
@app.route('/items', methods=['GET'])
def get_items():
    return jsonify(items)

# Ruta para obtener un elemento por su ID
@app.route('/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    item = next((item for item in items if item['id'] == item_id), None)
    if item:
        return jsonify(item)
    else:
        return jsonify({'error': 'Item not found'}), 404

# Ruta para crear un nuevo elemento
@app.route('/items', methods=['POST'])
def create_item():
    global next_id
    data = request.json
    if 'name' in data:
        new_item = {'id': next_id, 'name': data['name']}
        items.append(new_item)
        next_id += 1
        return jsonify(new_item), 201
    else:
        return jsonify({'error': 'Name is required'}), 400

# Ruta para actualizar un elemento por su ID
@app.route('/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    data = request.json
    item = next((item for item in items if item['id'] == item_id), None)
    if item and 'name' in data:
        item['name'] = data['name']
        return jsonify(item)
    elif not item:
        return jsonify({'error': 'Item not found'}), 404
    else:
        return jsonify({'error': 'Name is required'}), 400

# Ruta para eliminar un elemento por su ID
@app.route('/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    global items
    items = [item for item in items if item['id'] != item_id]
    return 'Objeto eliminado', 204

if __name__ == '__main__':
    app.run(debug=True)
