from flask import request, render_template, send_file
from io import BytesIO
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
from flask_login import current_user
from app.main.models import Transactions


def export_to_csv(month):
    # extract year and month from 'YYYY-MM' format
    year, month = month.split('-')
    # create a datetime object for the first day of the given month
    start_date = datetime(int(year), int(month), 1)
    # calculate the first day of the next month
    end_date = start_date + relativedelta(months=1)

    # query the database for transactions within the specified month and user_id
    transactions = Transactions.query.filter(
        Transactions.date >= start_date,
        Transactions.date < end_date,
        Transactions.user_id == current_user.user_id
    ).all()

    # prepare data for CSV export
    data = []
    for transaction in transactions:
        # create a dictionary for each transaction
        data.append({
            'Date': transaction.date,
            'Amount': transaction.amount,
            'Category': transaction.category.name,
            'Description': transaction.description,
            'Type': transaction.type,
        })

    # convert the data to a pandas DataFrame
    df = pd.DataFrame(data)
    # DataFrame = 2-dimensional labeled data structure in pandas, similar to a spreadsheet or SQL table.
    # each dictionary from data list becomes a row in the DataFrame, with the keys as column names

    #create an in-memory file-like object
    output = BytesIO()
    # this creates a binary stream in memory, will be used as a file-like object
    # BytesIO is part of Python's io module and allows us to work with bytes in memory as if it were a file on disk
    # this is useful because we don't need to create an actual file on the server's filesystem

    # converts the DataFrame to CSV format and writes it in the output BytesIO object
    df.to_csv(output, index=False) # index=False parameter tells pandas not to write the index of the DF as a column in the CSV


    output.seek(0)  # move to the beginning of the BytesIO buffer
    # in file operations, there's a concept of a "file pointer" or "cursor."
    # this is an internal marker that keeps track of where you are in the file
    # when you write to a file (or a file-like object like BytesIO), the pointer moves forward with each write operation
    # when you read from a file, you start reading from wherever the pointer currently is
    # this ensures that when Flask's send_file() function starts reading the data to send to the user, it begins from the start of our CSV data

    # create a file name that includes the month and user
    filename = f'transactions_{current_user.user_name}_{year}_{month}.csv'

    # send the CSV file to the user as a downloadable attachment with the new filename
    return send_file(output, mimetype='text/csv', download_name=filename) #Multipurpose Internet Mail Extensions

    # mime - a way to identify the type of data being transmitted over the internet
    # it's a standard that helps applications and web browsers understand the content they are receiving

#TODO - EXPORT AS PDF (includes charts and transactions list)