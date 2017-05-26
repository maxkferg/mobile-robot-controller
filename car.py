from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from webserver.application.app import app, db
from learning.train import train_car, train_simulation

migrate = Migrate(app, db)
manager = Manager(app)

# migrations
manager.add_command('db', MigrateCommand)


@manager.command
def create_db():
    """Creates the db tables."""
    db.create_all()


@manager.command
def simulate():
    """Train the car using the simulation"""
    train_simulation()


@manager.command
def train():
    """Train the car using the physical hardware"""
    train_car()


if __name__ == '__main__':
    manager.run()
