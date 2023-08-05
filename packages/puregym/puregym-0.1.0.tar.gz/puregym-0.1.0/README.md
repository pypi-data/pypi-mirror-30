# PyPureGym

Python module for interacting with PureGym.

## Installation

```bash
$ pip install puregym
```

## Usage

```python
>>> from puregym import PureGym
>>> puregym = PureGym()
>>> gym = puregym.gyms[0]
>>> gym
Gym(id=69, url='https://www.puregym.com/gyms/aberdeen-kittybrewster/', slug='aberdeen-kittybrewster', name='Aberdeen Kittybrewster', location=GymLocation(latitude=57.1614, longitude=-2.1123, address='Kittybrewster Retail Park, Bedford Road', postcode='AB24 3LJ'), price=GymPrice(per_month=16.99, joining_fee=15, pay_as_you_go=7.99), status=<GymStatus.ready: 2>)
```
