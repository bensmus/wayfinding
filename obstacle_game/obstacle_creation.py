import pygame
import random
pygame.init()

# Defining colors
BLACK = (0, 0, 0)
GRAY = (200, 200, 220)
RED = (117, 11, 11)
BLUE = (20, 50, 200)
PINK = 139,69,19

WORLDSIZE = 200
SCREENSIZE = 600  # should be a multiple of WORLDSIZE
SCREEN = pygame.display.set_mode((SCREENSIZE, SCREENSIZE))


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def raw(self):
        return (self.x, self.y)

    def scale(self, scalar):
        return Point(self.x * scalar, self.y * scalar)

    def __eq__(self, other):
        if isinstance(other, Point):
            return self.x == other.x and self.y == other.y
        return False

    def __hash__(self):
        return hash(self.raw())

    def __str__(self):
        return f"x = {self.x}, y = {self.y}"


class Rectangle:
    def __init__(self, topleft, width, height):
        self.topleft = topleft
        self.width = width
        self.height = height

    def get_bound_pts(self):
        """
        Get the points on the edge of the rectangle.
        """

        topleft = self.topleft
        width = self.width
        height = self.height

        # if width is 3, we have points 0, 1, 2
        # each pixel takes up space
        topright = Point(topleft.x + width - 1, topleft.y)
        bottomleft = Point(topleft.x, topleft.y + height - 1)
        bottomright = Point(topleft.x + width - 1, topleft.y + height - 1)

        bound_pts = []
        bound_pts.extend((topleft, topright, bottomleft, bottomright))
        bound_pts.extend(get_line_pts(topleft, topright, True))
        bound_pts.extend(get_line_pts(topright, bottomright, False))
        bound_pts.extend(get_line_pts(bottomleft, bottomright, True))
        bound_pts.extend(get_line_pts(topleft, bottomleft, False))

        return bound_pts

    def contains(self, point):
        """
        Check if point is contained within a rectangle.
        Edge points are not contained (> vs >=).
        """
        topleft = self.topleft
        width = self.width
        height = self.height

        min_x = topleft.x
        min_y = topleft.y
        max_x = min_x + width - 1
        max_y = min_y + height - 1
        if point.y > min_y and point.y < max_y and point.x > min_x and point.x < max_x:
            return True
        return False

    def get_all_points(self):
        """
        Get all the points of the rectangle.
        """
        topleft = self.topleft
        width = self.width
        height = self.height

        points = set()
        for x in range(topleft.x, topleft.x + width):
            for y in range(topleft.y, topleft.y + height):
                points.add(Point(x, y))
        return points


def draw_worldpixels(color, points):
    """
    Represent each worldpixel larger so we can see if we are doing everything properly
    """
    scalar = SCREENSIZE / WORLDSIZE
    for point in points:
        scaled_point = point.scale(scalar)
        pygame.draw.rect(SCREEN, color, (scaled_point.x,
                         scaled_point.y, scalar, scalar))

def get_line_pts(point_a, point_b, horiz):
    """
    Interpolate, do not include a or b
    b needs to be more positive than a for this to work.
    """
    pts = []
    if horiz:
        for xcoor in range(point_a.x + 1, point_b.x):
            pts.append(Point(xcoor, point_a.y))
    else:
        for ycoor in range(point_a.y + 1, point_b.y):
            pts.append(Point(point_a.x, ycoor))
    return pts


def reset_start_dest(spawn_pts, start, end):

    if start != None:
        # Clearing previous
        draw_worldpixels(GRAY, [start, end])

    start = random.choice(list(spawn_pts))
    end = random.choice(list(spawn_pts - {start}))
    draw_worldpixels(PINK, [start, end])
    return start, end


def setup(min_obstacle=20, max_obstacle=50, obstacle_count=10):
    """
    Set up the rover start and end points, and the obstacles.
    Returns:
    - wall_pts: list of Points
    - spawn_pts: set of Points
    """

    # WORLDSIZE - 1 is max_coor in general
    max_topleft = (WORLDSIZE - 1) - max_obstacle

    # [Rectangle(topleft, width, height)... ]
    rects = list()

    # The boundary points of every rectangle, without overlap -> one dimensional array
    # (for sonar).
    wall_pts = list()

    # As obstacles get created, pts will be removed from spawn possibilities
    spawn_pts = Rectangle(Point(0, 0), WORLDSIZE, WORLDSIZE).get_all_points()

    # Creating the obstacles.
    for i in range(obstacle_count):
        # Choosing a random point as well as dimensions, overlaps are okay.
        topleft = Point(random.randint(0, max_topleft),
                        random.randint(0, max_topleft))
        width = random.randint(min_obstacle, max_obstacle)
        height = random.randint(min_obstacle, max_obstacle)

        rect = Rectangle(topleft, width, height)
        rects.append(rect)
        spawn_pts -= rect.get_all_points()
        bound_pts = rect.get_bound_pts()

        wall_pts.extend(bound_pts)

    # DO THIS OUTSIDE THE LOOP, WHEN ALL RECTS DEFINED
    # Filter the bound points. If they are inside (not on the edge of) an obstacle, they are removed.
    for rect in rects:
        wall_pts = list(
            filter(lambda point: not rect.contains(point), wall_pts))

    return wall_pts, spawn_pts


if __name__ == '__main__':

    wall_pts, spawn_pts = setup()
    start, dest = reset_start_dest(spawn_pts, None, None)

    SCREEN.fill(GRAY)
    draw_worldpixels(BLACK, wall_pts)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    start, dest = reset_start_dest(spawn_pts, start, dest)

        x, y = pygame.mouse.get_pos()
        print(f'mouse coordinates x = {x:-3}, y = {y:-3}', end='\r')
        pygame.display.update()

    # Done! Time to quit.
    pygame.quit()