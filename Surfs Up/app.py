import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
measure = Base.classes.measurement
station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

#Welcome Page
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

#Precipitation
@app.route("/api/v1.0/precipitation")
def prcp():
    # Create our session (link) from Python to the DB
    session = Session(engine)

        #get all precipitation data using dates found in jupyter
        allprcp = session.query(measure.date,measure.prcp).filter(measure.date >= '2016-01-23').filter(measure.date <= '2017-01-23').all()
    session.close()

    #Convert the query results to a dictionary using date as the key and prcp as the value.
    prcp1617 = []
    for date, prcp in allprcp:
        prcpdict = {}
        prcpdict["date"] = date
        prcpdict["prcp"] = prcp
        prcp1617.append(prcpdict)
    return jsonify(prcp1617)


#Stations
@app.route("/api/v1.0/stations")
def station():
    # Create our session (link) from Python to the DB
    session = Session(engine)

        #Query to get all stations
        stations = (session.query(measure.station, func.count(measure.station)).group_by(measure.station).order_by(func.count(measure.station).desc()).all())
    session.close()
    
    #covert data
    stations_list = list(np.ravel(stations))
    return jsonify(stations_list)

#Temperature Observations
@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
        #get dates for past year
        startdate = dt.date(2016, 1, 23)
        alltemps = session.query(measure.tobs).filter(measure.date >= startdate).all()
    session.close()

    #convert data
    tobs_list = list(np.ravel(alltemps))
    return jsonify(tobs_list)

#Start Date
@app.route("/api/v1.0/<start>")
def startonly(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)
                  
        #get temp data from start to end of data
        start_temps = session.query(measure,func.avg(measure.tobs).label('TAVG'),func.max(measure.tobs).label('TMAX'),func.min(measure.tobs).label('TMIN')).filter(measure.date >= start).first()
    session.close()

    #convert data to dict
    start_tobs = []
    tobs_dict = {}
    tobs_dict["TMIN"] = start_temps.TMIN
    tobs_dict["TMAX"] = start_temps.TMAX
    tobs_dict["TAVG"] = start_temps.TAVG
    start_tobs.append(tobs_dict)
    return jsonify(start_tobs)


#Start/End Date
@app.route("/api/v1.0/<start>/<end>")
def startend(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

        #get temp data from start to end
        startend_temps = session.query(measure,func.avg(measure.tobs).label('TAVG'),func.max(measure.tobs).label('TMAX'),func.min(measure.tobs).label('TMIN')).filter((measure.date >= start)&(measure.date <= end).first()
    session.close()

    #convert data to dict
    startend_tobs = []
    tobs2_dict = {}
    tobs2_dict["TMIN"] = startend_temps.TMIN
    tobs2_dict["TMAX"] = startend_temps.TMAX
    tobs2_dict["TAVG"] = startend_temps.TAVG
    startend_tobs.append(tobs2_dict)
    return jsonify(startend_tobs)


if __name__ == '__main__':
    app.run(debug=True)