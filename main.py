import requests
import json
from geopy.geocoders import Nominatim
import mysql.connector
import time
import re
from googletrans import Translator
from langdetect import detect, LangDetectException

my_db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="wfbruhff-3rgwr3-wrt193rfr",
    database="wildfires"
)
cursor = my_db.cursor()
def get_api_url(event):
    return f"https://eonet.gsfc.nasa.gov/api/v3/categories/{event}"
def return_api(event):
    api_url = get_api_url(event)
    r = requests.get(api_url)
    events_earth = r.json()
    return events_earth

def get_event(event):
    events_earth = return_api(event)
    with open(f'{event}.json', 'w') as dataset:
        dataset.write(json.dumps(events_earth, indent=10))
    return events_earth

def find_address_data(location):
    city = "unknow"
    region = "unknow"
    territorium = "unknow"
    country = "unknow"
    translator = Translator()

    address_parts = location.address.split(',')

    print(address_parts)
    print(len(address_parts))

    def translate_address_part(text):
        text = text.strip()
        text = re.sub(r'\([^)]*\)', '', text).strip()
        try:
            language = detect(text)

        except LangDetectException:
            return "unknown"
        if language not in ['de', 'en']:
            try:
                translated_text = translator.translate(text, dest='en').text
                time.sleep(1)  # Hinzufügen einer Verzögerung zwischen den Anfragen
                return translated_text
            except Exception as e:
                return text  # Rückgabe des Originaltextes bei einem Fehler
        return text


    if len(address_parts) >= 1:
        if len(address_parts) == 2:
            city = translate_address_part(address_parts[0])
            country = translate_address_part(address_parts[-1])

        elif len(address_parts) == 3:
            region = translate_address_part(address_parts[0])
            territorium = translate_address_part(address_parts[-2])
            country = translate_address_part(address_parts[-1])

        elif len(address_parts) >= 4:
            territorium = translate_address_part(address_parts[-2])
            country = translate_address_part(address_parts[-1])
            if len(address_parts) == 4:
                city = translate_address_part(address_parts[0])
                region = translate_address_part(address_parts[1])

            if len(address_parts) == 5:
                city = translate_address_part(address_parts[1])
                region = translate_address_part(address_parts[-4])

            elif len(address_parts) >= 6:
                city = translate_address_part(address_parts[-5])
                region = translate_address_part(address_parts[-4])
                territorium = translate_address_part(address_parts[-3])

                if len(address_parts) == 7:
                    city = translate_address_part(address_parts[0])

                if len(address_parts) == 8:
                    city = translate_address_part(address_parts[1])


    return city, region, territorium, country


def fill_sql(event_date, date_time, timestamp, geo_type, longitude, latitude, city, region, territorium, country, mag_value, mag_unit, square_meters, square_kilometers):
    insert_global_wildfires = """
                INSERT INTO global_wildfires (
                    date, time, timestamp, longitude, latitude, city, region, territorium, country
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)

            """
    values_global_wildfires = (
        event_date, date_time, timestamp, longitude, latitude,
        city, region, territorium, country
    )
    cursor.execute(insert_global_wildfires, values_global_wildfires)
    event_id = cursor.lastrowid  # ID des gerade eingefügten Datensatzes abrufen
    insert_wildfire_magnitude = """
                INSERT INTO wildfires_size (event_id, type, magnitude_unit, magnitude_value, square_meter, square_km)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
    values_wildfire_magnitude = (event_id, geo_type, mag_unit, mag_value, square_meters, square_kilometers)

    cursor.execute(insert_wildfire_magnitude, values_wildfire_magnitude)
    my_db.commit()


collected_data = []
#
# Main Function
#
def fetch_data(events_earth):
    event_list = events_earth["events"]


    for e in event_list\
            :
        event_date = ""
        event_time = ""
        timestamp = ""
        geo_type = ""
        mag_unit = None
        mag_value = None
        latitude = 0
        longitude = 0
        square_meters = None
        square_kilometers = None
        city = "unknow"
        region = "unknow"
        territorium = "unknow"
        country = "unknow"

        for date_time in e['geometry']:
            dt = date_time['date']
            event_date = dt.split('T')[0]
            event_time = dt.split('T')[1].rstrip('Z')
            timestamp = f"{event_date} {event_time}"
            geo_type = date_time['type']

        for magnitude in e['geometry']:

            mag_unit = None  # Standartwert für Acres in Quadratmeter
            mag_value = None
            if magnitude['magnitudeUnit'] == "acres":
                mag_unit = 4046.86                      # Standartwert für Acres in Quadratmeter
                mag_value = magnitude['magnitudeValue']
                square_meters = round(mag_value * mag_unit, 2)
                square_kilometers = round(square_meters / 1_000_000, 2)



        for coordinates in e['geometry']:
            longitude = coordinates['coordinates'][0]
            latitude = coordinates['coordinates'][1]

            geolocator = Nominatim(user_agent="MyApple")  # Geokodierungsdienst aktivieren
            location = geolocator.reverse((latitude, longitude), exactly_one=True)  # Standort ermitteln

            city, region, territorium, country = find_address_data(location)



        data_fetch_act = [
            event_date, event_time, timestamp, geo_type, longitude,
            latitude, city, region, territorium, country,
            mag_value,mag_unit, square_meters, square_kilometers
        ]

        collected_data.append(data_fetch_act)




event_date = get_event("wildfires")
fetch_data(event_date)

for i in collected_data:
    fill_sql(i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7], i[8], i[9], i[10], i[11], i[12],i[13])
    print("übertragen")

cursor.close()
my_db.close()