import logging
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
    logger.setLevel(level)
    ch = logging.StreamHandler()
    ch.setLevel(level)
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)


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


if __name__ == '__main__':
    setup_logger('hardware',logging.INFO)
    setup_logger('learning',logging.INFO)
    setup_logger('webserver',logging.INFO)
    manager.run()
