import graphene
from hardware.motors import steering as steering_controller
from hardware.motors import throttle as throttle_controller



class CarState(graphene.ObjectType):
    """Mutation return value"""
    rotation = graphene.Float()
    throttle = graphene.Float()

    def __init__(self, *args, **kwargs):
        super(CarState, self).__init__(*args,**kwargs)
        self.rotation = steering_controller.get_rotation()
        self.throttle = throttle_controller.get_throttle()


class CarMutation(graphene.Mutation):
    """Adjust the car steering and throttle"""

    class Input:
        left = graphene.Float()
        right = graphene.Float()
        accelerate = graphene.Float()
        decelerate = graphene.Float()
        reset = graphene.Boolean()

    car = graphene.Field(lambda: CarState)

    @staticmethod
    def mutate(root, args, context, info):
        left = args.get('left')
        right = args.get('right')
        accelerate = args.get('accelerate')
        decelerate = args.get('decelerate')
        reset = args.get('reset')
        
        if reset:
            steering_controller.reset()
            throttle_controller.reset()
        if left:
            steering_controller.turn_left(left)
        if right:
            steering_controller.turn_right(right)
        if accelerate:
            throttle_controller.accelerate(accelerate)
        if decelerate:
            throttle_controller.decelerate(decelerate)
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
        return throttle.get_throttle()

    def resolve_steering(self, args, context, info):
        return steering.get_rotation()

    def resolve_car(self, args, context, info):
        return CarState()



schema = graphene.Schema(query=Query, mutation=Mutations)