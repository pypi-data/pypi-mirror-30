from enum import Enum
from collections import namedtuple

from cached_property import cached_property

from .scraper import AllGymsScaper, MyGymScaper


class GymStatus(Enum):
    """
    Gyms at PureGym can have a status of coming soon, opening soon or ready.
    """

    coming_soon = 1
    ready = 2
    opening_soon = 4


GymLocation = namedtuple('GymLocation',
                         ['latitude', 'longitude', 'address', 'postcode'])

GymPrice = namedtuple('GymPrice',
                      ['per_month', 'joining_fee', 'pay_as_you_go'])

Gym = namedtuple('Gym',
                 ['id', 'url', 'slug', 'name', 'location', 'price', 'status'])

MyGym = namedtuple('MyGym', ['number_of_people'])


class PureGym:

    """The main class for interacting with the PureGym services."""

    def __init__(self, email_address=None, pin=None):
        self.email_address = email_address
        self.pin = pin

    @cached_property
    def my_gym(self):
        scraper = MyGymScaper(self.email_address, self.pin)
        return MyGym(number_of_people=scraper.number_of_people)

    @cached_property
    def gyms(self):
        """Find all the gyms."""

        scraper = AllGymsScaper()
        return [
            self._parse_gym_data(gym_data)
            for gym_data in scraper.data
        ]

    def _parse_gym_data(self, gym_data):
        location = GymLocation(
            latitude=gym_data['latitude'],
            longitude=gym_data['longitude'],
            address=gym_data['streetAddress'],
            postcode=gym_data['postcode'],
        )

        price = GymPrice(
            per_month=gym_data['monthlyfee'],
            joining_fee=gym_data['joiningfee'],
            pay_as_you_go=gym_data['payAsYouGoFee'],
        )

        return Gym(
            id=gym_data['id'],
            url='https://www.puregym.com{0}'.format(gym_data['url']),
            slug=gym_data['urlName'],
            name=gym_data['name'],
            location=location,
            price=price,
            status=GymStatus(gym_data['status']),
        )
