from bs4 import BeautifulSoup
from requests import Session
from avenyn_lunch.Restaurant import Restaurant


day_routes = [
    'dagens-lunch-man',
    'dagens-lunch-tis',
    'dagens-lunch-ons',
    'dagens-lunch-tor',
    'dagens-lunch-fre'
]


class AvenySession(object):

    def __init__(self):
        self.session = Session()
        self.base_url = 'https://www.avenyn.se/'

    def get_restaurants(self):
        restaurants = {}

        for i, route in enumerate(day_routes):
            resp = self.session.get(
                self.base_url + route,
                allow_redirects=True
            )

            soup = BeautifulSoup(resp.text, 'html.parser')

            for box in soup.find_all('li', {'class': 'dagenslunchruta'}):
                if box.get('id') not in restaurants:
                    restaurants[box.get('id')] = Restaurant(
                        name=box.get('id'),
                        image=box.find('img').get('src')
                    )

                menu_text = box.find('p').encode_contents()
                foods = menu_text.split('<br/> <br/>')

                for food in foods:
                    if not len(food):
                        continue

                    food = ' '.join(food.split(' ')[1:]) if food[0] == ' '\
                        else food

                    restaurants[box.get('id')].add_menu_item(i, food)

        return restaurants.values()
