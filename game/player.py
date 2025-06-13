from .constants import RESOURCE_TYPES

class Player:
    def __init__(self, name):
        self.name = name
        self.resources = {
            'Minerals': 200,  # Starting resources
            'Energy': 150,
            'Science': 50,
            'Food': 100
        }
        self.planets = []
        self.ships = []
        self.technologies = set()
        self.fleet = []

    def add_resource(self, resource, amount):
        if resource in self.resources:
            self.resources[resource] += amount

    def get_resource(self, resource):
        return self.resources.get(resource, 0)

    def spend_resource(self, resource_type, amount):
        if resource_type in self.resources and self.resources[resource_type] >= amount:
            self.resources[resource_type] -= amount
            return True
        return False

    def add_planet(self, planet):
        self.planets.append(planet)
        planet.owner = self

    def remove_planet(self, planet):
        if planet in self.planets:
            self.planets.remove(planet)
            planet.owner = None

    def add_technology(self, tech):
        self.technologies.add(tech)

    def has_technology(self, tech):
        return tech in self.technologies

    def add_ship(self, ship):
        self.ships.append(ship)

    def remove_ship(self, ship):
        if ship in self.ships:
            self.ships.remove(ship)

    def get_total_resources(self):
        return sum(self.resources.values())

    def can_afford(self, costs):
        for resource_type, amount in costs.items():
            if self.resources.get(resource_type, 0) < amount:
                return False
        return True 