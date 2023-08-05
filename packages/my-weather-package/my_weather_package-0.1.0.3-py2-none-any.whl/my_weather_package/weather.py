
class Weather(object):
    """Class for weather related actions on a city
    """

    def __init__(self, city_obj):
        """Constructor of the weather class, takes only a City class object
        """
        self.city = city_obj

    def kelvin_to_celsius(self, temp_k):
        """converts degrees from kelvin to celsius
        """
        return temp_k - 273.15

    def get_temperature(self):
        """function to get temperature using OWM API,
           temperature is stored from the json response and converted from Kelvin to Celsius
        """
        import requests
        json_object = requests.get('http://api.openweathermap.org/data/2.5/weather?q='
                                   + self.city.city_name + '&appid=1d95d786cb30c4e75983b8ee6da19535').json()


        temp_c = self.kelvin_to_celsius(float(json_object['main']['temp']))

        print "Temperature in " + self.city.city_name + " is " + str(temp_c)
