from flask import request, render_template, send_file
from io import BytesIO
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
from app.main.models import Transactions

def export_to_csv(month):
    # Assume 'month' is in 'YYYY-MM' format
    year, month = month.split('-')
    start_date = datetime(int(year), int(month), 1)
    end_date = start_date + relativedelta(months=1)

    transactions = Transactions.query.filter(Transactions.date >= start_date,
                                             Transactions.date < end_date).all()

    data = []
    for transaction in transactions:
        data.append({
            'Date': transaction.date,
            'Amount': transaction.amount,
            'Category': transaction.category.name,
            'Description': transaction.description,
            'Type': transaction.type,
        })

    df = pd.DataFrame(data)
    output = BytesIO()
    df.to_csv(output, index=False)
    output.seek(0)  # Move to the beginning of the BytesIO buffer

    return send_file(output, mimetype='text/csv', as_attachment=True, download_name='transactions.csv')

#TBD - EXPORT AS PDF (includes charts and transactions list)