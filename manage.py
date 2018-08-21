import logging
from flask_script import Manager
from webserver.application.app import app

manager = Manager(app)


def setup_logger(name,level):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(level)
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
    ch.setFormatter(formatter)


@manager.command
def sonar():
    """Run the sonar sensors and print their values"""
    while True:
        for i in range(11):
            car.front_sonar.tick()
            car.rear_sonar.tick()
        print("Front:", car.front_sonar.distance())
        print("Rear:", car.rear_sonar.distance())

@manager.command
def encoders():
    """Print the encoder values for debugging"""
    while True:
        for i in range(11):
            car.front_sonar.tick()
            car.rear_sonar.tick()
        print("Front:", car.front_sonar.distance())
        print("Rear:", car.rear_sonar.distance())




if __name__ == '__main__':
    setup_logger('webserver',logging.INFO)
    manager.run()
