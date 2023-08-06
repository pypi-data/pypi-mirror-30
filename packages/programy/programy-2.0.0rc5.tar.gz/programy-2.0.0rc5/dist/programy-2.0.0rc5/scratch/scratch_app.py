from programy.extensions.weather.weather import WeatherExtension

class ScratchLicenseKeys(object):

    def __init__(self, keys=None):
        if keys is not None:
            self.keys = keys
        else:
            self.keys = {}

    def get_key(self, key):
        return self.keys[key]

    def has_key(self, name):
        return name in self.keys

class ScratchBot:

    def __init__(self):
        self.license_keys = ScratchLicenseKeys()


def get_observation(bot):
    result = extension.execute(bot, 'scratch', "OBSERVATION LOCATION KY39UR WHEN 0")
    print(result)

def get_5day_forecast(bot):
    result = extension.execute(bot, 'scratch', "FORECAST5DAY LOCATION KY39UR WHEN 1")
    print(result)

def get_24hour_forecast(bot):
    result = extension.execute(bot, 'scratch', "FORECAST24HOUR LOCATION KY39UR WHEN 12")
    print(result)


if __name__ == '__main__':

    extension = WeatherExtension()

    bot = ScratchBot()
    bot.license_keys.keys['METOFFICE_API_KEY'] = 'e5893ec0-4594-4bc7-a01b-b17a0c6d85fe'

    #get_observation(bot)
    get_24hour_forecast(bot)
    get_5day_forecast(bot)
