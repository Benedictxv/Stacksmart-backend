from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from ..extensions import db
from ..models import SavingsGoal, VirtualAccount
from ..services.squad import create_virtual_account

goals_bp = Blueprint('goals', __name__)


@goals_bp.route('/', methods=['GET'])
@jwt_required()
def get_goals():
    user_id = get_jwt_identity()
    goals = SavingsGoal.query.filter_by(user_id=user_id).all()

    return jsonify([{
        'id': g.id,
        'name': g.name,
        'target_amount': g.target_amount,
        'current_amount': g.current_amount,
        'deadline': g.deadline.isoformat() if g.deadline else None,
        'status': g.status,
        'progress': round((g.current_amount / g.target_amount) * 100, 1) if g.target_amount > 0 else 0,
        'virtual_account': {
            'account_number': g.virtual_account.account_number,
            'bank_name': g.virtual_account.bank_name
        } if g.virtual_account else None
    } for g in goals]), 200


@goals_bp.route('/', methods=['POST'])
@jwt_required()
def create_goal():
    user_id = get_jwt_identity()
    data = request.get_json()

    required = ['name', 'target_amount']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400

    goal = SavingsGoal(
        user_id=user_id,
        name=data['name'],
        target_amount=data['target_amount'],
        deadline=datetime.strptime(data['deadline'], '%Y-%m-%d').date() if data.get('deadline') else None
    )

    db.session.add(goal)
    db.session.flush()

    va_data = create_virtual_account(user_id=user_id, goal_id=goal.id, goal_name=data['name'])

    if va_data:
        virtual_account = VirtualAccount(
            goal_id=goal.id,
            squad_account_ref=va_data['squad_account_ref'],
            account_number=va_data['account_number'],
            bank_name=va_data['bank_name']
        )
        db.session.add(virtual_account)

    db.session.commit()

    return jsonify({
        'message': 'Goal created successfully',
        'goal': {
            'id': goal.id,
            'name': goal.name,
            'target_amount': goal.target_amount,
            'current_amount': goal.current_amount,
            'status': goal.status,
            'virtual_account': {
                'account_number': va_data['account_number'],
                'bank_name': va_data['bank_name']
            } if va_data else None
        }
    }), 201


@goals_bp.route('/<int:goal_id>', methods=['GET'])
@jwt_required()
def get_goal(goal_id):
    user_id = get_jwt_identity()
    goal = SavingsGoal.query.filter_by(id=goal_id, user_id=user_id).first()

    if not goal:
        return jsonify({'error': 'Goal not found'}), 404

    return jsonify({
        'id': goal.id,
        'name': goal.name,
        'target_amount': goal.target_amount,
        'current_amount': goal.current_amount,
        'deadline': goal.deadline.isoformat() if goal.deadline else None,
        'status': goal.status,
        'progress': round((goal.current_amount / goal.target_amount) * 100, 1) if goal.target_amount > 0 else 0,
        'virtual_account': {
            'account_number': goal.virtual_account.account_number,
            'bank_name': goal.virtual_account.bank_name
        } if goal.virtual_account else None
    }), 200


@goals_bp.route('/<int:goal_id>', methods=['DELETE'])
@jwt_required()
def delete_goal(goal_id):
    user_id = get_jwt_identity()
    goal = SavingsGoal.query.filter_by(id=goal_id, user_id=user_id).first()

    if not goal:
        return jsonify({'error': 'Goal not found'}), 404

    db.session.delete(goal)
    db.session.commit()

    return jsonify({'message': 'Goal deleted'}), 200
