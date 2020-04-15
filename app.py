import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify

# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Welcome to Hawaii Weather API:<br/>"
        f"<br/>"
        f"These are the available routes:<br/>"
        f"<br/>"
        f"Precipitation results: /api/v1.0/precipitation<br/>"
        f"List of all Stations: /api/v1.0/stations</br>"
        f"Temparature observed for most active station: /api/v1.0/tobs</br>"
        f"Weather stats for start date- enter start date: /api/v1.0/<start></br>"
        f"Weather stats for given start and end dates- enter start and end dates: /api/v1.0/<start>/<end></br>"
    )




@app.route("/api/v1.0/precipitation")
def precipitation():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    """  * Convert the query results to a dictionary using `date` as the key and `prcp` as the value."""
    """ * Return the JSON representation of your dictionary """

    results = session.query(Measurement.date, Measurement.prcp).all()
    session.close()
    prcp_data = []
    for date, prcp in results:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["prcp"] = prcp
        prcp_data.append(precipitation_dict)

    return jsonify(prcp_data)



@app.route("/api/v1.0/stations")
def station():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    """ * Return a JSON list of stations from the dataset """

    results = session.query(Station.station).all()
    session.close()
    station_names = list(np.ravel(results))

    return jsonify(station_names)


@app.route("/api/v1.0/tobs")
def tobs():
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """ Query the dates and temperature observations of the most active station for the last year of data. """
    """ * Return a JSON list of temperature observations (TOBS) for the previous year. """

    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == 'USC00519281').filter(Measurement.date >= year_ago)
    session.close()
    tobs_data = []
    for tobsdata in results:
        tobs_dict = {}
        tobs_dict["station_name"] = 'USC00519281'
        tobs_dict["date"] = tobsdata.date
        tobs_dict["tobs"] = tobsdata.tobs
        tobs_data.append(tobs_dict)

    return jsonify(tobs_data)


@app.route("/api/v1.0/<start>")
def start_stats(start):
    trip_start= dt.datetime.strptime(start, '%Y-%m-%d')

    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a json list of the minimum temperature, the average temperature, and the max temperature for a given start date"""

    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs),func.avg(Measurement.tobs)).filter(Measurement.date >= trip_start).all()
    session.close()
    start_stats = list(np.ravel(results))

    return jsonify(start_stats)
    

@app.route("/api/v1.0/<start>/<end>")
def trip_stats(start, end): 

    # Create our session (link) from Python to the DB
    session = Session(engine)


    """Return a json list of the minimum temperature, the average temperature, and the max temperature for a given start-end date range."""
    """Return a JSON list of tmin, tmax, tavg for the dates in range of start date and end date inclusive"""
    
    trip_dates = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).group_by(Measurement.date).all()
    trip_dates_results=list(trip_dates)
    session.close()

    return jsonify(trip_dates_results)


if __name__ == '__main__':
    app.run(debug=True)
