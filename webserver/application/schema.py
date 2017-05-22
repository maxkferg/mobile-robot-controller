import graphene
from hardware.car import car as hw
from learning.train import train_car


class CarState(graphene.ObjectType):
    """Mutation return value"""
    rotation = graphene.Float()
    throttle = graphene.Float()

    def __init__(self, *args, **kwargs):
        super(CarState, self).__init__(*args,**kwargs)
        self.rotation = hw.steering.get_rotation()
        self.throttle = hw.throttle.get_throttle()


class CarMutation(graphene.Mutation):
    """Adjust the car steering and throttle"""

    class Input():
        left = graphene.Float()
        right = graphene.Float()
        accelerate = graphene.Float()
        decelerate = graphene.Float()
        reset = graphene.Boolean()
        train = graphene.Boolean()

    car = graphene.Field(lambda: CarState)

    @staticmethod
    def mutate(root, args, context, info):
        left = args.get('left')
        right = args.get('right')
        accelerate = args.get('accelerate')
        decelerate = args.get('decelerate')
        reset = args.get('reset')
        train = args.get('train')

        if train:
            train_car()
        if reset:
            hw.reset()
        if left:
            hw.steering.turn_left(left)
        if right:
            hw.steering.turn_right(right)
        if accelerate:
            hw.throttle.accelerate(accelerate)
        if decelerate:
            hw.throttle.decelerate(decelerate)
        return CarMutation(car=CarState())



class Mutations(graphene.ObjectType):
    controlCar = CarMutation.Field()



class Query(graphene.ObjectType):
    car = graphene.Field(lambda: CarState)
    hello = graphene.String(description='A typical hello world')
    steering = graphene.Float(description='The steering angle of the car')
    throttle = graphene.Float(description='The throttle of the car')

    def resolve_hello(self, args, context, info):
        return 'World'

    def resolve_thottle(self, args, context, info):
        return hw.throttle.get_throttle()

    def resolve_steering(self, args, context, info):
        return hw.steering.get_rotation()

    def resolve_car(self, args, context, info):
        return CarState()



schema = graphene.Schema(query=Query, mutation=Mutations)