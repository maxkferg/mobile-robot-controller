# Stanford Toy Autonomous Racecar


Setup

```sh
sudo pip install -r requirements.txt
python setup.py install
```

## Building the dashboard
The dashbaord is a static html site which communicates with the robot using GraphQL. To build the webpage:
```sh
cd webserver/static
npm i
np run build
```

To run the development environment
```sh
cd /webserver/static
npm install
npm start
```


## Runing the server on the robot
```sh
export PROD=1 && python3 manage.py runserver --host=0.0.0.0 # Production
export python3 manage.py runserver # Development
```

## License
MIT