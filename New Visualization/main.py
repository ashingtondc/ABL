# Monte Carlo Simulator.py

# import userguide.txt, rollout_plan.txt
import time
import datetime
import argparse
import pygame
import random
import math
import sys
from itertools import combinations
from operator import attrgetter


class Logger(object):
    """Class for a logger which mirrors all output to sys.stdout to a file called "output file.txt" located in
        C:\\Users\Michael\PycharmProjects\ABLSim\.
        I don't really know how it works; I just copied some code off the Internet>
    """
    def __init__(self):
        self.terminal = sys.stdout
        self.log = open("C:\\Users\Michael\PycharmProjects\ABLSim\mcsim output.txt", "w")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        pass


class SimulationClock:
    """Class for the clock which times out the simulation, only 1 instance should exist

    Attributes are:
        _clock_value    number of ticks which have elapsed from the start of the simulation, nominally starts at zero
        _end_time       number of ticks over which the simulation should run
        _increment      the amount of real time, in seconds, which passes with each clock tick

        The value of _increment presents a trade-off between the time needed for a simulation to run and the
        resolution needed to run the simulation accurately. Too small a value will needlessly increase
        the time needed to run a simulation. Too large a value may cause unforeseen problems resulting
        from road users moving large distances at each clock tick. This issue needs to be characterized
        further. This interaction is important to the RoadUser.move function when it attempts to deal with a
        faster MV running into a slower MV traveling in the same direction. This will also impact the
        RoadUser.interacting_at_a_distance function.

    """

    def __init__(self, start_value=0, num_seconds=3600, inc=.1):
        """Initialization method for the Simulation Clock class

        start_value is the # of ticks the clock is set to at the start of the simulation, default is 0
        num_seconds is the # of seconds in real time the simulation should run, default is 1 hour
        inc is the amount of real time, in seconds, that passes for each clock tick, default = .1 sec

        """
        # should do a check on reasonableness of values here but am assuming they're good for now
        self._clock_value = start_value
        self._end_time = num_seconds * (1/inc)
        self._increment = inc

    def still_running(self):
        """Returns true if the simulation time has not yet elapsed else false"""
        if self._clock_value < self._end_time:
            return True
        else:
            return False

    def increment(self):
        """Increments simulation clock by 1 tick"""
        self._clock_value += 1

    def time_per_tick(self):
        """Returns the value of real time in seconds that elapses every clock tick"""
        return self._increment

    def value(self):
        """Returns the current value of the clock in ticks"""
        return self._clock_value

    def real_time(self):
        """Returns the current value of the clock in elapsed real time, in seconds"""
        return self._clock_value * self._increment

    def end_time(self):
        """Returns the end value of the clock, in seconds"""
        return self._end_time * self._increment

    def end_time_ticks(self):
        """Returns the end value of the clock, in ticks"""
        return self._end_time

    def set_time(self, time_in_seconds):
        """Sets the clock to the value passed in time_in_seconds after converting it to ticks, for testing only"""
        self._clock_value = time_in_seconds * (1/self._increment)


# END SimulationClock Class    *********************************************************************************


class Display:
    """Class which does something to display progress of simulation - elementary implementation so far.
        At each loop of the simulation, the Display class is invoked to update the display of the simulation.

    Attributes are:
    display_level:  a value of 0 indicates nothing is to be displayed
                    a value of 1 indicates that icons and interactions are to be displayed
                    a value of 2 indicates that time should slow whenever interactions exist

                    Display_level values include the behavior of lower display_level values, except 0.
    """
    # really need to clean up this mess of class vs instance variables
    width = 1280
    height = 720
    white = (255, 255, 255)
    black = (0, 0, 0)
    red = (255, 0, 0)
    green = (0, 255, 0)
    blue = (0, 0, 255)
    darkBlue = (0, 0, 128)
    pink = (255, 200, 200)

    def __init__(self, display_level):
        """ initialize all objects and variables involved with the display of the simulation
        """
        self._display_level = display_level

        if self._display_level != 0:
            self.sim_display = pygame.display.set_mode((Display.width, Display.height))
            self.background = pygame.image.load('abl-road.png').convert_alpha()

            # self.sim_display.fill(Display.white)
            pygame.init()
            pygame.display.set_caption('Simulation')
            clock = pygame.time.Clock()
            self.pixel_per_meters_wide = Display.width/road.length()
            self.mv_icon =   pygame.transform.scale(pygame.image.load('car.png'), (150, 68))
            # self.mv_icon = pygame.image.load('tinycar.jpg')
            self.bike_icon =   pygame.transform.scale(pygame.image.load('bike1.png'), (75, 40))
            # self.bike_icon = pygame.image.load('tinybike.jpg')
            self.ped_icon = [
                pygame.transform.scale(pygame.image.load('person1.png'), (60, 60)),
                pygame.transform.scale(pygame.image.load('person2.png'), (60, 60)),
                pygame.transform.scale(pygame.image.load('person3.png'), (60, 60)),
                pygame.transform.scale(pygame.image.load('person4.png'), (60, 60)),
            ]

    def update(self):
        """ This function updates the simulation display at every loop through the simulation
        """
        if self._display_level != 0:
            # blank the screen
            # self.sim_display.fill(Display.white)
            self.sim_display.blit(self.background, (0, 0)) 
            # paint the road
            Display.paint_road(self, road.length())

            #  paint the road users onto the road
            for ru in RoadUser.OnRoad:
                if ru._platooned:
                    Display.paint_icon(self, ru.type(), ru.direction(), ru.location())
                else:
                    Display.paint_icon(self, ru.type(), ru.direction(), ru.location())

            # paint the interactions onto the road users - wanted them to be slightly transparent
            if self._display_level > 1:
                for ai in Interaction.active:
                    Display.paint_interaction_box(self, ai.west_end(), ai.east_end())

            pygame.display.update()

            # wait a while if we're in a display mode which allows user to follow the interactions
            if len(Interaction.active) != 0 and self._display_level > 2:
                time.sleep(.3)

    def paint_interaction_box(self, west_end, east_end):
        """ This function displays a box showing the boundaries of the intersection for all intersections
            To hide attributes better, the interaction should provide the icon via a method
        """
        # draw a box whose east and west boundaries are those of the identified interaction, include ID at some point?
        # turn west and east boundaries into pixel measurements, boxes drawn top to bottom
        west = west_end * self.pixel_per_meters_wide
        east = east_end * self.pixel_per_meters_wide
        pygame.draw.rect(self.sim_display, Display.pink, (west, 0, east-west, Display.height), 0)

    def paint_icon(self, type, dirxn, locn):
        """ This function displays the appropriate icon for each road user
            To hide attributes better, the road user should provide the icon via a method
        """
        # get the appropriate icon
        if type == 'Motor Vehicle' and dirxn == 'WestBound':
            self.paint_icon_in_lane(self.mv_icon, 2, locn)
        elif type == 'Motor Vehicle' and dirxn == 'EastBound':
            # icon = MV
            self.paint_icon_in_lane(pygame.transform.flip(self.mv_icon, True, False), 3.4, locn)
        elif type == 'Bicycle' and dirxn == 'WestBound':
            # icon = bike
            self.paint_icon_in_lane(pygame.transform.flip(self.bike_icon, True, False), 1.15, locn)
        elif type == 'Bicycle' and dirxn == 'EastBound':
            # icon = bike
            self.paint_icon_in_lane(self.bike_icon, 4.5, locn)
        elif type == 'Pedestrian' and dirxn == 'WestBound':
            # icon = ped
            self.paint_icon_in_lane(self.ped_icon[int(time.time() * 2) % 4], 0.5, locn)
        elif type == 'Pedestrian' and dirxn == 'EastBound':
            # icon = ped
            self.paint_icon_in_lane(self.ped_icon[int(time.time() * 2) % 4], 5, locn)
        else:  # type/direction combo is unknown
            pass

    def paint_icon_in_lane(self, icon, lane_no, locn):
        """ This function paints one icon in the specified lane at the specified distance from west end
            lanes are identified as:
            0 - westbound ped lane
            1 - westbound bike lane
            2 - westbound car lane
            3 - eastbound car lane
            4 - eastbound bike lane
            5 - eastbound ped lane
        """
        # determine location of road user in number of pixels
        x_coord = locn * self.pixel_per_meters_wide
        y_coord = (lane_no * 100) + 55

        self.sim_display.blit(icon, (x_coord, y_coord))

    def paint_road(self, length):
        """ This function displays the blank road
            This will consist of 6 "lanes", 2 outside lanes for peds, 2 more lanes for bikes and 2 inner lanes for cars
        """
        # determine length of road in number of pixels
        len = length * self.pixel_per_meters_wide

        # pygame.draw.lines(self.sim_display, Display.black, 0, [(0,50),  (len,50)],  6)   # top outer line
        # pygame.draw.lines(self.sim_display, Display.black, 0, [(0,150), (len,150)], 3)   # top ped/bike line
        # pygame.draw.lines(self.sim_display, Display.black, 0, [(0,250), (len,250)], 3)   # top bike/car line
        # pygame.draw.lines(self.sim_display, Display.black, 0, [(0,350), (len,350)], 3)   # top car/car line
        # pygame.draw.lines(self.sim_display, Display.black, 0, [(0,450), (len,450)], 3)   # bttm car/bike line
        # pygame.draw.lines(self.sim_display, Display.black, 0, [(0,550), (len,550)], 3)   # bttm bike/ped line
        # pygame.draw.lines(self.sim_display, Display.black, 0, [(0,650), (len,650)], 6)   # bttm outer line

# END Display Class    ********************************************************************************************


class Road:
    """Class for the road that everybody is on, should only be 1 instance. Road modeled as a line - quite simple.
        This class primarily exists to let us know when road users are on or off the road. Assumption is that the
        west end of the road is represented by a value in meters which is less than the east end.

    Attributes are all in units of meters and are:
    _west_end   the leftmost end of the road, normally zero
    _east_end   the rightmost end of the road
    _length     the length of the road, equal to "_east_end - _west_end"

    """

    def __init__(self, we=0, ee=1000):
        """Create and initialize the road with a west end, an east end and a calculated length

            we is the count representing the west end of the road
            ee is the length of the road in meters and the count representing the west end of the road
            """
        # should check for reasonableness of west end and east end, nonnegative # ,etc assume good for now
        self._west_end = we
        self._east_end = ee
        self._length = self._east_end - self._west_end
        # print('road starts at', self._west_end, ', road ends at', self._east_end, ', and is', self._length, 'm long')

    def west_end(self):
        """Return the value for the west end of the road, in meters"""
        return self._west_end

    def length(self):
        """Return the value for the length of the road, in meters"""
        return self._length

    def east_end(self):
        """Return the value for the east end of the road, in meters"""
        return self._east_end

# END Road Class    ********************************************************************************************


class RoadUser:
    """Class for all types of road users that move along the road

        Road Users’ physical dimensions are modeled as lines (length but no width)
        where the length represents their physical dimensions or their sphere of influence.
        A road user's location is referenced to their rearmost physical point,
        ie the point furthest away from their direction of travel. The length is used to determine
        their frontmost physical point, e.g. when deciding if an interaction is occurring between road users.

        I have yet to create platoons of RoadUser. If implemented, this will likely be its own class.

        The RoadUser class is closely linked to the Interaction class which defines what it means for
        road users to interact.
        The partitioning in this area is not good but I have not attempted to simplify it yet because what
        it means to be interacting is not completely defined yet.

       Attributes are:
        ID: 0 - 250,000 int, unique to each road user instance
        Type: Motor Vehicle, Bicycle, Pedestrian
        CreateLocation: 0 - 50,000 m float location where road user is created
        Location: 0 - 50,000 m float
        Length: 0.1 - 100 m float
        Speed: 1 - 60 m/s float
        TravelDirection: EastBound, WestBound (EastBound is headed to the right & WestBound to the left)
        Step: meters traveled by the road user in one clock tick float, will be negative for WestBound RoadUsers
        EastEnd: location of the easternmost end of the road user, same type as Location
        WestEnd: location of the westernmost end of the road user, same type as Location
        Front: for a westbound RU, this is the WestEnd. for an eastbound RU, it is the EastEnd, same type as Location
        Rear:  for a westbound RU, this is the EastEnd. for an eastbound RU, it is the WestEnd, same type as Location
        Platooned: a flag which is true if the road user has ever been a leader or a member of a platoon, else false
        LeftOnRoad: a flag which is true if the road user is still on the road when the simulation ends, else false
        Create_Time: the time, in real seconds, that the road user was created (and placed on road)
        End_Time: the time, in real seconds, that the road user left the road

"""
    # start ID for road user objects at 0
    id = 0

    # this variable gets set to the parameter value passed in args.iaxntime in the initialization code
    ext_iaxn_time = 12

    # create variables which are running totals for the types of road users created during the simulation
    WB_peds = 0
    WB_cycs = 0
    WB_mvs  = 0
    EB_peds = 0
    EB_cycs = 0
    EB_mvs  = 0

    # clear the lists which store road user object IDs which are either on or off the road
    # road users start on the road and go off the road when they have moved past the end of the road
    OnRoad = []
    OffRoad = []

    def __init__(self, typ='Motor Vehicle', location=0, length=6.0, speed=11.176, dirxn='EastBound', step=.7):
        """Initialization method which creates an instance of a road user
        """
        # should do a check on reasonableness of values here but am assuming they're good for now
        # would like to have EastBound and WestBound be 1 & 0, need to use a literal
        self._ID = RoadUser.id
        RoadUser.id += 1
        self._type = typ
        self._createlocation = location
        self._location = location
        self._length = length
        self._direction = dirxn
        self._platooned = False
        self._leftonroad = False
        self._create_time = clk.real_time()
        self._offroad_time = 0

        if self._direction == 'EastBound':
            self._speed = speed
            self._step = step
            self._east_end = self._location + self._length
            self._west_end = self._location
            self._front = self._east_end
            self._rear = self._west_end
        else:  # road user is WestBound
            self._speed = -speed
            self._step = -step
            self._east_end = self._location
            self._west_end = self._location - self._length
            self._front = self._west_end
            self._rear = self._east_end

        # add the new road user to the OnRoad set
        RoadUser.OnRoad.append(self)
        # print('New RU', self)

        # update running totals of road users created
        # this is where we would attach the appropriate icon to the road user
        if self._direction == 'WestBound':
            if self._type == 'Pedestrian':
                RoadUser.WB_peds += 1
            elif self._type == 'Bicycle':
                RoadUser.WB_cycs += 1
            elif self._type == 'Motor Vehicle':
                RoadUser.WB_mvs += 1
        else:
            if self._type == 'Pedestrian':
                RoadUser.EB_peds += 1
            elif self._type == 'Bicycle':
                RoadUser.EB_cycs += 1
            elif self._type == 'Motor Vehicle':
                RoadUser.EB_mvs += 1

    def __repr__(self):
        """This function returns a string representation of a RoadUser object
        """
        if self in RoadUser.OnRoad:
            road_status = 'on road'
        else:
            road_status = 'off road'

        if self._platooned:
            platoon_status = ' Platoon: Yes.'
        else:
            platoon_status = ' Platoon:  No.'

        if self._leftonroad:
            lor_status = ' Left On Road: Yes.'
        else:
            lor_status = ' Left On Road:  No.'

        type = 'Motor Vehicle'
        if self._type == 'Bicycle':
            type = 'Bicycle      '
        elif self._type == 'Pedestrian':
            type = 'Pedestrian   '

        road_user_string = '<' + \
                'Road User ID ' + '{:6d}'.format(self._ID) + ': ' + self._direction + ' ' + type + \
                ' created at ' + '{:09.3f}'.format(self._createlocation) + ' m, located ' + road_status + \
                ' at ' + '{:09.3f}'.format(self._location) + ' m, going ' + '{:06.2f}'.format(self._speed) + \
                ' m/s, moving ' + '{:05.2f}'.format(self._step) + ' m/tick.' + \
                ' Length: ' + '{:05.2f}'.format(self._length) + ' m,' + \
                ' WE: ' + '{:09.3f}'.format(self._west_end) + ' EE: ' + '{:09.3f}'.format(self._east_end) + '.' + \
                platoon_status + lor_status + \
                ' Created at ' + '{:010.2f}'.format(self._create_time) + ' secs and taken off the road at ' + \
                '{:010.2f}'.format(self._offroad_time) + ' secs.' + \
                '>'
        return road_user_string

    @staticmethod
    def advance_RoadUsers_along_the_road():
        """This method advances all road users along the road an appropriate distance for one clock tick
        """
        # I don't think the "0:" is needed here
        # this method of updating all of the RoadUser's positions in a list ensures that all MVs are updated
        # from the oldest to the youngest, i.e. any MV being moved has already had the MV in front of it moved
        # This is important for dealing with faster cars behind slower cars.
        for ru in RoadUser.OnRoad[0:]:
            RoadUser.move(ru)

    def move(self):
        """This method moves a single road user the correct distance for one clock tick.
            It updates the road user's physical location and physical limits.
            If the road user goes off the end of the road, it is moved to off-road status.

            If a Motor Vehicle attempts to get too close to the Motor Vehicle in front of it, it is
            kept to a specified following distance which can result in an MV traveling more slowly than
            the speed assigned to it. That MV would instead travel at the speed assigned to the MV ahead of it.
            This prevents a faster MV from over-running or "passing" a slower MV.
        """
        # This code prevents an MV from getting too close to the MV in front of it
        # This function assumes that the MV in front of the MV being moved has already been moved for the clock tick.
        # use Pipes (constant headway distance) or Forbes (constant headway time) model to estimate following distance
        # following distance between 2 cars is given by the equation d=a + bv where a is vehicle length in meters,
        # b is reaction time in seconds and v is speed in meters per second. For this code a is absolute value of
        # _front - _rear, b is chosen to be 1.5 second, and v is self._speed.
        # The long if expression enforces the follow distance requirement only when all 3 conditions are true:
        # 1. both road users are MVs,
        # 2. there is an MV in front of the MV being moved that is traveling in the same direction, and
        # 3. the MV being moved would violate its follow distance to the MV in front of it after it had been moved.

        # this formula for follow_distance is closely related to the code used for minimum gap in
        # RoadUserSource.add_new_road_users fcn (Forbes model for gap between successive cars).
        # follow_distance is the min gap between the front of the trailing vehicle and the rear of the leading vehicle,
        # assuming a 1.5 second reaction time according to the Forbes model.
        # until it is abstracted out to eliminate the duplicated code, these 2 locations need to stay in sync
        follow_distance = 1.5*abs(self._speed)

        front_MV = RoadUser.get_MV_ahead_of_me(self)

        if self._type == 'Motor Vehicle' and front_MV and \
            ((self._direction == 'EastBound' and self._front + self._step > front_MV._rear - follow_distance) or
            (self._direction == 'WestBound' and self._front + self._step < front_MV._rear + follow_distance)):
            # move car back because it is too close but not so far that it is pushed off the road
            if self._direction == 'EastBound':
                    self._location = max((front_MV._rear - follow_distance - self._length), Road.west_end(road))
            else:
                self._location = min((front_MV._rear + follow_distance + self._length), Road.east_end(road))
                # mark the cars as having been platooned
            front_MV._platooned = True
            self._platooned = True
        else:                               # move road user without worrying about one MV running over another
            self._location = self._location + self._step

        # we've finished moving the road user so update its reference points
        if self._direction == 'WestBound':
            self._west_end = self._location - self._length
            self._east_end = self._location
            self._front = self._west_end
            self._rear = self._east_end
        else:  # RU is EastBound
            self._west_end = self._location
            self._east_end = self._location + self._length
            self._front = self._east_end
            self._rear = self._west_end
        # print('move', self._direction, self._type, ' to ', self._location,
        #       'WE:', self._west_end, 'EE:', self._east_end)

        # move road user to OffRoad if it has exited the road segment
        if self.user_has_left():
            self.transfer_road_user_to_off_road(clk.real_time())

    def get_MV_ahead_of_me(self):
        """This function returns the nearest MV in front of the parameter road user, if one exists.
           The returned value will be:
           None: if no MV exists between the road user passed to this function and the end of the road or
           MV: the nearest onroad MV moving in the same direction and ahead of parameter road user
        """
    #   Run through the OnRoad list toward the older road users (descending order) starting just
    #   below index of passed parameter and find the first MV traveling in the same direction.
        self_index = RoadUser.OnRoad.index(self)
        if self_index > 0:                          # make sure we have some road users in front of us
            for i in range(self_index-1, -1, -1):
                ru = RoadUser.OnRoad[i]
                if ru._type == 'Motor Vehicle' and ru._direction == self._direction:
                    return ru                       # not sure if this returns the right data structure
        return None

    def transfer_road_user_to_off_road(self, offroad_time):
        """This function appends the road user to the OffRoad list and removes it from the OnRoad list
        """
        self._offroad_time = offroad_time
        RoadUser.OffRoad.append(self)
        RoadUser.OnRoad.remove(self)

    def user_has_left(self):
        """Return True if the road user's location is off the road, ie west of the westmost point or
            east of the eastmost point else return False to indicate user is still on the road
        """
        # this logic considers road users to be on the road when their location is on the ends of the road
        # they have to completely move off the road before they are considered off the road
        if self._location < road.west_end() or self._location > road.east_end():
            return True
        else:
            return False

    def road_users_equal(self, ru2):
        """Return True if the 2 road users are the same, else False
        """
        if self._ID == ru2._ID:
            return True
        else:
            return False

    @staticmethod
    def output_all_created_road_users():
        """This function outputs information on all road users created during this simulation to stdout
        """
        print()
        print('Road Users Log')
        # write out a table of summary information on road users
        EB_totals = RoadUser.EB_mvs + RoadUser.EB_cycs + RoadUser.EB_peds
        WB_totals = RoadUser.WB_mvs + RoadUser.WB_cycs + RoadUser.WB_peds
        MV_totals = RoadUser.EB_mvs + RoadUser.WB_mvs
        Cyc_totals = RoadUser.EB_cycs + RoadUser.WB_cycs
        Ped_totals = RoadUser.EB_peds + RoadUser.WB_peds
        if (EB_totals+WB_totals) == (MV_totals+Cyc_totals+Ped_totals):
            Totals = str(EB_totals+WB_totals)
        else:
            Totals = 'Dont Add Up'
        print('               Motor                                                           ')
        print('             Vehicles           Bicycles           Pedestrians           Totals')
        print('EastBound      ', RoadUser.EB_mvs, '               ', RoadUser.EB_cycs, '                 ', RoadUser.EB_peds, '                 ', EB_totals)
        print('WestBound      ', RoadUser.WB_mvs, '               ', RoadUser.WB_cycs, '                 ', RoadUser.WB_peds, '                 ', WB_totals)
        print('Totals         ', MV_totals,        '              ', Cyc_totals,       '                 ', Ped_totals,        '                ', Totals)
        print()

        # move all of the road users still on the road into the off road list and sort by road user ID
        # be sure to mark the road user as one that was still on the road when the simulation ended
        while len(RoadUser.OnRoad) != 0:
            for ru in RoadUser.OnRoad:
                ru._leftonroad = True
                RoadUser.transfer_road_user_to_off_road(ru, clk.real_time())
        RoadUser.OffRoad.sort(key=attrgetter('_ID'))

        # write out all of the road users in the Off Road list
        for ru in RoadUser.OffRoad:
            print(ru)

    def oncoming_MVs(self, ru2):
        """Return True if the 2 road users are oncoming motor vehicles which haven't passed each other, else False
        """
        if self._type == 'Motor Vehicle' and ru2._type == 'Motor Vehicle':      # test for 2 motor vehicles
            if self._direction != ru2._direction:                               # test for opposite directions
                if self._direction == 'WestBound':                              # test for haven't passed each other yet
                    if self._front > ru2._front:
                        # print('2 oncoming MVs found. They are', self._ID, '&', ru2._ID, 'at', self._location, '&', ru2._location)
                        return True
                else:
                    if self._front < ru2._front:
                        # print('2 oncoming MVs found. They are', self._ID, '&', ru2._ID, 'at', self._location, '&', ru2._location)
                        return True
        return False

    def two_mvs_interacting_at_a_distance(self, ru2):
        """Return True if the 2 road users are both motor vehicles of opposing direction and close enough to each
            other to be interacting at a distance, else False. This consists of two cars approaching each other
            before passing, being physically alongside each other during a pass, or following a passing maneuver when they are
            returning to the center lane. The 2 MVs must be closer to each other than the
            extended interaction time which is translated to a distance by multiplying by the MV's speed.
            It is possible for 2 MVs to interact at a distance while a third MV is in between. The intervening MV
            will also be interacting with the oncoming MV.
        """
        # In order for two road users to have a chance at being classified as 2 MVs interacting at a distance:
        # 1. The extended interaction time parameter must be nonzero
        # 2. The 2 road users must be Motor Vehicles. Only MVs can interact at a distance
        # 3. The 2 MVs must be traveling in opposite directions
        if RoadUser.ext_iaxn_time == 0:
            return False
        if (self._type != 'Motor Vehicle') or (ru2._type != 'Motor Vehicle'):
            return False
        if self._direction == ru2._direction:
            return False

        # use the average speed of the 2 MVs to calculate the extended interaction length
        ext_iaxn_length = RoadUser.ext_iaxn_time * ((abs(self._speed) + abs(ru2._speed))/2)

        # determine if one car is within the extended interaction range of the other
        # it doesn't matter which car is used to create the extended interaction range
        west_end = self._front - ext_iaxn_length
        east_end = self._front + ext_iaxn_length
        if RoadUser.ru_within_range(ru2, west_end, east_end):
            return True
        else:
            return False

    def ru_within_range(self, west_side_of_range, east_side_of_range):
        """This function is used to determine if a road user falls within the envelope of an extended interaction
            between two MVs. It returns True if any portion of the road user lies within the limits of the range
            passed to it, else False.
            A road user which is straddling either, or both, bound(s) of the range returns True.
            A range where the values of west and east side are equal, returns True only if the road user is
            straddling the coincident bounds of the passed range.
        """
        if (self._east_end < west_side_of_range) or (self._west_end > east_side_of_range):
            return False
        else:
            return True

    def create_shorthand(parties):
        """ This fcn returns a textual shorthand for the parties involved with an interaction, which is passed to it.
            The shorthand consists of a 6 position code which lists the road users involved in an interaction.
            The leftmost position is position 0 and the rightmost is position 5.
            Position 0 represents a WestBound Pedestrian and contains a 'P' if present.
            Position 1 represents a WestBound Bicycle and contains a 'B' if present
            Position 2 represents a WestBound Motor Vehicle and contains an 'M' if present
            Position 3 represents a EastBound Motor Vehicle and contains an 'M' if present
            Position 4 represents a EastBound Bicycle and contains a 'B' if present
            Position 5 represents a EastBound Pedestrian and contains a 'P' if present
            No convention is afforded to indicate multiple instances of the same type/direction of road users,
            e.g. there is no way to tell if 'B' in position 1 indicates one WB bike or more than one. Consider
            using lowercase letters to indicate singular instance and capital letters for 2 or more instances.
        """
        shorthand = '      '

        for ru in parties:                                                                            # position #
            if   RoadUser.direction(ru) == 'WestBound' and RoadUser.type(ru) == 'Pedestrian':              # 0
                shorthand = 'P' + shorthand[1:]
            elif RoadUser.direction(ru) == 'WestBound' and RoadUser.type(ru) == 'Bicycle':                 # 1
                shorthand = shorthand[0] + 'B' + shorthand[2:]
            elif RoadUser.direction(ru) == 'WestBound' and RoadUser.type(ru) == 'Motor Vehicle':           # 2
                shorthand = shorthand[0:2] + 'M' + shorthand[3:]
            elif RoadUser.direction(ru) == 'EastBound' and RoadUser.type(ru) == 'Motor Vehicle':           # 3
                shorthand = shorthand[0:3] + 'M' + shorthand[4:]
            elif RoadUser.direction(ru) == 'EastBound' and RoadUser.type(ru) == 'Bicycle':                 # 4
                shorthand = shorthand[0:4] + 'B' + shorthand[5:]
            elif RoadUser.direction(ru) == 'EastBound' and RoadUser.type(ru) == 'Pedestrian':              # 5
                shorthand = shorthand[0:5] + 'P'
            else:       # unknown direction/type of road user
                print('Error in creating shorthand code for Interaction 27356873')
        # print('shorthand for', [ru.direction() + ' ' + ru.type() for ru in parties], 'is', shorthand)
        return shorthand

    def direction(self):
        """Return the direction in which the road user is traveling
        """
        return self._direction

    def west_end(self):
        """Return the west end of the road user
        """
        return self._west_end

    def east_end(self):
        """Return the east end of the road user
        """
        return self._east_end

    def type(self):
        """Return the type of the road user
        """
        return self._type

    def location(self):
        """Return the location of the road user
        """
        return self._location

    def ID(self):
        """Return the ID of the road user
        """
        return self._ID

    def set_extended_interaction_time(seconds):
        """Set the value of the lane change time for motor vehicles, in seconds
        """
        RoadUser.ext_iaxn_time = seconds


# END RoadUser Class    ********************************************************************************************


class RoadUserSource:
    """This class generates road users at points along the Road. The objects of this class are normally
        located at each end of the road but the idea was to allow them to exist anywhere along the road in order
        to simulate intersections where road users can enter the road. Not yet implemented is RoadUserSink
        which would sink road users leaving the road, either at an intersection or the end of the road. At this
        point, the model assumes road users leave the road only when they reach the end of the road.
        Creating a RoadUserSink class or its equivalent to fully implement the ability to model intersections
        would necessitate adding attributes to the road user showing origin and destination and likely
        other changes which are unnecessary until the need for modeling of intersections exists.

        This class will need to be modified in order to produce a distribution of speeds for each road user type.
        This class will need to be modified in order to allow selection of different types of distribution models
        of the headway of road users.

      Attributes:
      type:           type of the road user, eg Motor Vehicle, Bicycle, Pedestrian
      per_hour:       number of road users of this type which are added per hour
      birthplace:     the spot on the road where new road users are added
      direction:      the travel direction of the road user
      nominal_speed:  the nominal speed of the road user
      speed_distr:    selector for speed determination: 0 = always set speed to nominal speed
                        1 = set speed to value drawn from a normal distribution where 85th %ile is nominal_speed
      length:         the physical length of the road user
      minimum_gap:    the minimum time which must exist between the last and the next road user added to the road
      time_of_last:   time of the last road user which was added to the road
      time_of_next:   time of the next road user to be added to the road
      arrival_distribution: flag for road user spacing set to 1 for neg exponential distribution, 0 for equal intervals
    """

    # this list is a container which allows iteration over all instances of the RoadUserSource class
    list_of_road_user_sources = []

    def __init__(self, type, ru_per_hr, birth_locn, dirxn, speed, distr, len, mingap, arrival_spacing):

        """Creates new instance of RoadUserSource and adds it to the list of road user sources
        """
        self.type = type
        self.per_hour = ru_per_hr
        self.birthplace = birth_locn
        self.direction = dirxn
        self.nominal_speed = speed
        self.speed_distr = distr
        self.length = len
        self.minimum_gap = mingap
        self.time_of_last = clk.real_time()
        self.arrival_distribution = arrival_spacing
        if self.arrival_distribution:
            self.time_of_next = self.time_of_last + self.minimum_gap + self.neg_exp(self.per_hour)
        else:
            self.time_of_next = self.time_of_last + 1/self.per_hour * 3600
        # self.headway_distr = pointer to headway distribution, currently hardcoded to negative exponential
        # self.speed_distr = pointer to speed distribution - not implemented
        # add new instance to the list of instances
        RoadUserSource.list_of_road_user_sources.append(self)

    def __repr__(self):
        """This function returns a string representation of a RoadUserSource object
        """
        type = 'Motor Vehicle'
        if self.type == 'Bicycle':
            type = 'Bicycle      '
        elif self.type == 'Pedestrian':
            type = 'Pedestrian   '
        if self.arrival_distribution:
            spacing = 'neg exponential distribution.'
        else:
            spacing = 'constant interval of ' + str(1/self.per_hour*3600) + ' seconds.'

        string = '<' + \
                    self.direction + ' ' + type + ' source at ' + '{:07.1f}'.format(self.birthplace) + \
                    ' generating ' + '{:06.1f}'.format(self.per_hour) + ' road users/hour using a ' + spacing + \
                    ' Speed = ' + '{:06.3f}'.format(self.nominal_speed) + ' m/s,' + \
                    ' Speed Distr = ' + '{:01.0f}'.format(self.speed_distr) + ' (0=fixed, 1=normal distribution),' + \
                    ' Length = ' + '{:04.1f}'.format(self.length) + ' m,' + \
                    ' Minimum gap between consecutive road users = ' + '{:06.1f}'.format(self.minimum_gap) + ' seconds.' + \
                    '>'
        return string

    def add_new_road_users(self):
        """This function takes a RoadUserSource instance and adds a new road user to the road if it is time to do so
              This fcn returns the road user which was added or None if no road user was added
        """
        if clk.real_time() >= self.time_of_next:
            # this code generates a new road user.
            # a new road user can either be given a fixed speed or a random speed pulled
            # from a normal distribution with the nominal speed at the 85th percentile and the 15th
            # percentile being the nominal speed less 2.222 m/s (8 kph/4.98 MPH) (mean = nominal speed - 1.11 m/s,
            # std deviation = 1.11).
            # Justification for the normal distribution is found in "Estimating Free-flow Speed from Posted Speed
            # Limit Signs", Matthew Deardoff, Brady Wiesner, Joseph Fazio, Procedia-Social and Behavioral Sciences
            # Volume 16, 2011, Pages 306-316. Choice of 8 kph for 15th-85th percentile spread is guess; but 15-85
            # split makes for 70% of the range which is a close approximation to 68% which is +/- 1 SD.
            # SD = 1.1 m/s for motor vehicles but I just picked one value that would work OK for vehicles, bikes, and
            # peds - that guess came out to 1.5 m/s. If we want values for each type, I thought the following values
            # would be good: MV - 1.11; Bike - 2; Ped - 1.23
            if self.speed_distr == 0:                       # fixed speed
              instance_speed = self.nominal_speed
            elif self.speed_distr == 1:                     # use a variable speed pulled from a distribution
                if self.type == 'Motor Vehicle':
                    sigma = 1.11
                    lower_bound = 4.47                     # lower bound for speed = 10 MPH
                elif self.type == 'Bicycle':
                    sigma = 2
                    lower_bound = 1.788                     # lower bound for speed = 4 MPH
                elif self.type == 'Pedestrian':
                    sigma = 1.23
                    lower_bound = 0.447                     # lower bound for speed = 1 MPH
                else:
                    print("problem with type of road user in add_new_road_users")

                # this code gets a randomly generated speed assuming nominal speed is the 85th percentile speed.
                # the generated speed must be equal to or above the lower bound set for each road user type
                # sigma is subtracted from the nominal speed to get a value close to the mean for a normal distribution
                instance_speed = -1
                while instance_speed < lower_bound:
                    mu = self.nominal_speed - sigma             # calculate mean using symmetry of 85 and 15 %ile
                    instance_speed = random.gauss(mu, sigma)
                # print("Speed for the", self.direction, self.type, "is", instance_speed, "m/s, lower bound is", lower_bound)
            else:
                print("problem with speed distribution value in add_new_road_users, value incorrect")

            # For MVs only, convert speed to an appropriate headway (in seconds) to the next MV.
            # headway is the distance from the front of a trailing vehicle to the front of a leading vehicle.
            # in this case we're using it as the distance from the rear of the trailing vehicle to the rear of
            # the leading vehicle because the reference point we use is the rear of the vehicle.
            # I use the Forbes model assuming a 1.5 second reaction time.
            # this formula is closely related to follow_distance in RoadUser.move fcn - until it is
            # abstracted out to eliminate the duplicated code, these 2 locations need to stay in sync
            if self.type == 'Motor Vehicle':
                min_headway = (self.length + (1.5 * instance_speed))/instance_speed
            else:
                min_headway = 0

            # set time for next road user to be generated - use neg exponential distribution or equal intervals
            self.time_of_last = clk.real_time()
            if self.arrival_distribution:
                self.time_of_next = self.time_of_last + max(self.neg_exp(self.per_hour), min_headway)
            else:
                self.time_of_next = self.time_of_last + 1/self.per_hour * 3600

            return RoadUser(self.type, self.birthplace, self.length, instance_speed, self.direction,
                            instance_speed*clk.time_per_tick())
        else:
            return None

    def neg_exp(self, items_per_hour):
        """ This function determines the headway for the next road user from a given source by
              calculating the time between road users. This is a negative
              exponential distribution implementing the formula t=-mu * ln(Z) where t is the calculated time,
              mu is the mean headway, and Z is a random number equal to or greater than 0 and less than 1.
              This function returns the time to the next road user in seconds.

              Inputs to this function include
              the non-negative number of new road users per hour generated by the RoadUserSource instance
        """
        if items_per_hour != 0:
            mu = 3600/items_per_hour            # convert rate of road users per hour into a mean headway in seconds
            neg_exp_result = -mu * math.log(random.random())
        else:
            neg_exp_result = 9999999999
        return neg_exp_result

# END RoadUserSource Class    *************************************************************************************


class Interaction:
    """ Interaction class

    An interaction is an object which records the interaction of road users on the road.

    Three sets of interactions are defined.
    The first is Current Interactions which is the set of all interactions identified during the current clock tick;
    this set is only valid within one clock tick.
    The second set is Active Interactions. It contains all interactions which are ongoing for as long as they exist.
    The third set is Recorded Interactions. This is the set of all completed interactions (ongoing interactions
    which have ended). The set of Recorded Interactions is the primary output of this tool.
    When interactions are first identified, they show up in the Current set. As long as they continue to exist,
    they are present in the Active set and continue to appear in each Current set.
    Once they finish, ie do not appear in the Current set, they are moved from the Active set to the Recorded set.

    Attributes
        InteractionID: Unique ID
        Critical Road Users: the 2 MVs which define a critical interaction
        Parties: list of Road Users which are interacting with each other
        StartTime: Value of Clock when interaction is first detected
        EndTime: Value of Clock when interaction is marked as Complete
        StartLocation: Physical location of westmost point of westmost vehicle in interaction when it is first detected
        EndLocation: Physical location of eastmost point of eastmost vehicle in interaction when it is first detected
         an interaction's location is defined to be the westmost point of the westmost road user
        Extended: True if this interaction includes 2 MVs interacting at a distance, else False
        Critical: True if this interaction was established with 2 MVs of opposing direction, else False
        Shorthand: textual representation of the parties involved in the interaction
    """

    iid = 0
    recorded_id = 0
    num_unaggregated_iactions = 0
    num_recorded_iactions = 0
    # these 3 lists act as sets through which an interaction travels during its lifecycle
    current = []
    active = []
    recorded = []


    def __init__(self, critical_road_users, road_users, start_time, end_time, extended, critical):
        """Initialization method which creates an interaction
        """
        self._ID = Interaction.iid
        Interaction.iid += 1
        self._critical_road_users = critical_road_users
        self._parties = road_users
        self._start_time = start_time
        self._end_time = end_time
        self._start_location = self.west_end()
        self._end_location = self.east_end()
        self._extended = extended
        self._critical = critical
        self._shorthand = RoadUser.create_shorthand(self._parties)
        Interaction.num_unaggregated_iactions += 1

    def __repr__(self):
        """This function returns a string representation of an Interaction object
        """
        ext = 'False'
        if self._extended:
            ext = 'True '
        crit = 'False'
        if self._critical:
            crit = 'True '

        interaction_string = '<' + \
                'Interaction ID ' + '{:7d}'.format(self._ID) + ': ' + 'Code: ' + self._shorthand + '.' + \
                ' Start Time: ' + '{:08.1f}'.format(self._start_time) + ' secs,' + \
                ' End Time: ' + '{:08.1f}'.format(self._end_time) + ' secs.' + \
                ' Start Location: ' + '{:07.1f}'.format(self._start_location) + ' m,' + \
                ' End Location: ' + '{:07.1f}'.format(self._end_location) + ' m.' + \
                ' Extended= ' + ext + '.'\
                ' Critical= ' + crit + '.'\
                ' Critical Road Users= ' + str(self._critical_road_users) + '.' + \
                ' Road Users ' + str(self._parties) + '.' + \
                '>'

# this code is used for debug and replaces all of the road user details with just their ID #s
#         ru_ids = ''
#         for ru in self._parties:
#             ru_ids = ru_ids + str(RoadUser.ID(ru)) + ', '
#         interaction_string = '<' + \
#                 'Interaction ID ' + '{:7d}'.format(self._ID) + ': ' + 'Code: ' + self._shorthand + '.' + \
#                 ' Start Time: ' + '{:06.1f}'.format(self._start_time) + ' secs,' + \
#                 ' End Time: ' + '{:06.1f}'.format(self._end_time) + ' secs.' + \
#                 ' Start Location: ' + '{:07.1f}'.format(self._start_location) + ' m,' + \
#                 ' End Location: ' + '{:07.1f}'.format(self._end_location) + ' m.' + \
#                 ' Extended= ' + ext + '.'\
#                 ' Critical= ' + crit + '.'\
#                 ' Critical Road Users= ' + str(self._critical_road_users) + '.' + \
#                 ' Road Users ' + ru_ids + '.' + \
#                 '>'
        return interaction_string

    def exists(self, ru2):
        """ This function returns:
            0 if the 2 road users are not interacting,
            1 if the 2 road users are interacting by being physically alongside each other,
            2 if the 2 road users are oncoming MVs interacting at a distance.
            This function contains the definition of what it means for 2 road users to interact.
            A road user may not interact with itself.
            Interactions are defined to exist in the following cases:
            Case #1 If 2 road users are physically alongside each other, they are interacting.
            Case #2 If 2 oncoming motor vehicles are close enough that either driver may alter course
            in response to the other motor vehicle, they are interacting. If a road user is between 2 of these MVs,
            they are said to be interacting with those 2 motor vehicles.
            We define an area between two oncoming motor vehicles in which they are defined to be interacting
            without being physically alongside each other because motorists may choose to alter course or speed
            in response to the oncoming motor vehicle.
            Bicycles and peds are said to be interacting with the 2 oncoming vehicles if they are physically
            alongside this extended interaction area.
            Two motor vehicles traveling in the same direction are unable to interact with each
            other because passing is not allowed.
            This definition does allow for 2 motor vehicles close to one another and traveling in the same direction
            to both interact with an oncoming vehicle which reflects operational reality.
        """
        # a road user cannot interact with itself
        if RoadUser.road_users_equal(self, ru2):
            return 0

        # Two cases need to be evaluated to see if an interaction exists btwn the 2 road users:
        # 1. two road users are physically alongside each other
        # 2. two oncoming motor vehicles interact via the decision sight distance-derived area.

        # Case #2
        # if 2 vehicles of opposite direction are close enough to conduct a passing maneuver or are recovering
        # from a passing maneuver, then they are interacting at a distance.
        # Case 2 is tested first so that 2 MVs which were interacting at a distance at an earlier time
        # and which have come alongside each other now are not classified as Case #1.
        if RoadUser.two_mvs_interacting_at_a_distance(self, ru2):
            return 2

        # Case #1
        # Is any part of these 2 road users overlapping, i.e. are they alongside each other?
        if not((ru2.west_end() > self.east_end()) or (ru2.east_end() < self.west_end())):
            return 1

        return 0

    def share_road_users(self, i2):
        """ This function tests whether two multi-party interactions share any road users at all.
            if the interactions share one or more road users, return True else False
        """
        for ru1 in self._parties:
            for ru2 in i2._parties:
                if RoadUser.road_users_equal(ru1, ru2):
                    return True
        return False

    @staticmethod
    def identify_current_interactions():
        """ This function creates a set of unique current interactions which exist at the current clock tick.
        """
        # clear the set of current interactions for this new tick
        Interaction.current.clear()

        # this loop identifies all current interactions in which only 2 parties interact with each other
        for ru1, ru2 in combinations(RoadUser.OnRoad, 2):
            interaction_type = Interaction.exists(ru1, ru2)
            if interaction_type != 0:
                if (RoadUser.type(ru1) == 'Motor Vehicle' and RoadUser.type(ru2) == 'Motor Vehicle') and \
                   (RoadUser.direction(ru1) != RoadUser.direction(ru2)):
                    crit = True
                else:
                    crit = False
                if interaction_type == 1:
                    ext = False
                elif interaction_type == 2:
                    ext = True
                Interaction.current.append(Interaction([RoadUser.ID(ru1), RoadUser.ID(ru2)], [ru1, ru2], clk.real_time(), -1, ext, crit))

        # this loop adds road users to the interactions which consist of 2 oncoming MVs interacting at a distance.
        # any road user alongside this type of interaction must be added to the parties of that interaction.
        # remove duplicate road users from the list of involved parties
        for ci in Interaction.current:
            if ci._extended:
                for ru in RoadUser.OnRoad:
                    if RoadUser.ru_within_range(ru, ci._start_location, ci._end_location):
                        ci._parties.append(ru)
            ci._parties = list(set(ci._parties))
            ci._shorthand = RoadUser.create_shorthand(ci._parties)      # update shorthand code to include new additions

# debug code to monitor the progress of current interactions
#         if len(Interaction.current) != 0:
#             print()
#             print('Current Interaction Set:')
#             for ci in Interaction.current:
#                 print(ci)

        # at this point, all of the current interactions which have been created, with the exception of the
        # extended interactions, contain only 2 parties.
        # now we need to combine all of the 2-party interactions which share road users to create the current
        # interactions that have more than two involved parties.
        Interaction.aggregate_current_interactions()

# debug code to monitor the progress of current interactions
#         if len(Interaction.current) != 0:
#             print('Aggregated Current Interaction Set:')
#             for ci in Interaction.current:
#                 print(ci)

    def equal(self, i2):
        """ This function tests whether two interactions are the same by comparing the parties involved in each.
            The comparison process differs depending on whether the two interactions are critical or not.
            If both interactions are critical, then they are equal if the two opposing MVs which established the
            interaction are equal.
            If one or both interactions are not critical, then they are equal if all of the involved parties
            are the same.
            This function is used when comparing current interactions to Active interactions.
        """
        if self._critical and i2._critical:
            if set(self._critical_road_users) == set(i2._critical_road_users):
                return True
            else:
                return False
        if set(self._parties) == set(i2._parties):
            return True
        return False

    @staticmethod
    def update_interactions():
        """ UpdateInteractions moves interactions through their lifecycle,
        i.e. from Current (the set of interactions discovered during the current clock tick) to
        Active (the set of interactions which are ongoing) to Recorded (the set of interactions which have completed
        and the final log of all interactions which occurred during the simulation).
        Two transitions are effected by this function. It moves interactions from the set of CurrentInteractions
        to the set of ActiveInteractions and it moves interactions from the set of ActiveInteractions
        to the set of RecordedInteractions.
        The transition from Current to Active occurs when an interaction exists in the Current set
        but not yet in the Active set; this occurs when an interaction first arises.
        The transition from Active to Recorded occurs when an interaction exists in the Active set
        but not in the Current set; this occurs when an interaction ends.
        """
        # this code runs through the set of active interactions and does one of three things:
        # 1. if a corresponding interaction exists in current, this ongoing interaction is removed from current after
        #     updating the parties of the active interaction
        # 2. if no corresponding interaction exists in current, the interaction has finished and is moved into recorded.
        # 3. at the end of this code, the remaining current interactions are new and need to be moved into active
        for i in range(len(Interaction.active) - 1, -1, -1):
            for j in range(len(Interaction.current) - 1, -1, -1):
                if Interaction.equal(Interaction.current[j], Interaction.active[i]):
                    # for critical interactions: update the parties involved before deleting the current interaction
                    if Interaction.active[i]._critical:
                        Interaction.active[i]._parties = list(set(Interaction.active[i]._parties) | set(Interaction.current[j]._parties))
                        Interaction.active[i]._shorthand = RoadUser.create_shorthand(Interaction.active[i]._parties)
                    Interaction.current.remove(Interaction.current[j])
                    break  # to next element in active
            else:
                # move interaction into recorded
                Interaction.active[i].move_active_interaction_to_recorded(clk.real_time())

        # the remaining current interactions are new and should be added to the set of active interactions
        for i in Interaction.current:
            Interaction.active.append(i)
            # print('new current copied to active, active set=', [ai._ID for ai in active], 
            #       'current set=', [ci._ID for ci in current])

    @staticmethod
    def aggregate_current_interactions():
        """ This function processes the set of current interactions
            and aggregates them into multi-party interactions when they share road users.
            any interactions which are aggregated into new, multi-party interactions are deleted
                when the new interaction is created.
            all interactions which are not aggregated into multi-party interactions remain unchanged.
            At this function’s conclusion, no current interactions should share road users.
        """
        if len(Interaction.current) > 1:                     # need enough current interactions to aggregate
            aggregation_not_done = True
            while aggregation_not_done:
                # this loop compares all current interactions to each other looking for members which share road users
                # if 2 interactions share a road user and at least one is a non-critical interaction, combine them
                aggregation_not_done = False
                for ci1, ci2 in combinations(Interaction.current, 2):
                    if Interaction.share_road_users(ci1, ci2) and not(ci1._critical and ci2._critical):
                        ci3 = Interaction.combine_interactions(ci1, ci2)
                        Interaction.current.append(ci3)
                        Interaction.current.remove(ci1)
                        Interaction.current.remove(ci2)
                        aggregation_not_done = True
                        break

    def combine_interactions(self, i2):
        """ This fcn combines two interactions and returns the combined interaction.
            This function assumes that at least one of the interactions is NOT critical because one set of critical
            road users must be passed on to the new interaction.
            should probably implement this as an overload of the + operator
        """
        if self._critical:      # combine set of road users to maintain the criticality of this interaction
            critical_road_users = self._critical_road_users
        elif i2._critical:      # combine set of road users to maintain the criticality of this interaction
            critical_road_users = i2._critical_road_users
        else:                   # combine set of road users without caring which road users are critical
            critical_road_users = self._critical_road_users

        road_users = list(set(self._parties) | set(i2._parties))     # new list of road users without duplicates
        start_time = min(self._start_time, i2._start_time)
        end_time = max(self._end_time, i2._end_time)
        extended = self._extended or i2._extended
        critical = self._critical or i2._critical
        i3 = Interaction(critical_road_users, road_users, start_time, end_time, extended, critical)
        # overwrite the start and end locations because parties may have moved since original interactions were created
        i3._start_location = min(self.west_end(), i2.west_end())
        i3._end_location = max(self.east_end(), i2.east_end())
        return i3

    @staticmethod
    def flush_active_interactions_to_recorded():
        """This function moves all active interactions into recorded, used at end of main program only
        """
        # move all active interactions to the recorded list with a 0 end time to indicate forced termination
        while len(Interaction.active) != 0:
            for ai in Interaction.active:
                ai.move_active_interaction_to_recorded(0)

    def move_active_interaction_to_recorded(self, end_time):
        """This function moves one active interaction into the recorded list and removes it from the active list.
            Before making the move, it adds a recorded_ID and end_time to the interaction and updates its shorthand code.
        """
        self._ID = Interaction.recorded_id
        Interaction.recorded_id += 1
        self._end_time = end_time
        self._shorthand = RoadUser.create_shorthand(self._parties)
        Interaction.recorded.append(self)
        Interaction.active.remove(self)
        Interaction.num_recorded_iactions += 1

    @staticmethod
    def output_all_created_interactions():
        """This function outputs all interactions created during this simulation to stdout
        """
        print('\nInteractions Log')

        # move all active interactions to the recorded list
        Interaction.flush_active_interactions_to_recorded()

        # make sure we have some recorded interactions to do something with
        if len(Interaction.recorded) == 0:
            print('No interactions occurred in this run')
            print()                                         # print blank lines so header length is same
            print()
            return

        # write out all summary information on interactions
        print('Total number of unaggregated interactions:', Interaction.num_unaggregated_iactions)
        print('Total number of recorded interactions:', Interaction.num_recorded_iactions)
        print()

        # sort all of the recorded interactions by their ID #
        Interaction.recorded.sort(key=attrgetter('_ID'))

        # write out all recorded interactions to stdout
        for ri in Interaction.recorded:
            print(ri)

    def is_critical(self):
        """Returns True if the interaction is a critical one, ie it was established with 2 MVs with opposing directions, else False
        """
        return self._critical

    def contains_vru(self):
        """Returns True if at least one of the parties to an interaction is a ped or cyclist, else False
        """
        if (self._shorthand.count("P") != 0) or (self._shorthand.count("B") != 0) or \
           (self._shorthand.count("p") != 0) or (self._shorthand.count("b") != 0):
            return True
        else:
            return False

    def contains_mv(self):
        """Returns True if two of the parties to an interaction are MVs, else False
        """
        if (self._shorthand.count("M") + self._shorthand.count("m")) == 2:
            return True
        else:
            return False

    def start_time(self):
        """Return the start time of the passed interaction
        """
        return self._start_time

    def end_time(self):
        """Return the end time of the passed interaction
        """
        return self._end_time

    def west_end(self):
        """Return the westmost point of all vehicles involved in the interaction
        """
        return min([ru.west_end() for ru in self._parties])

    def east_end(self):
        """Return the eastmost point of all vehicles involved in the interaction
        """
        return max([ru.east_end() for ru in self._parties])

# END Interactions Class  ********************************************************************************************


class Test:
    """ This class contains the workings of the test capability which allows an input file containing commands to
        create road users, allow time to pass, set variable values which permits detailed testing of the code.

        The following test commands are defined by process_test_commands function:
            "set_time XX": sets the simulation clock to XX seconds
            "new_road_user XX": creates a road user using the XX string and places it OnRoad
            XX for (type='Motor Vehicle', start_locn=0, length=6.0, speed=11.176, dirxn='EastBound') is written as
                'new_road_user Motor Vehicle 0 6.0 11.176 EastBound'
            "del_road_user XX": moves the road user identified by the ID in XX to OffRoad status - not implemented
            "del_all_road_users": moves all OnRoad road users to OffRoad status
            "wait XX": waits XX seconds until processing the next test file command
            "set_ext_interaction_time XX": sets the extended interaction time to XX seconds
            "end_test": ends the test by setting clock equal to its end time
            "print ru": prints list of OnRoad and OffRoad users
            "print i": prints list of Active and Recorded interactions
            blank lines and comments are ignored. comments start with a pound sign and blank, '# '
    """

    wait_time = 0

    def __init__(self):
        """ Constructor for Test class - open test input file, init wait_time timer
        """
        sys.stdin = open('interaction test file.txt')
        Test.wait_time = 0

    @staticmethod
    def process_test_input_file():
        """ This function is called from the main simulation loop to time out the wait timer and read commands
            from the test input file.
        """
        if Test.wait_time == 0:
            while Test.wait_time == 0:
                try:
                    test_cmd = input()
                except EOFError:
                    return
                else:
                    Test.process_test_commands(test_cmd)
        else:
            # we're timing out a wait command
            Test.wait_time = Test.wait_time - 1

    def process_test_commands(cmd):
        """ This function executes a test command passed to it. Only one command allowed in the passed cmd parameter.
            The following test commands are defined:
            "set_time XX": sets the simulation clock to XX seconds
            "new_road_user XX": creates a road user using the XX string and places it OnRoad
            XX for (type='Motor Vehicle', start_locn=0, length=6.0, speed=11.176, dirxn='EastBound') is written as
                'new_road_user Motor Vehicle 0 6.0 11.176 EastBound'
            "del_road_user XX": moves the road user identified by the ID in XX to OffRoad status - not implemented
            "del_all_road_users": moves all OnRoad road users to OffRoad status
            "wait XX": waits XX seconds until processing the next test file command
            "set_ext_interaction_time XX": sets the extended interaction time to XX seconds
            "print ru": prints a list of OnRoad and OffRoad road users
            "print i": prints a list of Active and Recorded interactions
            "end_test": ends test by setting clock equal to the end time
            blank lines and comments are ignored. comments start with a pound sign and blank, '# '
        """

        cmd_list = cmd.split()

        # do nothing with blank lines and comments
        if len(cmd_list) == 0 or cmd_list[0].startswith('#'):
            return

        # is there a more pythonic way to implement elif chain?
        # process other commands in test file
        if cmd_list[0].startswith('set_time'):
            clk.set_time(float(cmd_list[1]))

        elif cmd_list[0].startswith('wait'):
            Test.wait_time = float(cmd_list[1]) * 1/clk.time_per_tick()

        elif cmd_list[0].startswith('new_road_user'):
            # need to handle Motor Vehicle separately since it includes a blank which messes with .split
            if cmd_list[1] == 'Motor':
                RoadUser(cmd_list[1] + ' ' + cmd_list[2], int(cmd_list[3]), float(cmd_list[4]), float(cmd_list[5]),
                         cmd_list[6], float(cmd_list[5]) * clk.time_per_tick())
            else:
                RoadUser(cmd_list[1], int(cmd_list[2]), float(cmd_list[3]), float(cmd_list[4]), cmd_list[5],
                         float(cmd_list[4]) * clk.time_per_tick())

        elif cmd_list[0].startswith('del_road_user'):
            # for ru in RoadUser.OnRoad:
            #     if ru._ID == int(cmd_list[1]):
            #         RoadUser.transfer_road_user_to_off_road(ru, 0)
            #         break
            pass

        elif cmd_list[0].startswith('del_all_road_users'):
            while len(RoadUser.OnRoad) != 0:
                for ru in RoadUser.OnRoad:
                    RoadUser.transfer_road_user_to_off_road(ru, 0)

        elif cmd_list[0].startswith('set_ext_interaction_time'):
            RoadUser.set_extended_interaction_time(float(cmd_list[1]))

        elif cmd_list[0].startswith('print'):
            if cmd_list[1].startswith('ru'):
                # print road users
                print()
                print("Road Users On Road")
                for ru in RoadUser.OnRoad:
                    print(ru)
                print("Road Users Off Road")
                for ru in RoadUser.OffRoad:
                    print(ru)
            elif cmd_list[1].startswith('i'):
                # print interactions
                print()
                print("Active Interactions")
                for ri in Interaction.active:
                    print(ri)
                print("Recorded Interactions")
                for ri in Interaction.recorded:
                    print(ri)
            else:
                # print parameter is unknown
                print()
                print('"', cmd, '" from test input file is unknown and is ignored')

        elif cmd_list[0].startswith('end_test'):
            clk.set_time(clk.end_time())

        else:
            # command is unknown
            print()
            print('"', cmd, '" from test input file is unknown and is ignored')

# END Test Class  ********************************************************************************************


def initialize_everything():
    """ initialize all objects and variables at the beginning of the program
    """
    # do we really need these global vars
    global clk, road, window

    clk = SimulationClock(0, args.time * 3600, .1)
    road = Road(0, args.roadlen)

    if args.test:
        # we are testing with an input file that provides test commands so set that up
        Test()
    else:
        # Create and initialize all of the objects with values from command line for a normal run
        if args.seed == 0:
            random.seed()
        else:
            random.seed(args.seed)

        # determine number of road users per hour for each mode and each end of the road
        eastbound_peds_per_hr = args.pedhr * (args.pedsplit * .01)
        westbound_peds_per_hr = args.pedhr * (100 - args.pedsplit) * .01
        eastbound_cycs_per_hr = args.cychr * (args.cycsplit * .01)
        westbound_cycs_per_hr = args.cychr * (100 - args.cycsplit) * .01
        eastbound_mvs_per_hr =  args.mvhr  * (args.mvsplit * .01)
        westbound_mvs_per_hr =  args.mvhr  * (100 - args.mvsplit) * .01

        # create the sources of road users along the road
        if westbound_peds_per_hr != 0:
            RoadUserSource('Pedestrian',    westbound_peds_per_hr, road.east_end(), 'WestBound', args.pedspeed, args.pedspeeddistr, 1.0, 0, args.pedarrival)
        if westbound_cycs_per_hr != 0:
            RoadUserSource('Bicycle',       westbound_cycs_per_hr, road.east_end(), 'WestBound', args.cycspeed, args.cycspeeddistr, 2.0, .5, args.cycarrival)
        if westbound_mvs_per_hr != 0:
            RoadUserSource('Motor Vehicle', westbound_mvs_per_hr,  road.east_end(), 'WestBound', args.mvspeed,  args.mvspeeddistr,  6.0, 1.5, args.mvarrival)
        if eastbound_peds_per_hr != 0:
            RoadUserSource('Pedestrian',    eastbound_peds_per_hr, road.west_end(), 'EastBound', args.pedspeed, args.pedspeeddistr, 1.0, 0, args.pedarrival)
        if eastbound_cycs_per_hr != 0:
            RoadUserSource('Bicycle',       eastbound_cycs_per_hr, road.west_end(), 'EastBound', args.cycspeed, args.cycspeeddistr, 2.0, .5, args.cycarrival)
        if eastbound_mvs_per_hr != 0:
            RoadUserSource('Motor Vehicle', eastbound_mvs_per_hr,  road.west_end(), 'EastBound', args.mvspeed,  args.mvspeeddistr,  6.0, 1.5, args.mvarrival)

        # set duration of extended interaction envelope
        RoadUser.set_extended_interaction_time(args.iaxntime)

    if args.display > 1:
        window = Display(args.display)


#  START OF MAIN LOGIC    ******************************************************************************************

if __name__ == '__main__':

    # save date and time of program start for output file
    program_start_time = time.perf_counter()

    # the command line parsing logic has NOT been (officially) tested!
    # get command line parameter values
    parser = argparse.ArgumentParser(description='Simulate an ABL and count road user interactions.')
    parser.add_argument('-r', '--roadlen', type=int, default=1000, help='specify road length in meters.')
    parser.add_argument('-t', '--time', type=float, default=1, help='specify simulation duration in hours.')
    parser.add_argument('-it', '--iaxntime', type=float, default=2.0, help='specify MVxMV interaction in seconds.')

    parser.add_argument('-c', '--cychr', type=int, default=20, help='specify # of cyclists per hour.')
    parser.add_argument('-p', '--pedhr', type=int, default=10, help='specify # of pedestrians per hour.')
    parser.add_argument('-v', '--mvhr', type=int, default=60, help='specify # of motor vehicles per hour, range 0-3600.')

    parser.add_argument('-cp', '--cycsplit', type=int, default=50, help='specify %% of cyclist volume traveling east, the remaining volume will travel west. range 0-100.')
    parser.add_argument('-pp', '--pedsplit', type=int, default=50, help='specify %% of pedestrian volume traveling east, the remaining volume will travel west. range 0-100.')
    parser.add_argument('-vp', '--mvsplit', type=int, default=50, help='specify %% of vehicle volume traveling east, the remaining volume will travel west. range 0-100.')

    parser.add_argument('-ca', '--cycarrival', type=int, default=1, help='specify cyclist arrival spacing (0=all cyclists arrive at equal intervals, 1=negative exponential distribution arrival).')
    parser.add_argument('-pa', '--pedarrival', type=int, default=1, help='specify pedestrian arrival spacing (0=all pedestrians arrive at equal intervals, 1=negative exponential distribution arrival).')
    parser.add_argument('-va', '--mvarrival', type=int, default=1, help='specify vehicle arrival spacing (0=all vehicles arrive at equal intervals, 1=negative exponential distribution arrival).')

    parser.add_argument('-cs', '--cycspeed', type=float, default=5.3645, help='specify cyclist speed in meters/second.')
    parser.add_argument('-ps', '--pedspeed', type=float, default=1.22, help='specify ped speed in meters/second.')
    parser.add_argument('-vs', '--mvspeed', type=float, default=11.176, help='specify vehicle speed in meters/second.')

    parser.add_argument('-cd', '--cycspeeddistr', type=int, default=1, help='specify cyclist speed distribution (0=all cyclists travel at cycspeed, 1=normal distribution with 85th percentile at cycspeed value).')
    parser.add_argument('-pd', '--pedspeeddistr', type=int, default=1, help='specify pedestrian speed distribution (0=all pedestrians travel at pedspeed, 1=normal distribution with 85th percentile at pedspeed value).')
    parser.add_argument('-vd', '--mvspeeddistr', type=int, default=1, help='specify vehicle speed distribution (0=all vehicles travel at mvspeed, 1=normal distribution with 85th percentile at mvspeed value).')

    parser.add_argument('-d', '--display', type=int, default=1, help='specify a display level from 0 to 9.\n' +
                        '0 = display only the number and rate of interactions\n' +
                        '1 = display the detailed interaction and road user information created in the simulation\n' +
                        '2 = display the graphical representation of the simulation while running\n' +
                        '9 = display all current debug information during the simulation run.')
    parser.add_argument('-sd', '--seed', type=int, default=0, help='specify value of randomization seed (a value of 0 allows true randomization, a nonzero value used as seed provides repeatable results).')
    parser.add_argument('-te', '--test', default=False, action="store_true", help='include this parameter for automated test, else omit it. Automated tests take commands from a file called "test file.txt".')
    parser.add_argument('-o', '--outfile', default=False, action="store_true", help='include this parameter to enable output to "mcsim output.txt" for use by Double Check.')
    args = parser.parse_args()

    initialize_everything()

    # create a logfile of output if the -o parameter was specified
    # this is useful when comparing the output of the simulator to the double checker output
    if args.outfile:
        sys.stdout = Logger()

    # writing to a standard output file is only here for testing. should goto stdout for pipelining in real world
    # sys.stdout = open('C:\\Users\Michael\PycharmProjects\ABLSim\output file.txt', 'w')

    # write out important summary information on command line parameter values
    # avoid printing out time-specific info because it screws up automated testing
    if args.display > 0:
        if not args.test:
            print('\nSimulation began at', str(datetime.datetime.now()))

        print('\nCommand line or default parameter values')
        print('road length:      ', args.roadlen, 'meters')
        print('time:             ', args.time, 'hours')
        print('MVxMV i-axn time/length: ', args.iaxntime, 'seconds / ~', args.iaxntime * args.mvspeed, 'meters')
        print('ped volume:       ', args.pedhr, 'pedestrians/hour on entire road')
        print('bike volume:      ', args.cychr, 'bikes/hour on entire road')
        print('MV volume:        ', args.mvhr, 'motor vehicles/hour on entire road')
        print('ped % split:      ', args.pedsplit, '% of pedestrian volume heading east')
        print('bike % split:     ', args.cycsplit, '% of bike volume heading east')
        print('MV % split:       ', args.mvsplit, '% of motor vehicle volume heading east')
        print('ped arrival distr:  ', args.pedarrival, '0 = equal intervals, 1 = negative exponential distribution')
        print('bike arrival distr: ', args.cycarrival, '0 = equal intervals, 1 = negative exponential distribution')
        print('MV arrival distr:   ', args.mvarrival, '0 = equal intervals, 1 = negative exponential distribution')
        print('ped speed:        ', args.pedspeed, 'meters/second / ~', args.pedspeed * 2.24, 'MPH / ~', args.pedspeed * 3.28, 'feet/second')
        print('bike speed:       ', args.cycspeed, 'meters/second / ~', args.cycspeed * 2.24, 'MPH')
        print('MV speed:         ', args.mvspeed, 'meters/second / ~', args.mvspeed * 2.24, 'MPH')
        print('ped speed distr:  ', args.pedspeeddistr, '0 = fixed, 1 = normal distribution')
        print('bike speed distr: ', args.cycspeeddistr, '0 = fixed, 1 = normal distribution')
        print('MV speed distr:   ', args.mvspeeddistr, '0 = fixed, 1 = normal distribution')
        print('Display level:    ', args.display)
        if not args.test:
            print('Random seed:      ', args.seed, '. A 0 represents true randomization; any other value used as initial seed')
        print('\nSimulation parameter values')
        # this road length appears to be off by 1 meter, eg start at 0, end at 1000 should result in 1001 meters, not 1000
        print('Road west end at', road.west_end(), ', east end at', road.east_end(), 'for a total of', road.length(),
              'meters')
        # there may be another +/- 1 error in the clock value as well
        print('Clock started at', clk.value(), 'ticks and ran to', clk.end_time_ticks(), 'ticks, with each tick =',
              clk.time_per_tick(), 'seconds for a total of', clk.end_time() / 3600, 'hours.')
        print('Duration of extended interactions =', RoadUser.ext_iaxn_time, 'seconds.')
        if args.test:
            print('Test run with input provided from file. Some command line parameter values may not apply.')
        else:
            # these values only matter when not running with input from a test file of commands
            print('Number of Road User Sources =', str(len(RoadUserSource.list_of_road_user_sources)))
            for source in RoadUserSource.list_of_road_user_sources:
                print(source)
        print()

    # SIMULATION LOOP STARTS HERE  *****************************************************************************
    while clk.still_running():

        # move everybody down the road
        RoadUser.advance_RoadUsers_along_the_road()

        if not args.test:
            # give all of the sources of new road users the opportunity to create new road users
            for source in RoadUserSource.list_of_road_user_sources:
                source.add_new_road_users()
        else:
            # execute commands from test input file
            Test.process_test_input_file()

        # Identify all interactions occurring in this clock tick and move interactions through their lifecycle
        Interaction.identify_current_interactions()
        Interaction.update_interactions()

        # graphically display the simulation
        if args.display > 1:
            window.update()

        # increment the simulation clock
        clk.increment()
    else:
        # Simulation has ended, wrap it up
        if args.display > 0:
            # print out the simulated elapsed time for the run now that we've completed it
            print('Simulation duration:   ', clk.real_time()/3600, 'hours')

            # write out information on all interactions created during the run
            Interaction.output_all_created_interactions()

            # write out information on all road users created during the run
            RoadUser.output_all_created_road_users()

        # Output the number and hourly rate of interactions that are MVxMV only and the number that include VRUs
        iaxns_w_vrus = 0
        iaxns_mv_only = 0
        for ri in Interaction.recorded:
            if Interaction.is_critical(ri):
                if Interaction.contains_vru(ri):
                    iaxns_w_vrus += 1
                else:
                    iaxns_mv_only += 1
        print('Total Number of critical interactions = ', iaxns_w_vrus + iaxns_mv_only, '. Number with VRUS = ', iaxns_w_vrus,
              '. Number with MVs only = ', iaxns_mv_only, '.')
        print('Number of critical interactions per hour, both types     = ',
              (iaxns_mv_only + iaxns_w_vrus) / args.time)
        print('Number of critical interactions per hour including VRUs = ', iaxns_w_vrus / args.time)
        print('Number of critical interactions per hour with MVs only  = ', iaxns_mv_only / args.time)

        # avoid printing out time-specific info because it screws up automated testing
        if not args.test and args.display > 0:
            print()
            print('Simulation finished at', str(datetime.datetime.now()),
                  '. Program finished in', time.perf_counter()-program_start_time, 'seconds.')



