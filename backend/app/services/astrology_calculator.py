"""
Serviço para cálculos astrológicos usando PyEphem
"""
import ephem
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from geopy.geocoders import Nominatim
import math
from app.models.schemas import PlanetPosition, House, Aspect, BigThree, ElementData, ModalityData, ChartRuler

# Planet mappings for PyEphem
PLANETS_EPHEM = {
    'Sol': ephem.Sun,
    'Lua': ephem.Moon,
    'Mercúrio': ephem.Mercury,
    'Vênus': ephem.Venus,
    'Marte': ephem.Mars,
    'Júpiter': ephem.Jupiter,
    'Saturno': ephem.Saturn,
    'Urano': ephem.Uranus,
    'Netuno': ephem.Neptune,
    'Plutão': ephem.Pluto
}

# Signs (Zodiac)
SIGNS = [
    'Áries', 'Touro', 'Gêmeos', 'Câncer', 'Leão', 'Virgem',
    'Libra', 'Escorpião', 'Sagitário', 'Capricórnio', 'Aquário', 'Peixes'
]

# Elements mapping
ELEMENT_MAPPING = {
    'Áries': 'Fogo', 'Leão': 'Fogo', 'Sagitário': 'Fogo',
    'Touro': 'Terra', 'Virgem': 'Terra', 'Capricórnio': 'Terra',
    'Gêmeos': 'Ar', 'Libra': 'Ar', 'Aquário': 'Ar',
    'Câncer': 'Água', 'Escorpião': 'Água', 'Peixes': 'Água'
}

# Modalities mapping
MODALITY_MAPPING = {
    'Áries': 'Cardinal', 'Câncer': 'Cardinal', 'Libra': 'Cardinal', 'Capricórnio': 'Cardinal',
    'Touro': 'Fixo', 'Leão': 'Fixo', 'Escorpião': 'Fixo', 'Aquário': 'Fixo',
    'Gêmeos': 'Mutável', 'Virgem': 'Mutável', 'Sagitário': 'Mutável', 'Peixes': 'Mutável'
}

# Chart ruler mapping (Ascendant -> Ruler Planet)
CHART_RULER_MAPPING = {
    'Áries': 'Marte',
    'Touro': 'Vênus',
    'Gêmeos': 'Mercúrio',
    'Câncer': 'Lua',
    'Leão': 'Sol',
    'Virgem': 'Mercúrio',
    'Libra': 'Vênus',
    'Escorpião': 'Marte',  # Traditional: Mars, Modern: Pluto
    'Sagitário': 'Júpiter',
    'Capricórnio': 'Saturno',
    'Aquário': 'Saturno',  # Traditional: Saturn, Modern: Uranus
    'Peixes': 'Júpiter'  # Traditional: Jupiter, Modern: Neptune
}

# Aspect orbs (degrees of tolerance)
ASPECT_ORBS = {
    'conjunction': 8,
    'opposition': 8,
    'square': 7,
    'trine': 6,
    'sextile': 5
}

# Aspect angles
ASPECT_ANGLES = {
    'conjunction': 0,
    'opposition': 180,
    'square': 90,
    'trine': 120,
    'sextile': 60
}

class AstrologyCalculator:
    def __init__(self):
        pass
        
    def get_coordinates(self, place: str) -> Tuple[float, float]:
        """Get latitude and longitude from place name"""
        geolocator = Nominatim(user_agent="astrology_app")
        try:
            location = geolocator.geocode(place, timeout=10)
            if location:
                return location.latitude, location.longitude
            else:
                # Default to São Paulo if not found
                return -23.5505, -46.6333
        except Exception:
            return -23.5505, -46.6333  # São Paulo default
    
    def degree_to_sign(self, degree: float) -> Tuple[str, float]:
        """Convert absolute degree to sign and degree within sign"""
        # Normalize to 0-360
        degree = degree % 360
        sign_index = int(degree / 30)
        degree_in_sign = degree % 30
        return SIGNS[sign_index % 12], degree_in_sign
    
    def calculate_planet_position(self, observer: ephem.Observer, planet_class) -> Dict:
        """Calculate planet position using correct geocentric ecliptic coordinates"""
        try:
            planet = planet_class()
            planet.compute(observer)
            
            # Convert equatorial coordinates (RA/Dec) to ecliptic longitude
            # This is the correct way to get zodiac positions
            ra = float(planet.ra)  # Right ascension in radians
            dec = float(planet.dec)  # Declination in radians
            
            # Calculate ecliptic longitude from equatorial coordinates
            # Using the obliquity of the ecliptic
            obliquity = math.radians(23.4367)  # Mean obliquity for epoch J2000.0
            
            # Convert RA/Dec to ecliptic longitude/latitude
            sin_lon = (math.sin(ra) * math.cos(obliquity) + 
                      math.tan(dec) * math.sin(obliquity))
            cos_lon = math.cos(ra)
            
            longitude_rad = math.atan2(sin_lon, cos_lon)
            longitude = math.degrees(longitude_rad) % 360
            
            sign, degree_in_sign = self.degree_to_sign(longitude)
            
            return {
                'longitude': longitude,
                'sign': sign,
                'degree': degree_in_sign,
                'speed': 0.0
            }
        except Exception as e:
            # Fallback calculation
            print(f"Warning: Error calculating planet position for {planet_class}: {e}")
            return {
                'longitude': 0.0,
                'sign': 'Áries',
                'degree': 0.0,
                'speed': 0.0
            }
    
    def calculate_ascendant(self, observer: ephem.Observer) -> Tuple[str, float]:
        """Calculate the ascendant (rising sign) using Local Sidereal Time"""
        try:
            # Get local sidereal time in radians
            lst_rad = observer.sidereal_time()
            lat_rad = float(observer.lat)
            
            # Calculate ascendant using the standard formula
            # ASC longitude = arctan2(cos(LST), -sin(LST) * cos(obliquity) - tan(lat) * sin(obliquity))
            obliquity = math.radians(23.4367)  # Mean obliquity of ecliptic for J2000.0
            
            # Calculate ascendant ecliptic longitude
            numerator = math.cos(lst_rad)
            denominator = (-math.sin(lst_rad) * math.cos(obliquity) - 
                          math.tan(lat_rad) * math.sin(obliquity))
            
            asc_rad = math.atan2(numerator, denominator)
            asc_degree = math.degrees(asc_rad)
            
            # Ensure positive angle (0-360)
            if asc_degree < 0:
                asc_degree += 360
            
            asc_sign, asc_degree_in_sign = self.degree_to_sign(asc_degree)
            
            return asc_sign, asc_degree
            
        except Exception as e:
            print(f"Error calculating ascendant: {e}")
            # Simple fallback: use LST directly (less accurate)
            lst_rad = observer.sidereal_time()
            asc_degree = (math.degrees(lst_rad) * 15) % 360  # Convert hours to degrees
            asc_sign, asc_degree_in_sign = self.degree_to_sign(asc_degree)
            return asc_sign, asc_degree

    def calculate_houses_placidus(self, observer: ephem.Observer) -> List[Dict]:
        """Calculate house cusps using Equal House system"""
        # Calculate ascendant first
        asc_sign, asc_degree = self.calculate_ascendant(observer)
        
        # Create houses using Equal House system (ascendant = house 1 cusp)
        houses = []
        for i in range(12):
            cusp_degree = (asc_degree + (i * 30)) % 360
            sign, cusp_degree_in_sign = self.degree_to_sign(cusp_degree)
            houses.append({
                'number': i + 1,
                'cusp_degree': cusp_degree,
                'cusp_sign': sign,
                'cusp_degree_in_sign': cusp_degree_in_sign
            })
        
        return houses, asc_sign, asc_degree
    
    def get_house_for_planet(self, planet_longitude: float, houses: List[Dict]) -> int:
        """Determine which house a planet is in"""
        for i, house in enumerate(houses):
            next_house_idx = (i + 1) % 12
            next_house = houses[next_house_idx]
            
            cusp1 = house['cusp_degree']
            cusp2 = next_house['cusp_degree']
            
            # Handle wrapping around 360 degrees
            if cusp2 < cusp1:
                cusp2 += 360
            
            # Normalize planet longitude
            planet_norm = planet_longitude
            if planet_norm < cusp1:
                planet_norm += 360
            
            if cusp1 <= planet_norm < cusp2:
                return house['number']
        
        # Default to house 1 if not found
        return 1
    
    def calculate_aspect(self, planet1_longitude: float, planet2_longitude: float) -> Optional[Dict]:
        """Calculate aspect between two planets"""
        angle = abs(planet1_longitude - planet2_longitude)
        if angle > 180:
            angle = 360 - angle
        
        for aspect_name, aspect_angle in ASPECT_ANGLES.items():
            orb = abs(angle - aspect_angle)
            max_orb = ASPECT_ORBS[aspect_name]
            
            if orb <= max_orb:
                is_positive = aspect_name in ['trine', 'sextile', 'conjunction']
                return {
                    'type': aspect_name,
                    'orb': orb,
                    'is_positive': is_positive
                }
        
        return None
    
    def calculate_chart(self, birth_date: str, birth_time: str, birth_place: str) -> Dict:
        """Calculate complete birth chart"""
        # Parse inputs
        dt_str = f"{birth_date} {birth_time}"
        dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
        
        # Get coordinates
        lat, lon = self.get_coordinates(birth_place)
        
        # Create observer
        observer = ephem.Observer()
        observer.lat = str(lat)
        observer.lon = str(lon)
        observer.date = dt.strftime("%Y/%m/%d %H:%M:%S")
        observer.epoch = dt.strftime("%Y/%m/%d %H:%M:%S")
        
        # Calculate houses and ascendant
        houses_data, ascendant_sign, ascendant_degree = self.calculate_houses_placidus(observer)
        
        # Calculate planet positions
        planets_data = []
        planet_longitudes = {}
        
        for planet_name, planet_class in PLANETS_EPHEM.items():
            pos = self.calculate_planet_position(observer, planet_class)
            house = self.get_house_for_planet(pos['longitude'], houses_data)
            
            planet_longitudes[planet_name] = pos['longitude']
            
            planets_data.append({
                'planet': planet_name,
                'sign': pos['sign'],
                'house': house,
                'degree': math.floor(pos['degree']),
                'minutes': int((pos['degree'] % 1) * 60),
                'longitude': pos['longitude']
            })
        
        # Get Big Three
        sun_pos = next(p for p in planets_data if p['planet'] == 'Sol')
        moon_pos = next(p for p in planets_data if p['planet'] == 'Lua')
        
        big_three = {
            'sun': sun_pos['sign'],
            'moon': moon_pos['sign'],
            'ascendant': ascendant_sign
        }
        
        # Calculate aspects
        aspects = []
        planet_names_list = list(PLANETS_EPHEM.keys())
        for i, planet1 in enumerate(planet_names_list):
            for planet2 in planet_names_list[i+1:]:
                if planet1 in planet_longitudes and planet2 in planet_longitudes:
                    aspect = self.calculate_aspect(
                        planet_longitudes[planet1],
                        planet_longitudes[planet2]
                    )
                    if aspect:
                        aspects.append({
                            'planet1': planet1,
                            'planet2': planet2,
                            **aspect
                        })
        
        # Calculate elements and modalities
        elements_count = {'Fogo': 0, 'Terra': 0, 'Ar': 0, 'Água': 0}
        modalities_count = {'Cardinal': 0, 'Fixo': 0, 'Mutável': 0}
        
        for planet in planets_data:
            sign = planet['sign']
            if sign in ELEMENT_MAPPING:
                elements_count[ELEMENT_MAPPING[sign]] += 1
            if sign in MODALITY_MAPPING:
                modalities_count[MODALITY_MAPPING[sign]] += 1
        
        # Add ascendant
        if ascendant_sign in ELEMENT_MAPPING:
            elements_count[ELEMENT_MAPPING[ascendant_sign]] += 0.5
        if ascendant_sign in MODALITY_MAPPING:
            modalities_count[MODALITY_MAPPING[ascendant_sign]] += 0.5
        
        total = sum(elements_count.values())
        elements = [
            ElementData(
                name=name,
                percentage=round((count / total) * 100, 1) if total > 0 else 0,
                color=self._get_element_color(name)
            )
            for name, count in elements_count.items()
        ]
        
        total_mod = sum(modalities_count.values())
        modalities = [
            ModalityData(
                name=name,
                percentage=round((count / total_mod) * 100, 1) if total_mod > 0 else 0,
                color=self._get_modality_color(name)
            )
            for name, count in modalities_count.items()
        ]
        
        # Calculate chart ruler
        ruler_planet_name = CHART_RULER_MAPPING.get(ascendant_sign, 'Sol')
        ruler_planet = next((p for p in planets_data if p['planet'] == ruler_planet_name), None)
        
        chart_ruler = ChartRuler(
            ascendant=ascendant_sign,
            ruler=ruler_planet_name,
            ruler_sign=ruler_planet['sign'] if ruler_planet else 'Áries',
            ruler_house=ruler_planet['house'] if ruler_planet else 1
        )
        
        # Build houses with planets
        houses_with_planets = []
        for house_data in houses_data:
            planets_in_house = [
                p['planet'] for p in planets_data
                if p['house'] == house_data['number']
            ]
            houses_with_planets.append(
                House(
                    number=house_data['number'],
                    cusp_sign=house_data['cusp_sign'],
                    cusp_degree=house_data['cusp_degree_in_sign'],
                    planets_in_house=planets_in_house
                )
            )
        
        return {
            'big_three': big_three,
            'planets': planets_data,
            'houses': houses_with_planets,
            'aspects': aspects,
            'elements': elements,
            'modalities': modalities,
            'chart_ruler': chart_ruler
        }
    
    def _get_element_color(self, element: str) -> str:
        colors = {
            'Fogo': '#E8B95A',
            'Terra': '#8B7355',
            'Ar': '#A0AEC0',
            'Água': '#4A90E2'
        }
        return colors.get(element, '#E8B95A')
    
    def _get_modality_color(self, modality: str) -> str:
        colors = {
            'Cardinal': '#E8B95A',
            'Fixo': '#8B7355',
            'Mutável': '#A0AEC0'
        }
        return colors.get(modality, '#E8B95A')
