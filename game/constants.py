# Window settings
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768
FPS = 60
TITLE = "Galactic Conquest"

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
DARK_BLUE = (0, 0, 50)
GRID_COLOR = (50, 50, 50)

# Galaxy map settings
GALAXY_GRID_SIZE = 64
GALAXY_GRID_WIDTH = 20
GALAXY_GRID_HEIGHT = 15
GALAXY_VIEW_PADDING = 50

# Galaxy settings
GALAXY_SIZE = 1000  # Huge galaxy to fit very distant systems
GRID_SIZE = 40    # Size of each grid cell in pixels
GRID_VIEW_PADDING = 20  # Padding around the grid view

# Planet grid settings
PLANET_GRID_SIZE = 32
PLANET_GRID_WIDTH = 5
PLANET_GRID_HEIGHT = 5

# Resource types
RESOURCE_TYPES = {
    'MINERALS': 'Minerals',
    'FOOD': 'Food',
    'ENERGY': 'Energy',
    'SCIENCE': 'Science'
}

# Building types
BUILDING_TYPES = {
    'POWER_PLANT': 'Power Plant',
    'RESEARCH_LAB': 'Research Lab',
    'FARM': 'Farm',
    'DEFENSE_TURRET': 'Defense Turret',
    'MINING_STATION': 'Mining Station',
    'SOLAR_ARRAY': 'Solar Array',
    'RESEARCH_STATION': 'Research Station',
    'DEFENSE_PLATFORM': 'Defense Platform',
    'SHIPYARD': 'Shipyard'
}

# Building colors
BUILDING_COLORS = {
    'Power Plant': (255, 255, 0),        # Yellow
    'Research Lab': (128, 0, 128),       # Purple
    'Farm': (0, 255, 0),                 # Green
    'Defense Turret': (255, 0, 0),       # Red
    'Mining Station': (139, 69, 19),     # Brown
    'Solar Array': (255, 215, 0),        # Gold
    'Research Station': (0, 191, 255),   # Deep Sky Blue
    'Defense Platform': (220, 20, 60),   # Crimson
    'Shipyard': (100, 149, 237)          # Cornflower Blue - much brighter
}

# Planet types
PLANET_TYPES = {
    'ROCKY': 'Rocky',
    'GAS_GIANT': 'Gas Giant',
    'ICE': 'Ice',
    'DESERT': 'Desert',
    'TERRAN': 'Terran',
    'OCEAN': 'Ocean',
    'VOLCANIC': 'Volcanic',
    'TOXIC': 'Toxic'
}

# Nebulae types
NEBULA_TYPES = {
    'EMISSION': 'Emission Nebula',      # Red/pink - star-forming regions
    'REFLECTION': 'Reflection Nebula',  # Blue - reflects starlight
    'PLANETARY': 'Planetary Nebula',    # Green/cyan - dying star remnants
    'DARK': 'Dark Nebula',             # Purple/black - dense dust clouds
    'SUPERNOVA': 'Supernova Remnant'   # Orange/yellow - stellar explosion remnants
}

# Nebula colors (with transparency for cloudy effect)
NEBULA_COLORS = {
    'EMISSION': (255, 100, 150, 80),      # Pink/red with transparency
    'REFLECTION': (100, 150, 255, 80),    # Blue with transparency
    'PLANETARY': (100, 255, 200, 80),     # Cyan/green with transparency
    'DARK': (80, 50, 120, 100),          # Dark purple with more opacity
    'SUPERNOVA': (255, 200, 100, 90)     # Orange/yellow with transparency
}

# Nebula effects on gameplay
NEBULA_EFFECTS = {
    'EMISSION': {'science_bonus': 2, 'movement_penalty': 0},      # Science bonus from stellar formation
    'REFLECTION': {'energy_bonus': 1, 'movement_penalty': 1},     # Energy from reflected light, slight movement penalty
    'PLANETARY': {'science_bonus': 3, 'movement_penalty': 1},     # High science from exotic matter
    'DARK': {'stealth_bonus': True, 'movement_penalty': 2},       # Ships harder to detect, significant movement penalty
    'SUPERNOVA': {'energy_bonus': 3, 'damage_risk': True}        # High energy but potential ship damage
}

# Building costs
BUILDING_COSTS = {
    BUILDING_TYPES['POWER_PLANT']: {
        RESOURCE_TYPES['MINERALS']: 75,
        RESOURCE_TYPES['ENERGY']: 25
    },
    BUILDING_TYPES['RESEARCH_LAB']: {
        RESOURCE_TYPES['MINERALS']: 100,
        RESOURCE_TYPES['ENERGY']: 50,
        RESOURCE_TYPES['SCIENCE']: 25
    },
    BUILDING_TYPES['FARM']: {
        RESOURCE_TYPES['MINERALS']: 50,
        RESOURCE_TYPES['ENERGY']: 25
    },
    BUILDING_TYPES['DEFENSE_TURRET']: {
        RESOURCE_TYPES['MINERALS']: 75,
        RESOURCE_TYPES['ENERGY']: 50
    },
    BUILDING_TYPES['MINING_STATION']: {
        RESOURCE_TYPES['MINERALS']: 100,
        RESOURCE_TYPES['ENERGY']: 50
    },
    BUILDING_TYPES['SOLAR_ARRAY']: {
        RESOURCE_TYPES['MINERALS']: 80,
        RESOURCE_TYPES['ENERGY']: 30
    },
    BUILDING_TYPES['RESEARCH_STATION']: {
        RESOURCE_TYPES['MINERALS']: 120,
        RESOURCE_TYPES['ENERGY']: 60,
        RESOURCE_TYPES['SCIENCE']: 40
    },
    BUILDING_TYPES['DEFENSE_PLATFORM']: {
        RESOURCE_TYPES['MINERALS']: 150,
        RESOURCE_TYPES['ENERGY']: 100
    },
    BUILDING_TYPES['SHIPYARD']: {
        RESOURCE_TYPES['MINERALS']: 200,
        RESOURCE_TYPES['ENERGY']: 150,
        RESOURCE_TYPES['SCIENCE']: 75
    },
}

# Building resource generation per turn
BUILDING_PRODUCTION = {
    'Power Plant': {
        'Energy': 8
    },
    'Research Lab': {
        'Science': 5
    },
    'Farm': {
        'Food': 6
    },
    'Defense Turret': {
        # No resource generation, defensive building
    },
    'Mining Station': {
        'Minerals': 5
    },
    'Solar Array': {
        'Energy': 10
    },
    'Research Station': {
        'Science': 8
    },
    'Defense Platform': {
        # No resource generation, defensive building
    },
    'Shipyard': {
        'Minerals': 2,
        'Energy': 2
    },
}

# Planet-specific building restrictions
PLANET_BUILDING_RESTRICTIONS = {
    'ROCKY': ['Power Plant', 'Defense Turret', 'Mining Station', 'Defense Platform'],  # Good for mining and defense
    'GAS_GIANT': ['Research Lab', 'Power Plant', 'Research Station'],  # Energy and research from gas
    'ICE': ['Research Lab', 'Farm', 'Research Station'],  # Water for farms, cold for research
    'DESERT': ['Power Plant', 'Defense Turret', 'Solar Array'],  # Solar power, harsh conditions for defense
    'TERRAN': ['Farm', 'Research Lab', 'Defense Turret', 'Shipyard'],  # Earth-like, most versatile
    'OCEAN': ['Farm', 'Research Lab', 'Research Station'],  # Water-rich, good for farms and research
    'VOLCANIC': ['Power Plant', 'Mining Station', 'Defense Platform', 'Solar Array'],  # High energy and minerals
    'TOXIC': ['Research Lab', 'Defense Platform', 'Research Station'],  # Harsh environment, limited options
}

# Orbital types
ORBITAL_TYPES = {
    'NEBULA_RESEARCH_STATION': 'Nebula Research Station',
    'ORBITAL_SHIPYARD': 'Orbital Shipyard',
    'DEEP_SPACE_FORTRESS': 'Deep Space Fortress'
}

# Orbital costs
ORBITAL_COSTS = {
    'Nebula Research Station': {
        RESOURCE_TYPES['MINERALS']: 300,
        RESOURCE_TYPES['ENERGY']: 200,
        RESOURCE_TYPES['SCIENCE']: 150
    },
    'Orbital Shipyard': {
        RESOURCE_TYPES['MINERALS']: 400,
        RESOURCE_TYPES['ENERGY']: 300,
        RESOURCE_TYPES['SCIENCE']: 100
    },
    'Deep Space Fortress': {
        RESOURCE_TYPES['MINERALS']: 500,
        RESOURCE_TYPES['ENERGY']: 400,
        RESOURCE_TYPES['SCIENCE']: 50
    }
}

# Orbital resource production per turn
ORBITAL_PRODUCTION = {
    'Nebula Research Station': {
        'Science': 15
    },
    'Orbital Shipyard': {
        'Minerals': 8,
        'Energy': 5
    },
    'Deep Space Fortress': {
        'Energy': 10
    }
}

# Orbital colors
ORBITAL_COLORS = {
    'Nebula Research Station': (0, 255, 255),    # Cyan
    'Orbital Shipyard': (255, 165, 0),          # Orange
    'Deep Space Fortress': (255, 0, 0)          # Red
}

# Orbital menu labels
BUILD_MENU_TABS = [
    'Buildings',
    'Orbitals'
]

# Ship types available for construction
SHIP_TYPES = {
    'CORVETTE': 'Corvette',
    'FRIGATE': 'Frigate', 
    'DESTROYER': 'Destroyer',
    'CRUISER': 'Cruiser',
    'BATTLESHIP': 'Battleship',
    'CARRIER': 'Carrier',
    'FIGHTER': 'Fighter',
    'BOMBER': 'Bomber',
    'SCOUT': 'Scout',
    'TRANSPORT': 'Transport',
    'BUILDER': 'Builder',
    'COLONIZER': 'Colonizer'
}

# Ship construction costs
SHIP_COSTS = {
    'Corvette': {
        'Minerals': 80,
        'Energy': 40
    },
    'Frigate': {
        'Minerals': 120,
        'Energy': 60
    },
    'Destroyer': {
        'Minerals': 180,
        'Energy': 90,
        'Science': 30
    },
    'Cruiser': {
        'Minerals': 250,
        'Energy': 120,
        'Science': 50
    },
    'Battleship': {
        'Minerals': 400,
        'Energy': 200,
        'Science': 100
    },
    'Carrier': {
        'Minerals': 350,
        'Energy': 180,
        'Science': 80
    },
    'Fighter': {
        'Minerals': 40,
        'Energy': 20
    },
    'Bomber': {
        'Minerals': 60,
        'Energy': 30
    },
    'Scout': {
        'Minerals': 50,
        'Energy': 25
    },
    'Transport': {
        'Minerals': 100,
        'Energy': 50
    },
    'Builder': {
        'Minerals': 120,
        'Energy': 60,
        'Science': 20
    },
    'Colonizer': {
        'Minerals': 200,
        'Energy': 100,
        'Science': 40,
        'Food': 50
    }
}

# Ship construction time (in turns)
SHIP_BUILD_TIME = {
    'Corvette': 2,
    'Frigate': 3,
    'Destroyer': 4,
    'Cruiser': 5,
    'Battleship': 8,
    'Carrier': 7,
    'Fighter': 1,
    'Bomber': 1,
    'Scout': 1,
    'Transport': 2,
    'Builder': 3,
    'Colonizer': 4
}

 