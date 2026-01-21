from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user

bp = Blueprint('main', __name__)

from app.models.core import Member, User
from app.models.finance import Tithe, Offering
from app.extensions import db
from sqlalchemy import func
from datetime import datetime

from app.models.stewardship import Event

@bp.route('/profile', methods=['GET', 'POST'])
@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    # Fetch linked Member record
    member = current_user.member
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        
        # Check if username exists and is not current user
        user_by_name = User.query.filter_by(username=username).first()
        if user_by_name and user_by_name.id != current_user.id:
            flash('Username already taken.')
            return redirect(url_for('main.profile'))
            
        # Check if email exists and is not current user
        user_by_email = User.query.filter_by(email=email).first()
        if user_by_email and user_by_email.id != current_user.id:
            flash('Email already registered.')
            return redirect(url_for('main.profile'))
            
        # Update User fields
        current_user.username = username
        current_user.email = email
        
        new_password = request.form.get('password')
        if new_password:
            current_user.set_password(new_password)
            
        # Update Linked Member fields if exists
        if member:
            member.first_name = request.form.get('first_name')
            member.last_name = request.form.get('last_name')
            member.phone = request.form.get('phone')
            
            dob_str = request.form.get('dob')
            if dob_str:
                member.dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
                
            baptism_str = request.form.get('baptism_date')
            if baptism_str:
                member.baptism_date = datetime.strptime(baptism_str, '%Y-%m-%d').date()
            
            # Also sync email if changed
            member.email = email
            
        db.session.commit()
        flash('Profile updated successfully.')
        return redirect(url_for('main.profile'))
        
    return render_template('main/profile.html', member=member)

@bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    next_event = Event.query.filter(Event.date >= datetime.now()).order_by(Event.date.asc()).first()
    return render_template('home.html', next_event=next_event)

@bp.route('/dashboard')
@login_required
def dashboard():
    # Role-based dashboard logic
    if current_user.role.name == 'Member':
        # 1. Find linked Member record by email
        member = current_user.member
        
        my_monthly_tithe = 0
        my_total_offerings = 0
        my_recent_contributions = []
        
        if member:
            # Financial Stats (Personal)
            current_month = datetime.now().month
            current_year = datetime.now().year
            
            my_monthly_tithe = db.session.query(func.sum(Tithe.amount)).filter(
                Tithe.member_id == member.id,
                func.extract('month', Tithe.date) == current_month,
                func.extract('year', Tithe.date) == current_year
            ).scalar() or 0
            
            my_total_offerings = db.session.query(func.sum(Offering.amount)).filter(
                Offering.member_id == member.id
            ).scalar() or 0
            
            # Recent Contributions (Personal)
            recent_tithes = Tithe.query.filter_by(member_id=member.id).order_by(Tithe.date.desc()).limit(5).all()
            recent_offerings = Offering.query.filter_by(member_id=member.id).order_by(Offering.date.desc()).limit(5).all()
            
            contributions = []
            for t in recent_tithes:
                contributions.append({
                    'date': t.date,
                    'type': 'Tithe',
                    'amount': t.amount,
                    'method': t.method
                })
            for o in recent_offerings:
                contributions.append({
                    'date': o.date,
                    'type': 'Offering (' + o.category + ')',
                    'amount': o.amount,
                    'method': o.method
                })
            
            contributions.sort(key=lambda x: x['date'], reverse=True)
            my_recent_contributions = contributions[:5]

        # Events (Visible to all)
        upcoming_events = Event.query.filter(Event.date >= datetime.now()).order_by(Event.date.asc()).limit(5).all()
        event_count = len(upcoming_events)

        return render_template('main/member_dashboard.html',
                               my_monthly_tithe=my_monthly_tithe,
                               my_total_offerings=my_total_offerings,
                               my_recent_contributions=my_recent_contributions,
                               upcoming_events=upcoming_events,
                               event_count=event_count)

    # ADMIN / DIRECTOR / TREASURER DASHBOARD
    member_count = Member.query.count()
    event_count = Event.query.filter(Event.date >= datetime.now()).count()
    
    # Financial Stats
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    monthly_tithe = db.session.query(func.sum(Tithe.amount)).filter(
        func.extract('month', Tithe.date) == current_month,
        func.extract('year', Tithe.date) == current_year
    ).scalar() or 0
    
    total_offerings = db.session.query(func.sum(Offering.amount)).scalar() or 0
    
    # Recent Contributions
    recent_tithes = Tithe.query.order_by(Tithe.date.desc()).limit(5).all()
    recent_offerings = Offering.query.order_by(Offering.date.desc()).limit(5).all()
    
    contributions = []
    for t in recent_tithes:
        contributions.append({
            'date': t.date,
            'member': t.member,
            'type': 'Tithe',
            'amount': t.amount,
            'method': t.method
        })
    for o in recent_offerings:
        contributions.append({
            'date': o.date,
            'member': o.member,
            'type': 'Offering (' + o.category + ')',
            'amount': o.amount,
            'method': o.method
        })
        
    contributions.sort(key=lambda x: x['date'], reverse=True)
    contributions.sort(key=lambda x: x['date'], reverse=True)
    recent_contributions = contributions[:5]

    # CHART DATA
    # 1. Giving Trends (Last 6 Months)
    trends_labels = []
    trends_values = []
    
    # from dateutil.relativedelta import relativedelta # REMOVED to avoid dependency issues
    
    current_date = datetime.now()
    for i in range(5, -1, -1):
        # Calculate target month and year
        target_date = current_date.replace(day=1) 
        # Logic to subtract months:
        y, m = target_date.year, target_date.month - i
        while m <= 0:
            m += 12
            y -= 1
            
        month_name = datetime(y, m, 1).strftime('%b')
        trends_labels.append(month_name)
        
        # Query sums
        t_sum = db.session.query(func.sum(Tithe.amount)).filter(
            func.extract('month', Tithe.date) == m,
            func.extract('year', Tithe.date) == y
        ).scalar() or 0
        
        o_sum = db.session.query(func.sum(Offering.amount)).filter(
            func.extract('month', Offering.date) == m,
            func.extract('year', Offering.date) == y
        ).scalar() or 0
        
        trends_values.append(t_sum + o_sum)

    # 2. Offering Distribution
    dist_query = db.session.query(Offering.category, func.sum(Offering.amount)).group_by(Offering.category).all()
    dist_labels = [row[0] for row in dist_query]
    dist_values = [row[1] for row in dist_query]

    return render_template('main/dashboard.html', 
                           member_count=member_count,
                           event_count=event_count,
                           monthly_tithe=monthly_tithe,
                           total_offerings=total_offerings,
                           recent_contributions=recent_contributions,
                           trends_labels=trends_labels,
                           trends_values=trends_values,
                           dist_labels=dist_labels,
                           dist_values=dist_values)
