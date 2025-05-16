"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from utils import APIException, generate_sitemap
from datastructures import FamilyStructure
# from models import Person


app = Flask(__name__)
app.url_map.strict_slashes = False
CORS(app)

# Create the jackson family object
jackson_family = FamilyStructure("Jackson")


# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code


# Generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)


@app.route('/members', methods=['GET'])
def handle_hello():
    # This is how you can use the Family datastructure by calling its methods
    members = jackson_family.get_all_members()
    response_body = {"family members": members}
    return jsonify(response_body), 200


@app.route('/members', methods=['POST'])
def add_member_api():
    try:
        member = request.get_json()

        # Validación general: petición vacía o faltan campos obligatorios
        required_fields = ["first_name", "age", "lucky_numbers"]
        if not member or not all(field in member for field in required_fields):
            return jsonify({
                "error": "Solicitud inválida. Debes incluir los campos: first_name, age, lucky_numbers."
            }), 400

        jackson_family.add_member(member)
        return jsonify({"msg": "Miembro añadido"}), 200

    except Exception as e:
        return jsonify({
            "error": "Error interno del servidor",
            "detalle": str(e)
        }), 500


@app.route('/members/<int:member_id>', methods=['GET'])
def get_member_api(member_id: int):
    member = jackson_family.get_member(member_id)
    if member is None:
        return jsonify({"error": "El miembro insertado no existe"}), 400

    response_body = {
        "id": member["id"],
        "first_name": member["first_name"],
        "age": member["age"],
        "lucky_numbers": member["lucky_numbers"]
    }
    return jsonify(response_body), 200

    

@app.route('/members/<int:member_id>', methods=['DELETE'])
def delete_member_api(member_id):
    result = jackson_family.delete_member(member_id)

    if result is None:
        return jsonify({"error": "Miembro no encontrado"}), 404

    return jsonify({
        "msg": f"Miembro con id {member_id} eliminado correctamente",
        "family": result
    }), 200



# This only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=True)
