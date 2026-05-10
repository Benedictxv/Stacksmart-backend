from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db
from ..models import User

user_bp = Blueprint('user', __name__)


@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'phone': user.phone,
        'income_range': user.income_range,
        'spending_habit': user.spending_habit,
        'profile_photo': user.profile_photo,
        'created_at': user.created_at.isoformat()
    }), 200


@user_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()

    if data.get('name'):
        user.name = data['name']
    if data.get('income_range'):
        user.income_range = data['income_range']
    if data.get('spending_habit'):
        user.spending_habit = data['spending_habit']

    db.session.commit()

    return jsonify({'message': 'Profile updated successfully'}), 200


@user_bp.route('/profile/photo', methods=['POST'])
@jwt_required()
def upload_photo():
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data.get('photo'):
        return jsonify({'error': 'No photo provided'}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    user.profile_photo = data['photo']
    db.session.commit()

    return jsonify({'message': 'Photo updated successfully'}), 200