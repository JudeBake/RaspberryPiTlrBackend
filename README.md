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
* clone the repo
`git clone git@github.com:JudeBake/RaspberryPiTlrBackend.git`
or
`git clone https://github.com/JudeBake/RaspberryPiTlrBackend.git`

* install python3 and pip

`sudo apt install python3 pip`

* install python modules
`sudo pip install flask flask-restful flask-jsonify flask-cors`

* make main script executable
`chmod +x raspberryPiTlr.py`

## Run project
`python3 raspberryPiTlr.py`
or
`./raspberryPiTlr.py`
