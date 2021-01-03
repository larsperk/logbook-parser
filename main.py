import csv
from datetime import datetime
from math import radians, cos, sin, asin, sqrt

trans_dict = {
    'BOWLESAGAWAM': '7B0',
    'OXFORD': '43M',
    'WICHABAI': 'SYWI',
    'WICHIBAI': 'SYWI',
    'NORTHADAMS': 'AQW',
    'NORTHCENTRAL': 'SFZ',
    'SHIRLEY': '61MA',
    'MARSTONMILLS': '2B1',
    'BARRE': '8B5',
    'NORTHAMPTON': '7B2',
    'STERLING': '3B3',
    "9B!": '9B1',
    "DADANAWA": "SYDW",
    "GUNNS": "SYGN",
    "WJC": "KWJF",
    "9B4": "61MA",
    "YUL": "CYUL",
    "2B4": "KUUU",
    "NEWPORT": "KUUU",
    "N76": "4PA0",
    "SFD": "KSFM",
    "AUB": "KLEW",
    "NUG": "KNUQ",
    "40N": "KMQS",
    "PUT": "",
    "VOR": "",
    "PLACEHOLDER": "",
    "LOGBOOK": "",
    "PIRU": "",
}


def distance_between_airports(airport_1, airport_2, airport_lookup_dict):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """

    lon1 = airport_lookup_dict.get(airport_1, {}).get("long")
    lat1 = airport_lookup_dict.get(airport_1, {}).get("lat")

    if not lon1 and not lat1:
        lon1 = airport_lookup_dict.get("K" + airport_1, {}).get("long")
        lat1 = airport_lookup_dict.get("K" + airport_1, {}).get("lat")

    lon2 = airport_lookup_dict.get(airport_2, {}).get("long")
    lat2 = airport_lookup_dict.get(airport_2, {}).get("lat")

    if not lon2 and not lat2:
        lon2 = airport_lookup_dict.get("K" + airport_2, {}).get("long")
        lat2 = airport_lookup_dict.get("K" + airport_2, {}).get("lat")

    if lon1 and lat1 and lon2 and lat2:
        # convert decimal degrees to radians
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

        # haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))

        # Radius of earth in nautical miles
        radius = 3958.8 / 1.151
        distance = round(c * radius, 0)

    else:
        if not lat1:
            print(airport_1)
        if not lat2:
            print(airport_2)

        distance = 0.0

    return distance


def load_airport_data():
    airport_lookup_dict = {}
    with open("airports.csv", 'r', newline='') as airport_csv_file:
        airport_csv_reader = csv.reader(airport_csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for airport in airport_csv_reader:
            """
            if airport[0] != 'ident':
                airport_lookup_dict[airport[0]] = {
                    "long": float(airport[11].split(",")[0]), "lat": float(airport[11].split(",")[1])
                }
            """
            ident = airport[1]
            gps_code = airport[12]
            iata_code = airport[13]
            local_code = airport[14]

            if airport[0] != 'id':
                longitude = float(airport[5])
                latitude = float(airport[4])

                airport_lookup_dict[ident] = {
                    "long": longitude, "lat": latitude
                }

                if gps_code:
                    airport_lookup_dict[gps_code] = {
                        "long": longitude, "lat": latitude
                    }

                if iata_code:
                    airport_lookup_dict[iata_code] = {
                        "long": longitude, "lat": latitude
                    }
                if local_code:
                    airport_lookup_dict[local_code] = {
                        "long": longitude, "lat": latitude
                    }

    return airport_lookup_dict


def translate_identifier(identifier):
    identifier = trans_dict.get(identifier, identifier)
    if len(identifier) == 3 and not(any(c.isnumeric() for c in identifier)):
        identifier = "K" + identifier
    identifier = "UNKN" if not identifier else identifier

    return identifier.upper()


input_flights = []
aircraft_table = []

with open("logbook_2020-11-29_16_08_34.csv", 'r', newline='') as logbook_csv_file:
    flight_csv_reader = csv.reader(logbook_csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    logbook_started = False
    for input_line in flight_csv_reader:

        if logbook_started:
            input_flights.append(input_line)

        else:
            aircraft_table.append(input_line)

            if input_line[0] == 'Flights Table':
                logbook_started = True

airport_lat_long_dict = load_airport_data()

output_flights = []
starting_airport = ''

for flight in input_flights:
    if flight[0] != "Date":

        origin_airport = translate_identifier(flight[2])
        destination_airport = translate_identifier(flight[3])

        total_input_flight_distance = distance_between_airports(origin_airport, destination_airport, airport_lat_long_dict)

        flight[2] = origin_airport
        flight[3] = destination_airport

        flight_datetime = datetime.now()
        try:
            flight_datetime = datetime.strptime(flight[0], '%Y-%m-%d')
            valid = True

        except ValueError:
            valid = False

        if valid and flight_datetime < datetime(2016, 1, 1) and flight[0] != "Date":
            flight_route = flight[4]
            route_segments = flight_route.split(' ')
            route_has_segments_to_split = all(len(x) == 3 or len(x) == 4 for x in route_segments)

            if route_has_segments_to_split:
                starting_airport = origin_airport
                total_number_of_segments = len(route_segments) + 1

                total_segments_flight_distance = 0.0
                segment_flights = []

                for i in range(total_number_of_segments):
                    segment_flight = flight.copy()
                    segment_flight[4] = ''

                    segment_origin_airport = translate_identifier(starting_airport) if i == 0 else translate_identifier(route_segments[i - 1])
                    segment_destination_airport = translate_identifier(route_segments[i]) if i != total_number_of_segments - 1 else translate_identifier(flight[3])
                    segment_distance = distance_between_airports(segment_origin_airport,
                                                                 segment_destination_airport,
                                                                 airport_lat_long_dict,
                                                                 )

                    segment_distance = 25 if segment_distance == 0 else segment_distance

                    segment_flight[2] = segment_origin_airport
                    segment_flight[3] = segment_destination_airport

                    for j in range(18, 23):
                        landing_count = int(flight[j]) if flight[j] else 0
                        segment_flight[j] = 1 if landing_count > 1 else landing_count

                    segment_flight[17] = segment_distance
                    segment_flights.append(segment_flight)
                    total_segments_flight_distance += segment_distance

                for segment_flight in segment_flights:
                    for i in list(range(11, 17)) + list(range(23, 25)) + list(range(36, 38)):
                        hours = float(segment_flight[i]) if segment_flight[i] else 0.0
                        segment_distance = float(segment_flight[17])
                        segment_distance = 25 if segment_distance == 0.0 else segment_distance
                        segment_flight[i] = round(hours * segment_distance / total_segments_flight_distance, 1)

                    output_flights.append(segment_flight)

            else:
                flight[17] = total_input_flight_distance
                output_flights.append(flight)

        else:
            flight[17] = total_input_flight_distance
            output_flights.append(flight)

    else:
        output_flights.append(flight)

for flight in output_flights:
    for i in range(18, 22):
        try:
            flight[i] = 0 if not flight[i] else int(flight[i])

        except ValueError:
            pass

    try:
        total_takeoffs = (int(flight[18]) + int(flight[20]))
        total_landings = (int(flight[19]) + int(flight[21]))

        if total_takeoffs > total_landings:
            flight[19] = int(flight[19]) + total_takeoffs - total_landings

        if total_landings > total_takeoffs:
            flight[18] = int(flight[18]) + total_landings - total_takeoffs

        flight[18] = int() if (int(flight[18]) + int(flight[20])) == 0 else flight[18]
        flight[19] = int(flight[18]) + int(flight[20]) if (int(flight[19]) + int(flight[21])) == 0 else flight[19]

    except ValueError:
        pass

with open(f'logbook-output.csv', 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
    csv_writer.writerows(aircraft_table)
    csv_writer.writerows(output_flights)
