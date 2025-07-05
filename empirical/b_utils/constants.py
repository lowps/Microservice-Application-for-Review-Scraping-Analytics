import configparser
import os

parser = configparser.ConfigParser()
parser.read(os.path.join(os.path.dirname(__file__), "../config/config.conf"))

BRIGHTDATA_AUTH = parser.get("brightdata", "bright_data_auth")


# when you need to use the above data then:

# "sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# from utils.constants import BRIGHTDATA_AUTH"
