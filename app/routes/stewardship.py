from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.extensions import db
from app.models.stewardship import Commitment, Resource, Event, CommitteeMember, Audit
from app.models.core import Member, SystemSetting
from datetime import datetime

bp = Blueprint('stewardship', __name__)

@bp.route('/commitments')
@login_required
def commitments():
    commitments_list = Commitment.query.all()
    return render_template('stewardship/commitments.html', commitments=commitments_list)

@bp.route('/commitments/add', methods=['GET', 'POST'])
@login_required
def add_commitment():
    members = Member.query.all()
    if request.method == 'POST':
        try:
            member_id = request.form.get('member_id')
            member_id = int(member_id) if member_id else None
            
            commitment = Commitment(
                member_id=member_id,
                type=request.form['type'],
                description=request.form['description'],
                status='Active'
            )
            db.session.add(commitment)
            db.session.commit()
            flash('Commitment added successfully.')
            return redirect(url_for('stewardship.commitments'))
        except Exception as e:
            flash(f'Error adding commitment: {e}')
            
    return render_template('stewardship/commitment_form.html', members=members, title="Add Commitment")

@bp.route('/education')
@login_required
def education():
    resources = Resource.query.all()
    return render_template('stewardship/education.html', resources=resources)

@bp.route('/education/add', methods=['GET', 'POST'])
@login_required
def add_resource():
    if request.method == 'POST':
        try:
            resource_type = request.form['type']
            url = request.form.get('url') # Default to form URL
            
            if resource_type in ['Document', 'Sermon', 'Video']:
                if 'file' not in request.files:
                    flash('No file part')
                    return redirect(request.url)
                file = request.files['file']
                if file.filename == '':
                    flash('No selected file')
                    return redirect(request.url)
                if file:
                    from werkzeug.utils import secure_filename
                    import os
                    from flask import current_app
                    
                    filename = secure_filename(file.filename)
                    # Unique filename to prevent overwrite
                    import uuid
                    unique_filename = f"{uuid.uuid4().hex}_{filename}"
                    upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
                    file.save(upload_path)
                    url = url_for('static', filename=f'uploads/{unique_filename}')

            resource = Resource(
                title=request.form['title'],
                type=resource_type,
                url=url
            )
            db.session.add(resource)
            db.session.commit()
            flash('Resource added successfully.')
            return redirect(url_for('stewardship.education'))
        except Exception as e:
            flash(f'Error adding resource: {e}')

    return render_template('stewardship/resource_form.html', title="Add Resource")


# ... (Commitment and Education routes remain unchanged)

@bp.route('/events')
@login_required
def events():
    events_list = Event.query.order_by(Event.date.asc()).all()
    return render_template('stewardship/events.html', events=events_list)

@bp.route('/events/add', methods=['GET', 'POST'])
@login_required
def add_event():
    if request.method == 'POST':
        try:
            date_str = request.form['date']
            time_str = request.form['time']
            # Combine date and time
            dt_str = f"{date_str} {time_str}"
            event_date = datetime.strptime(dt_str, '%Y-%m-%d %H:%M')
            
            event = Event(
                title=request.form['title'],
                date=event_date,
                location=request.form['location'],
                type=request.form['type'],
                description=request.form['description']
            )
            db.session.add(event)
            db.session.commit()
            flash('Event added successfully.')
            return redirect(url_for('stewardship.events'))
        except Exception as e:
            flash(f'Error adding event: {e}')
            
    return render_template('stewardship/event_form.html', title="Add Event")

@bp.route('/committee')
@login_required
def committee():
    committee_members = CommitteeMember.query.filter_by(status='Active').all()
    return render_template('stewardship/committee.html', members=committee_members)

@bp.route('/committee/add', methods=['GET', 'POST'])
@login_required
def add_committee_member():
    members = Member.query.all()
    if request.method == 'POST':
        try:
            member_id = request.form['member_id']
            term_start_str = request.form['term_start']
            term_start = datetime.strptime(term_start_str, '%Y-%m-%d').date()
            
            term_end_str = request.form.get('term_end')
            term_end = datetime.strptime(term_end_str, '%Y-%m-%d').date() if term_end_str else None

            committee_member = CommitteeMember(
                member_id=member_id,
                role=request.form['role'],
                term_start=term_start,
                term_end=term_end,
                status='Active'
            )
            db.session.add(committee_member)
            db.session.commit()
            flash('Committee member added successfully.')
            return redirect(url_for('stewardship.committee'))
        except Exception as e:
            flash(f'Error adding committee member: {e}')
            
    return render_template('stewardship/committee_form.html', members=members, title="Add Committee Member")

@bp.route('/audit')
@login_required
def audit():
    audits = Audit.query.order_by(Audit.date.desc()).all()
    return render_template('stewardship/audit.html', audits=audits)

@bp.route('/audit/add', methods=['GET', 'POST'])
@login_required
def add_audit():
    if request.method == 'POST':
        try:
            audit_date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
            
            audit = Audit(
                year=request.form['year'],
                quarter=request.form['quarter'],
                date=audit_date,
                auditor=request.form['auditor'],
                status=request.form['status'],
                findings=request.form['findings'],
                recommendations=request.form['recommendations']
            )
            db.session.add(audit)
            db.session.commit()
            flash('Audit record added successfully.')
            return redirect(url_for('stewardship.audit'))
        except Exception as e:
            flash(f'Error adding audit record: {e}')
            
    return render_template('stewardship/audit_form.html', title="Add Audit Record")

@bp.route('/audit/<int:id>')
@login_required
def view_audit(id):
    audit = Audit.query.get_or_404(id)
    return render_template('stewardship/audit_view.html', audit=audit)

@bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    setting = SystemSetting.query.first()
    if not setting:
        setting = SystemSetting(church_name='My Local Church', conference_name='My Conference')
        db.session.add(setting)
        db.session.commit()
        
    if request.method == 'POST':
        try:
            setting.church_name = request.form['church_name']
            setting.conference_name = request.form['conference_name']
            setting.currency_symbol = request.form['currency_symbol']
            db.session.commit()
            flash('System settings updated successfully.')
            return redirect(url_for('stewardship.settings'))
        except Exception as e:
            flash(f'Error updating settings: {e}')
            
    return render_template('stewardship/settings.html', setting=setting)
