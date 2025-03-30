from pydoc import plain


class TypeOfTecnic:
    def __init__(self, control_type):
        self.control_type = control_type

    def get_speed_and_control_type(self):
        return f"{self.get_speed()} управляемый - {self.control_type.get_control_type()}"

    def get_speed(self):
        pass

class Car(TypeOfTecnic):
    def get_speed(self):
        return 80

class Plane(TypeOfTecnic):
    def get_speed(self):
        return 300

class ControlType:
    def get_control_type(self):
        pass

class SteeringWheel(ControlType):
    def get_control_type(self):
        return "рулевым колесом"

class PlaneSteeringWheel(ControlType):
    def get_control_type(self):
        return "штурвалом"


steering_wheel = SteeringWheel()

plain_wheel = PlaneSteeringWheel()

car = Car(steering_wheel)
plane = Plane(plain_wheel)

print(car.get_speed_and_control_type())
print(plane.get_speed_and_control_type())