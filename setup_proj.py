from DataManager.WorldClim import WorldClimAPI
from irradiance.models.delta import Delta
from irradiance.models.model import SolarPanel

# Setting up connection with the API
print("Setting up API authentication...")
email_address = input("Email Address: ")
nrel_key = input("NREL API Key: ")
openweather_key = input("OpenWeather API Key: ")

with open('DataManager/keys.yaml', 'a') as keys_file:
    keys_file.write(f"EMAIL: \"{email_address}\"\n")
    keys_file.write(f"NREL_API_KEY: \"{nrel_key}\"\n")
    keys_file.write(f"OPEN_WEATHER_API_KEY: \"{openweather_key}\"\n")

# Download the WorldClim data
print("Setting up WorldClim dataset...")
wc_api = WorldClimAPI()
print("WorldClim: downloading data...")
wc_api.download()
print("WorldClim: tabelizing data...")
wc_api.tabelize()

# Training the Delta Model
print("Setting up the Delta model...")
sp = SolarPanel(eff=0, cap=0, area=0, pr=0)
delta_model = Delta(sp)
print("Delta: Training the Delta Model...")
delta_model.train(verbose=True)
