import requests

base_url = "https://pokeapi.co/api/v2/"

print("Hello, welcome to the Pokedex API!\nThis program will allow you to retrieve information about any Pokemon by name."
      "\nJust like pokedex in pokemon games, you can get details such as height, weight, and types of the Pokemon."
      "\nENJOYYY.....")

def get_pokemon_info(name):
    url = f"{base_url}/pokemon/{name}"
    response = requests.get(url)
    print(response)

    if response.status_code == 200:
        pokemon_data = response.json()
        return pokemon_data
    else:
        print(f"Failed to retrieve data {response.status_code}")
        return None
pokemon_name= input("Enter the name of the Pokemon you want to search for: ").lower()
if not pokemon_name:
    print("Please enter a valid Pokemon name.")
else:
    get_pokemon_info = get_pokemon_info(pokemon_name)

if get_pokemon_info:
    print(f"Name: {get_pokemon_info['name']}")
    print(f"Height: {get_pokemon_info['height']}")
    print(f"Weight: {get_pokemon_info['weight']}")
    print("Types:")
    for type_info in get_pokemon_info['types']:
        print(f"- {type_info['type']['name']}")
    print(f"Abilities:")
    for ability_info in get_pokemon_info['abilities']:
        print(f"- {ability_info['ability']['name']}")
    print(f"Stats:")
    for stat_info in get_pokemon_info['stats']:
        print(f"- {stat_info['stat']['name']}: {stat_info['base_stat']}")
else:
    print("Could not retrieve Pokemon information.")