import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, app, jsonify

engine = create_engine("sqlite:///hawaii.sqlite")
connect = engine.connect()

Base = automap_base()
Base.prepare(engine, reflect = True)

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

#Create FLASK
app = Flask(__name__)

@app.route('/')
def welcome():
    return(f"Climate App<br/>"
    f"---------------------------<br/>"
    f"Available Routes<br/>"
    f"---------------------------<br/>"
    f"/api/v1.0/precipitation<br/>"
    f"/api/v1.0/stations<br/>"
    f"/api/v1.0/tobs<br/>"
    f"/api/v1.0/dates/start<br/>"
    f"/api/v1.0/dates/start/end"
    )

@app.route("/api/v1.0/precipitation")
def rain():
    session = Session(engine)

    rainfall = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    prcp_data = []
    for date, prcp in rainfall:
        rain_dict = {}
        rain_dict["date"] = date
        rain_dict["prcp"] = prcp
        prcp_data.append(rain_dict)

    return jsonify(prcp_data)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    unique_stations = session.query(Measurement.station).distinct().all()
    session.close()
    
    all_stations = list(np.ravel(unique_stations))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def temps():
    
    session = Session(engine)
    active_stations = session.query(Measurement.date,Measurement.tobs).filter(Measurement.station == 'USC00519281').\
    group_by(Measurement.date).\
    order_by(Measurement.date.desc()).all()
    session.close()

    active_data = []
    for dates, fahrens in active_stations:
        active_dict = {}
        active_dict["date"] = dates
        active_dict["temperature"] = fahrens
        active_data.append(active_dict)

    return jsonify(active_data)

@app.route("/api/v1.0/dates/<start>")
def date_time(start):
    session = Session(engine)
    
    minim = list(np.ravel(session.query(func.min(Measurement.tobs)).filter(Measurement.date >= start).all()))
    maxim = list(np.ravel(session.query(func.max(Measurement.tobs)).filter(Measurement.date >= start).all()))
    averg = list(np.ravel(session.query(func.avg(Measurement.tobs)).filter(Measurement.date >= start).all()))
    
    tobs_dict1 = {'TMIN': minim[0],'TMAX':maxim[0], 'TAVG':averg[0]}

    session.close()

    return jsonify(tobs_dict1)

@app.route("/api/v1.0/dates/<start>/<end>")
def start_end(start, end):
    session = Session(engine)
    
    minim = list(np.ravel(session.query(func.min(Measurement.tobs)).filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()))
    maxim = list(np.ravel(session.query(func.max(Measurement.tobs)).filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()))
    averg = list(np.ravel(session.query(func.avg(Measurement.tobs)).filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()))
    
    tobs_dict2 = {'TMIN':minim[0], 'TMAX':maxim[0], 'TAVG':averg[0]}

    session.close()
    
    return jsonify(tobs_dict2)
    

if __name__ == "__main__":
    app.run(debug=True)