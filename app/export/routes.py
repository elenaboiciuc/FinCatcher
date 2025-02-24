from flask import render_template,request
from flask_login import login_required

from app.export import export
from app.export.export_functions import export_to_csv

@export.route('/export', methods=['GET'])
@login_required # requires the user to be logged in to access this route
def export_data():
    month = request.args.get('month') # get the 'month' query parameter from the URL
    if month: # if a month is specified
        return export_to_csv(month) # call the function to export data to CSV for the specified month

    return render_template('export_data.html', page_title='Export Data', icon='fas fa-download')