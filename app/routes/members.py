from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.extensions import db
from app.models.core import Member, Church
from datetime import datetime
from sqlalchemy.exc import IntegrityError

bp = Blueprint('members', __name__)

@bp.route('/')
@login_required
def index():
    members = Member.query.all()
    return render_template('members/list.html', members=members)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        try:
            member = Member(
                first_name=request.form['first_name'],
                last_name=request.form['last_name'],
                email=request.form['email'],
                phone=request.form['phone'],
                dob=datetime.strptime(request.form['dob'], '%Y-%m-%d').date() if request.form['dob'] else None,
                baptism_date=datetime.strptime(request.form['baptism_date'], '%Y-%m-%d').date() if request.form['baptism_date'] else None
            )
            db.session.add(member)
            db.session.commit()
            flash('Member added successfully.')
            return redirect(url_for('members.index'))
        except IntegrityError:
            db.session.rollback()
            flash('Error: This user (email) already exists.')
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding member: {e}')
            
    return render_template('members/form.html', title='Add Member')

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    member = Member.query.get_or_404(id)
    if request.method == 'POST':
        try:
            member.first_name = request.form['first_name']
            member.last_name = request.form['last_name']
            member.email = request.form['email']
            member.phone = request.form['phone']
            member.dob = datetime.strptime(request.form['dob'], '%Y-%m-%d').date() if request.form['dob'] else None
            member.baptism_date = datetime.strptime(request.form['baptism_date'], '%Y-%m-%d').date() if request.form['baptism_date'] else None
            
            db.session.commit()
            flash('Member updated successfully.')
            return redirect(url_for('members.index'))
        except IntegrityError:
            db.session.rollback()
            flash('Error: This user (email) already exists.')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating member: {e}')

    return render_template('members/form.html', title='Edit Member', member=member)

@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    member = Member.query.get_or_404(id)
    db.session.delete(member)
    db.session.commit()
    flash('Member deleted.')
    return redirect(url_for('members.index'))
