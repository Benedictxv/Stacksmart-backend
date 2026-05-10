from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db
from ..models import Transaction, VirtualAccount, SavingsGoal

payments_bp = Blueprint('payments', __name__)


@payments_bp.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()

    # Squad sends event type and transaction data
    if not data:
        return jsonify({'error': 'No data received'}), 400

    event = data.get('Event')
    transaction_data = data.get('Body', {})

    if event != 'charge.success':
        return jsonify({'message': 'Event ignored'}), 200

    squad_ref = transaction_data.get('transaction_ref')
    amount = transaction_data.get('amount', 0) / 100  # Squad sends in kobo
    virtual_account_number = transaction_data.get('virtual_account_number')

    if not squad_ref or not virtual_account_number:
        return jsonify({'error': 'Missing transaction data'}), 400

    # prevent double processing
    existing = Transaction.query.filter_by(squad_ref=squad_ref).first()
    if existing:
        return jsonify({'message': 'Transaction already processed'}), 200

    # find which goal this virtual account belongs to
    virtual_account = VirtualAccount.query.filter_by(
        account_number=virtual_account_number
    ).first()

    if not virtual_account:
        return jsonify({'error': 'Virtual account not found'}), 404

    goal = SavingsGoal.query.get(virtual_account.goal_id)

    if not goal:
        return jsonify({'error': 'Goal not found'}), 404

    # record the transaction
    transaction = Transaction(
        user_id=goal.user_id,
        goal_id=goal.id,
        amount=amount,
        squad_ref=squad_ref,
        status='confirmed'
    )

    # update goal balance
    goal.current_amount += amount

    # check if goal is completed
    if goal.current_amount >= goal.target_amount:
        goal.status = 'completed'

    db.session.add(transaction)
    db.session.commit()

    return jsonify({'message': 'Transaction recorded successfully'}), 200


@payments_bp.route('/transactions', methods=['GET'])
@jwt_required()
def get_transactions():
    user_id = get_jwt_identity()
    transactions = Transaction.query.filter_by(user_id=user_id).order_by(
        Transaction.paid_at.desc()
    ).all()

    return jsonify([{
        'id': t.id,
        'amount': t.amount,
        'goal_id': t.goal_id,
        'status': t.status,
        'squad_ref': t.squad_ref,
        'paid_at': t.paid_at.isoformat()
    } for t in transactions]), 200
@payments_bp.route('/withdraw', methods=['POST'])
@jwt_required()
def request_withdrawal():
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data.get('amount') or not data.get('goal_id'):
        return jsonify({'error': 'Amount and goal_id are required'}), 400

    goal = SavingsGoal.query.filter_by(id=data['goal_id'], user_id=user_id).first()

    if not goal:
        return jsonify({'error': 'Goal not found'}), 404

    if data['amount'] > goal.current_amount:
        return jsonify({'error': 'Insufficient balance'}), 400

    goal.current_amount -= data['amount']

    transaction = Transaction(
        user_id=user_id,
        goal_id=goal.id,
        amount=-data['amount'],
        squad_ref=f"WITHDRAW-{user_id}-{goal.id}-{int(__import__('time').time())}",
        status='confirmed'
    )

    db.session.add(transaction)
    db.session.commit()

    return jsonify({'message': 'Withdrawal request processed', 'new_balance': goal.current_amount}), 200