import logging
from hardware.car import car
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from webserver.application.app import app, db
from learning.train import train_car_ddpg, train_simulation_ddpg

migrate = Migrate(app, db)
manager = Manager(app)

# migrations
manager.add_command('db', MigrateCommand)


def setup_logger(name,level):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(level)
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
    ch.setFormatter(formatter)
    #logger.addHandler(ch)


@manager.command
def create_db():
    """Creates the db tables."""
    db.create_all()


@manager.command
def simulate():
    """Train the car using the simulation"""
    train_simulation_ddpg()


@manager.command
def train():
    """Train the car using the physical hardware"""
    train_car_ddpg()


@manager.command
def demo():
    """Run the DDPG pendulum demo"""
    from learning.algorithms.ddpg.demo import demo
    from learning.configs.ddpg import demo as config
    demo(config)


@manager.command
def sonar():
    """Run the sonar sensors and print their values"""
    while True:
        for i in range(11):
            car.front_sonar.tick()
            car.rear_sonar.tick()
        print("Front:", car.front_sonar.distance())
        print("Rear:", car.rear_sonar.distance())



if __name__ == '__main__':
    setup_logger('hardware',logging.INFO)
    setup_logger('learning',logging.INFO)
    setup_logger('webserver',logging.INFO)
    manager.run()
