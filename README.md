# RaspberryPiTlrBackend
Raspberry Pi Time-Lapse Recorder Backend. This application can be run on a
Raspberry Pi Zero, but processing will take for ever. So it's better to run
it on regular Raspberry Pi.

## Dependencies
* Mandatory
    * python3
    * pip
    * picamera
    * flask
    * flask-socketio
    * flask-jsonify
    * flask-cors
    * pymediainfo
    * libmediainfo-dev
* Frontend
    * [RaspberryPiTlrFrontend](https://github.com/JudeBake/RaspberryPiTlrFrontend "Frontend Repo")

## Setup project
* install libmediainof-dev

```
sudo apt install libmediainfo-dev
```

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
pip install picamera flask flask-socketio flask-jsonpify flask-cors pymediainfo
```

## Run project
in the virtual environment

```
python raspberryPiTlr.py
```

## Contribution
Any body is welcome to contribute. For any questions you can contact me [julien.bacon.1@gmail.com](mailto:julien.bacon.1@gmail.com)

## TO-DO list
* Move camera stuff in its own module
* ~~Adding support for managing and downloading time-lapses~~
* Adding support for adjusing camera settings
* Adding documentation for service setup
* Adding tests
* ~~Adding documentation for contributing~~
* Adding support for the Ultimaker 3 API
* Beefing error handling
* Remove hardcoded stuff (config in sync with frontend)
