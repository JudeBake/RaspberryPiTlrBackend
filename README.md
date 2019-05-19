# RaspberryPiTlrBackend
Raspberry Pi Time-Lapse Recorder Backend

## Dependencies
* Mandatory
    * python3
    * pip
    * picamera
    * flask
    * flask-restful
    * flask-jsonify
    * flask-cors
* Frontend
    * [RaspberryPiTlrFrontend](https://github.com/JudeBake/RaspberryPiTlrFrontend "Frontend Repo")

## Setup project
* enable the camera interface and make sure the pi is updated to the latest

* clone the repo

```
git clone git@github.com:JudeBake/RaspberryPiTlrBackend.git
```

or

```
git clone https://github.com/JudeBake/RaspberryPiTlrBackend.git
```

* setup virtual environment and activate it

```
python3 -m venv venv

source venv/bin/activate
```

* install dependencies module

```
pip install picamera flask flask-restful flask-jsonpify flask-cors
```

## Run project

```
export FLASK_APP=raspberryPiTlr.py

export FLASK_APP=raspberryPiTlr.py #if running debug

flask run --host=0.0.0.0 --port=5000
```
