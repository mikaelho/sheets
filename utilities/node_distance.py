from decimal import Decimal
from dataclasses import dataclass
from math import atan2
from math import cos
from math import sin
from math import sqrt


@dataclass
class Rectangle:
    center_x: float
    center_y: float
    width: float
    height: float

    @property
    def center(self):
        return self.center_x, self.center_y

    @property
    def dimensions(self):
        return self.width, self.height

    def angle_to(self, other: "Rectangle"):
        delta_x = other.center_x - self.center_x
        delta_y = self.center_y - other.center_y

        return atan2(delta_y, delta_x)

    def center_distance_to(self, other: "Rectangle"):
        delta_x_abs = abs(self.center_x - other.center_x)
        delta_y_abs = abs(self.center_y - other.center_y)
        return sqrt(delta_x_abs ** 2 + delta_y_abs ** 2)

    def magnitude_from_center_to_edge(self, radians: float):
        abs_cos_angle = abs(cos(radians))
        abs_sin_angle = abs(sin(radians))

        if self.width / 2 * abs_sin_angle <= self.height / 2 * abs_cos_angle:
            magnitude = self.width / 2 / abs_cos_angle;
        else:
            magnitude = self.height / 2 / abs_sin_angle;

        return magnitude

    def edge_distance_to(self, other: "Rectangle") -> float:
        center_distance_to = self.center_distance_to(other)

        if center_distance_to < min(self.dimensions):
            return 0.0

        angle_to_other = self.angle_to(other)

        distance = (
            self.center_distance_to(other) -
            self.magnitude_from_center_to_edge(angle_to_other) -
            other.magnitude_from_center_to_edge(angle_to_other)
        )

        return distance if distance > 0 else 0.0


r1 = Rectangle(10, 10, 10, 10)
r2 = Rectangle(50, 10, 10, 10)
r3 = Rectangle(40, 40, 10, 10)

print(r1.edge_distance_to(r2), "==", r2.edge_distance_to(r1))
print(r1.edge_distance_to(r3), "==", r3.edge_distance_to(r1), "==", sqrt(800))
print(r2.edge_distance_to(r3), "==", r3.edge_distance_to(r2))
