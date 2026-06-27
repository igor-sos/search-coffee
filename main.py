import json
import requests
import folium
from decouple import config
from geopy import distance


USER_EMAIL = config("USER_EMAIL")


def fetch_coordinates(address):
    """Получает координаты через Nominatim (OpenStreetMap)"""
    base_url = "https://nominatim.openstreetmap.org/search"

    try:
        response = requests.get(
            base_url,
            params={
                "q": address,
                "format": "json",
                "limit": 1,
                "addressdetails": 1,
                "accept-language": "ru"
            },
            headers={
                "User-Agent": f"CoffeeSearchApp/1.0 ({USER_EMAIL})"
            },
            timeout=10
        )

        if response.status_code != 200:
            print("Ошибка от сервера:", response.text)
            return None

        data = response.json()

        if not data:
            print(f"Адрес не найден: {address}")
            return None

        place = data[0]
        lat = float(place['lat'])
        lon = float(place['lon'])

        return lat, lon

    except Exception as e:
        print(f"Ошибка: {e}")
        return None


def load_coffee_data(file_path="coffee.json"):
    with open(file_path, "r", encoding="CP1251") as coffee_file:
        coffee_contents = coffee_file.read()
        coffee_list = json.loads(coffee_contents)

    return coffee_list


def coffee_info(coordinate, coffee_list):
    new_list_caffee = []

    for coffee in coffee_list:
        coffee_longitude, coffee_latitude = coffee["geoData"]["coordinates"]

        distance_km = distance.distance(
            (coffee_latitude, coffee_longitude),
            coordinate
        ).km

        new_list_caffee.append(
            {
                'title': coffee.get("Name"),
                'distance': distance_km,
                'longitude': coffee_longitude,
                'latitude': coffee_latitude,
            }
        )

    return new_list_caffee


def main():
    coordinate = fetch_coordinates(input('Где вы находитесь? '))
    coffee_list = load_coffee_data()

    five_coffee = sorted(
        coffee_info(coordinate, coffee_list),
        key=lambda x: x['distance']
    )[:5]

    m = folium.Map(location=coordinate, zoom_start=12)

    folium.Marker(
        location=coordinate,
        tooltip="Вы здесь",
        popup="Ваше местоположение",
        icon=folium.Icon(color="blue", icon="user"),
    ).add_to(m)

    for coffee in five_coffee:
        folium.Marker(
            location=[coffee['latitude'], coffee['longitude']],
            tooltip=coffee['title'],
            popup=coffee['title'],
            icon=folium.Icon(color="green"),
        ).add_to(m)

    m.save("index.html")


if __name__ == '__main__':
    main()
