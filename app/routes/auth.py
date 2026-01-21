from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from app.extensions import db
from app.models.core import User
from urllib.parse import urlparse

bp = Blueprint('auth', __name__)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists.')
            return redirect(url_for('main.index'))
        if User.query.filter_by(email=email).first():
            flash('Email already exists.')
            return redirect(url_for('main.index'))
            
        # Default role: Member (ensure 'Member' role exists in seed_db)
        # Default role: Member (ensure 'Member' role exists in seed_db)
        from app.models.core import Role, Member
        member_role = Role.query.filter_by(name='Member').first()
        
        user = User(username=username, email=email, role=member_role)
        user.set_password(password)
        db.session.add(user)
        
        # Auto-create Member record or Link to existing
        existing_member = Member.query.filter_by(email=email).first()
        if existing_member:
            existing_member.user_id = user.id
            db.session.add(existing_member)
        else:
            member = Member(first_name=username, email=email, user_id=user.id)
            db.session.add(member)
        
        db.session.commit()
        
        flash('Registration successful. Please log in.')
        return redirect(url_for('main.index'))
        
    return redirect(url_for('main.index'))

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user is None or not user.check_password(password):
            flash('Invalid username or password')
            return redirect(url_for('main.index'))
            
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('main.dashboard')
        return redirect(next_page)
        
    return redirect(url_for('main.index'))

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
