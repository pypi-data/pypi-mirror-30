import pytest
import random
import requests

from puregym import GymStatus, PureGym


puregym = PureGym()


@pytest.mark.parametrize('gym', puregym.gyms)
def test_a_gym(gym):
    assert gym.id is not None
    assert gym.name is not None
    assert gym.slug is not None

    assert gym.location.longitude is not None
    assert gym.location.latitude is not None

    if gym.status != GymStatus.coming_soon:
        assert gym.price.per_month is not None


@pytest.mark.parametrize('gym', random.sample(puregym.gyms, 5))
def test_gym_url_opens(gym):
    assert requests.get(gym.url).status_code == 200
