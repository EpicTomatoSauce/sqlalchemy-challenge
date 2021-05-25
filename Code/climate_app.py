# import all prior dependencies + Flask.
import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# Set up database
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect = True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# Flask Setup
app = Flask(__name__)

# Flask routes

################################################################
# root (/) = homepage which lists all routes that are available.
@app.route("/")
def home_page():
    return(
        f"Welcome to the Hawaii Climate API<br/><br/>"
        f"Available Routes:<br/><br/>"
        f"Precipation data:<br/>"
        f"/api/v1.0/precipitation<br/><br/>"
        f"Weather station information:<br/>"
        f"/api/v1.0/stations<br/><br/>"
        f"Temperature Observations for the previous year of last datapoint:<br/>"
        f"/api/v1.0/tobs<br/><br/>"
        f"Find the minimum, average and maximum temperatures for a given start date in 'yyyy-mm-dd' format:<br/>"
        f"/api/v1.0/temps/&lt;start date&gt;<br/><br/>"
        f"Find the minimum, average and maximum temperatures between a given start and end date in 'yyyy-mm-dd' format:<br/>"
        f"/api/v1.0/temps/&lt;start date&gt;/&lt;end date&gt;<br/>"
    )
    
################################################################
# route 1 - precipitation
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    
    results = session.query(Measurement.date, Measurement.prcp).all()
    
    session.close()
    
    precipitation = []
    for result in results:
        precip_dictionary = {}
        # in the dictionary, set the first result (0) (date) as key and prcp as value
        precip_dictionary[result[0]] = result[1]
        precipitation.append(precip_dictionary)
        
    return jsonify (precipitation)

################################################################
# route 2 - station information
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    
    results = session.query(Station.station, Station.name).all()
    
    session.close()
    
    station_list = []
    for result in results:
        station_dictionary = {}
        # result 0 = station, result 1 = station name
        # https://github.com/nlohmann/json/issues/660
        # JSON natively does not preserve insertion order and will instead by alphabetical.
        station_dictionary["station"] = result[0]
        station_dictionary["name"] = result[1]
        station_list.append(station_dictionary)
        
    return jsonify (station_list)

################################################################
# route 3 - tobs information
# Query the dates and temperature observations of the most active station for the last year of data.
# From climate_starter:
# Calculate the date 1 year ago from the last data point in the database
year_minus_365 = dt.date(2017,8,23) - dt.timedelta(days=365)
latest_year = dt.date(2017,8,23)
# most activate station:
most_active_station = "USC00519281"

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    
    # filter date range to be greater than year_minus_365 to provide past year data
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= year_minus_365).filter(Measurement.station == most_active_station).all()
    
    session.close()
    
    tobs_list = [0]
    for result in results:
        tobs_dictionary = {}
        tobs_dictionary["date"] = result[0]
        tobs_dictionary["temperature observed"] = result[1]
        tobs_list.append(tobs_dictionary)
        
    return jsonify (tobs_list)

################################################################
# route 4 - Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.

# https://koenwoortman.com/python-flask-multiple-routes-for-one-function/
@app.route("/api/v1.0/temps/<start>")
@app.route("/api/v1.0/temps/<start>/<end>")
def stats(start=None, end=None):
    
    sel = [func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)]
    
    # https://stackoverflow.com/questions/16739555/python-if-not-syntax
    if not end:
        results = session.query(*sel).filter(Measurement.date >= start).all()
        
        session.close()
        
        temp_data = list(np.ravel(results))
            
        return jsonify (temp_data)
    
    # if end != None then include filter of end date
    results = session.query(*sel).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    
    session.close()
    
    temp_data = list(np.ravel(results))
        
    return jsonify (temp_data)
    
    
if __name__ == '__main__':
    app.run(debug = True)