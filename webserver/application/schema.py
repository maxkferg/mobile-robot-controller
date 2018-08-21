import os
import graphene
from .hardware import MotorController, clip_verbose

isProd = os.environ.get('PROD')
motor = MotorController(isProd)


class CarState(graphene.ObjectType):
    """Mutation return value"""
    leftWheel = graphene.Float()
    rightWheel = graphene.Float()

    def set_state(self, left_wheel, right_wheel):
        """Set the state on true hardware"""
        self.leftWheel = clip_verbose(left_wheel, -100, 100)
        self.rightWheel = clip_verbose(right_wheel, -100, 100)
        motor.drive(1, self.leftWheel)
        motor.drive(2, self.rightWheel)

    def __del__(self):
        motor.stop()


car = CarState(leftWheel=0, rightWheel=0)


class CarMutation(graphene.Mutation):
    """Adjust the car steering and throttle"""

    class Arguments:
        leftWheel = graphene.Float()
        rightWheel = graphene.Float()

    car = graphene.Field(lambda: CarState)

    def mutate(self, info, leftWheel, rightWheel):
        car.set_state(leftWheel, rightWheel)
        return CarMutation(car=car)



class Mutations(graphene.ObjectType):
    controlCar = CarMutation.Field()



class Query(graphene.ObjectType):
    car = graphene.Field(lambda: CarState)
    hello = graphene.String(description='A typical hello world')
    leftWheel = graphene.Float(description='Velocity of the leftWheel wheel')
    rightWheel = graphene.Float(description='Velocity of the rightWheel wheel')

    def resolve_hello(self, info, **kwargs):
        return 'World'

    def resolve_leftWheel(self, info, **kwargs):
        return 6

    def resolve_rightWheel(self, info, **kwargs):
        return 8

    def resolve_car(self, info, **kwargs):
        return car



schema = graphene.Schema(query=Query, mutation=Mutations)
