from datetime import datetime
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import io
from flask import Flask, render_template, make_response, request, redirect, session, url_for
from flask_wtf import FlaskForm
from wtforms import SubmitField, DateTimeField
import sqlite3
import logging

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secretwordthatyouneedtoguess'

class Datum_azure(FlaskForm):
    start = DateTimeField('Start-date:', format='%d/%m/%Y %H:%M:%S', render_kw={"placeholder": "DD-MM-YYYY H:M:S"})
    end = DateTimeField('End-date:', format='%d/%m/%Y %H:%M:%S', render_kw={"placeholder": "DD-MM-YYYY H:M:S"})
    submit = SubmitField('submit')

def getData():
    conn = sqlite3.connect('/fundamentals/fund.db')
    curs = conn.cursor()
    for row in curs.execute("SELECT * FROM data ORDER BY time_ras DESC LIMIT 1"):
        time = str(row[0])
        temp = row[1]
        hum = row[2]
        pres = row[3]
    conn.close()
    return time, hum, pres, temp

def getNewData(sensor_type, start_date, end_date):
    conn = sqlite3.connect('/fundamentals/fund.db')
    curs = conn.cursor()
    
    try:
        if start_date is None:
            start_date_sql = None
        else:
            start_date_sql = datetime.strptime(start_date, '%d/%m/%Y %H:%M:%S').strftime('%d/%m/%Y %H:%M:%S')
            
        if end_date is None:
            end_date_sql = None
        else:
            end_date_sql = datetime.strptime(end_date, '%d/%m/%Y %H:%M:%S').strftime('%d/%m/%Y %H:%M:%S')

        # Adjust the SQL query to select all data if start_date or end_date is None
        if start_date_sql is None or end_date_sql is None:
            curs.execute(f"SELECT time_ras, {sensor_type} FROM data")
        else:
            curs.execute(f"SELECT time_ras, {sensor_type} FROM data WHERE time_ras BETWEEN ? AND ?",
                         (start_date_sql, end_date_sql))
        
        data = curs.fetchall()
        conn.close()

        return data
    except sqlite3.Error as e:
        logging.error("SQLite error: %s", e)
        return []
    except Exception as e:
        logging.error("An unexpected error occurred: %s", e)
        return []


def create_graph(data, y_label, title, y_min=None, y_max=None):
    fig, ax = plt.subplots()
    timestamps = [datetime.strptime(row[0], '%d/%m/%Y %H:%M:%S') for row in data]
    y_data = [row[1] for row in data]

    ax.plot(timestamps, y_data)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m/%Y %H:%M:%S"))
    ax.set_xlabel("Time")
    ax.set_ylabel(y_label)
    ax.set_title(title)

    if y_min is not None and y_max is not None:
        ax.set_ylim(y_min, y_max)

    ax.grid(True)
    fig.autofmt_xdate()
    return fig

@app.route('/plot/temp')
def graph_temp():
    start_date = session.get('start', None)
    end_date = session.get('end', None)
    data = getNewData('temp', start_date, end_date)
    fig = create_graph(data, "Temperature [°C]", "Temperature Over Time")

    output = io.BytesIO()
    fig.savefig(output, format="png")
    output.seek(0)
    response = make_response(output.read())
    response.mimetype = 'image/png'
    return response

@app.route('/plot/hum')
def graph_hum():
    start_date = session.get('start', None)
    end_date = session.get('end', None)
    data = getNewData('hum', start_date, end_date)
    fig = create_graph(data, "Humidity [%]", "Humidity Over Time")

    canvas = FigureCanvas(fig)
    output = io.BytesIO()
    canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response


@app.route('/plot/pres')
def plot_pres():
    start_date = session.get('start', None)
    end_date = session.get('end', None)
    data = getNewData('pres', start_date, end_date)
    fig = create_graph(data, "Pressure [Hpa]", "Pressure Over Time")

    canvas = FigureCanvas(fig)
    output = io.BytesIO()
    canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response


@app.route("/", methods=['GET', 'POST'])
def index():
    form = Datum_azure()
    if form.validate_on_submit():
        session['start'] = form.start.data.strftime('%d/%m/%Y %H:%M:%S')
        session['end'] = form.end.data.strftime('%d/%m/%Y %H:%M:%S')
        print("Form submitted. Start Date:", session.get('start', 'Not set'))
        print("Form submitted. End Date:", session.get('end', 'Not set'))
        return redirect(url_for('index'))

    if request.method == 'POST':
         if form.start.data is None and form.end.data is None:
            session.pop('start', None)
            session.pop('end', None)
            return redirect(url_for('index'))

    start_date = datetime.strptime(session.get('start', '01/01/1900 00:00:00'), '%d/%m/%Y %H:%M:%S')
    end_date = datetime.strptime(session.get('end', datetime.now().strftime('%d/%m/%Y %H:%M:%S')), '%d/%m/%Y %H:%M:%S')
    print("Start Date:", start_date)
    print("End Date:", end_date)

    time, hum, pres, temp = getData()
    templateData = {
        'time': time,
        'hum': hum,
        'pres': pres,
        'temp': temp,
    }
    return render_template('index.html', **templateData, form=form)

if __name__ == "__main__":
    app.run(host='192.168.137.40', port=5000, debug=True)
