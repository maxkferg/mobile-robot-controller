#Stanford Toy Autonomous Racecar


Setup

```
sudo pip install -r requirements.txt
python setup.py install
source setup.sh
```

Running the control dashboard

```sh
export CAR=1 && sudo python car.py runserver --port=80
```

Developing the car dashboard
```sh
cd /webserver/static
npm install
npm start
```


