from flask import render_template,request
from flask_login import login_required

from app.export import export
from app.export.export_functions import export_to_csv

@export.route('/export', methods=['GET'])
@login_required
def export_data():
    month = request.args.get('month')
    if month:
        return export_to_csv(month)

    return render_template('export_data.html', page_title='Export Data', icon='fas fa-download')