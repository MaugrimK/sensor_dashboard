import getopt
import logging
import sys

from bokeh.embed import components
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
from flask import Flask, render_template, redirect
from apscheduler.schedulers.background import BackgroundScheduler

from sensor_dashboard.camera import Camera
from config import PHOTO_FILE_DIR, DB_PATH, PIN
from sensor_dashboard.db import DB
from sensor_dashboard.temperature_sensor import TempSensor

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

app = Flask(__name__)


@app.route('/')
def homepage():
    return render_template('page.html')

########################################################################
# Photo endpoints
########################################################################
@app.route('/take_photo')
def take_photo():
    error = app.camera.take_photo()
    if error:
        return render_template(
            'error.html',
            error_text='Error while taking a photo'
        )

    return redirect('/latest_photo')


@app.route('/take_fake_photo')
def take_fake_photo():
    _ = app.camera.take_fake_photo()
    return redirect('/latest_photo')


@app.route('/latest_photo')
def latest_photo():
    photo_files = app.camera.get_list_of_photo_files()

    if len(photo_files) == 0:
        return render_template(
            'error.html',
            error_text='There are no photos yet'
        )

    file_name = photo_files[-1]
    return redirect('/photos/{}'.format(file_name))


@app.route('/photos/<file_name>')
def photos(file_name):
    photo_files = app.camera.get_list_of_photo_files()

    return render_template(
        'photos.html',
        file_name=file_name,
        photo_files=photo_files,
    )


@app.route('/delete_photos')
def delete_photos():
    app.camera.delete_all_photos()
    return "All photos deleted"

########################################################################
# Temp/Humidity endpoints
########################################################################
@app.route('/take_measurement')
def take_measurement():
    hum, temp = app.temp_sens.get_measuremet_from_sensor()
    if temp:
        app.db.add_measurement_to_db(temp, hum)
        return "Measurement taken"
    else:
        return render_template(
            'error.html',
            error_text='Error while taking measurements'
        )


@app.route('/take_fake_measurement')
def take_fake_measurement():
    hum, temp = app.temp_sens.get_fake_measurement_from_sensor()
    app.db.add_measurement_to_db(temp, hum)
    return "Measurement taken"


@app.route('/show_measurements')
def show_measurements():
    measurements = app.db.get_db_measurements_list()
    return render_template(
        'measurements.html',
        measurements=measurements,
    )


@app.route('/graph')
def graph():
    df = app.db.get_db_measurements_df()
    if df is None:
        return render_template(
            'error.html',
            error_text='There are no measurements yet'
        )

    source = ColumnDataSource(df)
    plot_temp = figure(x_axis_type='datetime', plot_width=800, plot_height=300)
    plot_temp.line('Time', 'Temperature', source=source, line_width=3,
                   legend_label="temp")
    plot_temp.line('Time', 'Humidity', source=source, line_width=3,
                   line_color='red', legend_label="hum")
    script_temp, div_temp = components(plot_temp)

    return render_template(
        'graph.html',
        div_temp=div_temp,
        script_temp=script_temp,
        )


@app.route('/delete_measurements')
def delete_measurements():
    app.db.delete_all_measurements()
    return "All measurements deleted"


def take_periodic_measurement():
    logger.debug('Taking measurement')
    hum, temp = app.temp_sens.get_measuremet_from_sensor()
    if temp:
        app.db.add_measurement_to_db(temp, hum)


def delete_older_than_one_week():
    logger.info('Deleting measurements older than 1 week')
    app.db.delete_older_than_one_week()


def create_periodic_tasks():
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        take_periodic_measurement,
        'interval',
        minutes=2,
        id='job_measurement'
        )
    scheduler.add_job(
        delete_older_than_one_week,
        'interval',
        hours=10,
        id='job_delete_old_measurements'
        )
    scheduler.start()


def create_app(args_config):
    app.camera = Camera(
        photo_file_dir=args_config.get('photo-dir') or PHOTO_FILE_DIR,
        fake_measurements=args_config.get('fake-measurements', False)
        )
    app.db = DB(
        db_path=args_config.get('db-path') or DB_PATH
    )
    app.temp_sens = TempSensor(
        pin=args_config.get('pin') or PIN,
        fake_measurements=args_config.get('fake-measurements', False)
    )

    create_periodic_tasks()

    # use_reloader is set to False because flask in debug mode loads the app
    # twice so the scheduled jobs are duplicated
    app.run(host='0.0.0.0', debug=True, use_reloader=False)


def parse_args():
    arg_names = \
        ['fake-measurements', 'pin=', 'db-path=', 'photo-dir=', 'debug']

    args_config = {}
    opts, _ = getopt.getopt(sys.argv[1:], 'x', arg_names)
    for o, v in opts:
        if o == '--fake-measurements':
            args_config['fake-measurements'] = True

        if o == '--pin':
            args_config['pin'] = v

        if o == '--db-path':
            args_config['db-path'] = v

        if o == '--photo-dir':
            args_config['photo-dir'] = v

        if o == '--debug':
            logger.setLevel(logging.DEBUG)

    return args_config


if __name__ == '__main__':
    args_config = parse_args()
    create_app(args_config)
