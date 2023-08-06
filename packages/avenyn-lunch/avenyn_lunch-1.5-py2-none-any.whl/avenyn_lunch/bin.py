from avenyn_lunch.AvenySession import AvenySession
from avenyn_lunch.constants import DAYS


def run():
    session = AvenySession()

    restaurants = session.get_restaurants()

    for rest in restaurants:
        prev_name = None

        for i, daymenu in enumerate(rest.weekly_menu):
            dayname = DAYS[i]

            if prev_name != rest.name:
                print('\n*----[ {} ]----*'.format(rest.name))

            print('> {}:'.format(dayname))

            for food in daymenu:
                print('- ' + food)

            prev_name = rest.name
