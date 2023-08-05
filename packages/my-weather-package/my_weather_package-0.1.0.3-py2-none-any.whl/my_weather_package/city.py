
class City(object):
    """Class for the city instances"""

    def __init__(self, name, country=None):
        """Constructor for the City class, takes\ name of the city and it's country as params"""
        self.city_name = name
        if country is not None:
            self.country = country
        else:
            self.country = None

    def print_city(self):
        """Print city's country, if given"""
        if self.country is not None:
            print self.city_name + " from " + self.country
        else:
            print self.city_name

    def print__doc__(self):
        print self.__doc__
