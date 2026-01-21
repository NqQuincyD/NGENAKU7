from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.extensions import db
from app.models.finance import Tithe, Offering
from app.models.core import Member
from datetime import datetime
from sqlalchemy import desc

bp = Blueprint('finance', __name__)

@bp.route('/')
@login_required
def index():
    tithes = Tithe.query.order_by(desc(Tithe.date)).limit(50).all()
    offerings = Offering.query.order_by(desc(Offering.date)).limit(50).all()
    return render_template('finance/index.html', tithes=tithes, offerings=offerings)

@bp.route('/tithe/add', methods=['GET', 'POST'])
@login_required
def add_tithe():
    members = Member.query.all()
    if request.method == 'POST':
        try:
            amount = float(request.form['amount'])
            member_id = request.form.get('member_id')
            member_id = int(member_id) if member_id else None
            
            tithe = Tithe(
                amount=amount,
                member_id=member_id,
                date=datetime.strptime(request.form['date'], '%Y-%m-%d') if request.form['date'] else datetime.utcnow(),
                method=request.form['method']
            )
            db.session.add(tithe)
            db.session.commit()
            flash('Tithe recorded successfully.')
            return redirect(url_for('finance.index'))
        except Exception as e:
            flash(f'Error recording tithe: {e}')
            
    return render_template('finance/tithe_form.html', members=members, title="Record Tithe")

@bp.route('/offering/add', methods=['GET', 'POST'])
@login_required
def add_offering():
    members = Member.query.all()
    if request.method == 'POST':
        try:
            amount = float(request.form['amount'])
            member_id = request.form.get('member_id')
            member_id = int(member_id) if member_id else None
            
            offering = Offering(
                amount=amount,
                member_id=member_id,
                category=request.form['category'],
                description=request.form['description'],
                date=datetime.strptime(request.form['date'], '%Y-%m-%d') if request.form['date'] else datetime.utcnow(),
                method=request.form['method']
            )
            db.session.add(offering)
            db.session.commit()
            flash('Offering recorded successfully.')
            return redirect(url_for('finance.index'))
        except Exception as e:
            flash(f'Error recording offering: {e}')

    return render_template('finance/offering_form.html', members=members, title="Record Offering")
