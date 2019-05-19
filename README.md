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

* install python and pip

```
sudo apt install python3 python3-pip
```

* install python modules

```
sudo pip install flask flask-restful flask-jsonpify flask-cors
```

* make main script executable

```
sudo chmod +x raspberryPiTlr.py
```

## Run project

```
python3 raspberryPiTlr.py
```
or

```
./raspberryPiTlr.py
```
