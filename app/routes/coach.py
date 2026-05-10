from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db
from ..models import User, SavingsGoal, CoachMessage
from ..services.claude import get_coach_response

coach_bp = Blueprint('coach', __name__)


@coach_bp.route('/chat', methods=['POST'])
@jwt_required()
def chat():
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data.get('message'):
        return jsonify({'error': 'Message is required'}), 400

    user = User.query.get(user_id)
    goals = SavingsGoal.query.filter_by(user_id=user_id, status='active').all()
    chat_history = CoachMessage.query.filter_by(user_id=user_id).order_by(
        CoachMessage.created_at.asc()
    ).all()

    user_message = data['message']

    # save user message
    user_msg = CoachMessage(
        user_id=user_id,
        role='user',
        content=user_message
    )
    db.session.add(user_msg)

    # get AI response
    response_text = get_coach_response(
        user=user,
        goals=goals,
        chat_history=chat_history,
        user_message=user_message
    )

    # save assistant response
    assistant_msg = CoachMessage(
        user_id=user_id,
        role='assistant',
        content=response_text
    )
    db.session.add(assistant_msg)
    db.session.commit()

    return jsonify({
        'response': response_text
    }), 200


@coach_bp.route('/history', methods=['GET'])
@jwt_required()
def get_history():
    user_id = get_jwt_identity()
    messages = CoachMessage.query.filter_by(user_id=user_id).order_by(
        CoachMessage.created_at.asc()
    ).all()

    return jsonify([{
        'role': m.role,
        'content': m.content,
        'created_at': m.created_at.isoformat()
    } for m in messages]), 200