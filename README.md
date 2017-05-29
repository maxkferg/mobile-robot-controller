#Stanford Toy Autonomous Racecar


Setup

```
sudo pip install -r requirements.txt
python setup.py install
source setup.sh
```

## Server

```sh
sudo python3 manage.py runserver --host=0.0.0.0 # Production
export DEV=1 && python3 manage.py runserver --host=0.0.0.0 # Dev
```

## Simulations

```sh
sudo python3 manage.py simulate # Production
export DEV=1 && python3 manage.py simulate # Dev
```

## Learning Algorithm

```sh
sudo python3 manage.py train # Production
export DEV=1 && python3 manage.py train  # Dev
```

## Dashboard
```sh
cd /webserver/static
npm install
npm start
```


