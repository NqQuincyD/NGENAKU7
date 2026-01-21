from flask import Blueprint, render_template
from flask_login import login_required
from app.models.finance import Tithe, Offering
from app.extensions import db
from sqlalchemy import func
from datetime import datetime

bp = Blueprint('reports', __name__)

@bp.route('/')
@login_required
def index():
    # Simple summary data for now
    total_tithe = db.session.query(func.sum(Tithe.amount)).scalar() or 0
    total_offering = db.session.query(func.sum(Offering.amount)).scalar() or 0
    
    # Group by category for offering
    offering_by_category = db.session.query(
        Offering.category, func.sum(Offering.amount)
    ).group_by(Offering.category).all()
    
    # Prepare distribution chart data
    dist_labels = [row[0] for row in offering_by_category]
    dist_values = [row[1] for row in offering_by_category]

    # Monthly Trends (Last 12 Months)
    trend_labels = []
    tithe_values = []
    offering_values = []
    
    current_date = datetime.now()
    for i in range(11, -1, -1):
        target_date = current_date.replace(day=1)
        y, m = target_date.year, target_date.month - i
        while m <= 0:
            m += 12
            y -= 1
            
        month_name = datetime(y, m, 1).strftime('%b %Y')
        trend_labels.append(month_name)
        
        t_sum = db.session.query(func.sum(Tithe.amount)).filter(
            func.extract('month', Tithe.date) == m,
            func.extract('year', Tithe.date) == y
        ).scalar() or 0
        
        o_sum = db.session.query(func.sum(Offering.amount)).filter(
            func.extract('month', Offering.date) == m,
            func.extract('year', Offering.date) == y
        ).scalar() or 0
        
        tithe_values.append(t_sum)
        offering_values.append(o_sum)

    return render_template('reports/index.html', 
                           total_tithe=total_tithe, 
                           total_offering=total_offering,
                           offering_by_category=offering_by_category,
                           dist_labels=dist_labels,
                           dist_values=dist_values,
                           trend_labels=trend_labels,
                           tithe_values=tithe_values,
                           offering_values=offering_values)
