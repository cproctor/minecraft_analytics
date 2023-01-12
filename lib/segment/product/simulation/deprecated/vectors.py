
LEFT = (-1, 0, 0)
RIGHT = (1, 0, 0)
DOWN = (0, -1, 0)
UP = (0, 1, 0)
BACK = (0, 0, -1)
FORWARD = (0, 0, 1)

LEFT_CORNERS = (
    (0, 1, 0),
    (0, 0, 0),
    (0, 1, 1),
    (0, 0, 1),
)
RIGHT_CORNERS = (
    (1, 1, 1),
    (1, 0, 1),
    (1, 1, 0),
    (1, 0, 0),
)
DOWN_CORNERS = (
    (1, 0, 1),
    (0, 0, 1),
    (1, 0, 0),
    (0, 0, 0),
)
UP_CORNERS = (
    (0, 1, 1),
    (1, 1, 1),
    (0, 1, 0),
    (1, 1, 0),
)
BACK_CORNERS = (
    (1, 0, 0),
    (0, 0, 0),
    (1, 1, 0),
    (0, 1, 0),
)
FRONT_CORNERS = (
    (0, 0, 1),
    (1, 0, 1),
    (0, 1, 1),
    (1, 1, 1),
)

VECTORS = (LEFT, RIGHT, DOWN, UP, BACK, FORWARD)
FACES = (LEFT_CORNERS, RIGHT_CORNERS, DOWN_CORNERS, UP_CORNERS, BACK_CORNERS, FRONT_CORNERS)

def translate(point, vector):
    px, py, pz = point
    vx, vy, vz = vector
    return (px + vx, py + vy, pz + vz)

def get_face(point, vector, corners):
    return [{"position": translate(point, c), "normal": vector} for c in corners]
