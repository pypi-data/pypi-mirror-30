from city import *
from weather import *

def main():
    import sys

    if len(sys.argv) == 3:
        city = City(sys.argv[1], sys.argv[2])
    else:
        city = City(sys.argv[1])

    city.print_city()
    city.print__doc__()

    weather = Weather(city)
    try:
        weather.get_temperature()
    except:
        print "Wrong city name"


if __name__ == "__main__":
    main()
