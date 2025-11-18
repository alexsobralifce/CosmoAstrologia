"""
Serviço para cálculos de trânsitos astrológicos
"""
import ephem
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from app.services.astrology_calculator import AstrologyCalculator, SIGNS

class TransitService:
    def __init__(self):
        self.calculator = AstrologyCalculator()
    
    def get_daily_transits(self, natal_chart: Dict, target_date: Optional[datetime] = None) -> Dict:
        """Get daily transits for a given date"""
        if target_date is None:
            target_date = datetime.now()
        
        # Create observer for current date
        observer = ephem.Observer()
        observer.date = target_date.strftime("%Y/%m/%d %H:%M:%S")
        observer.lat = "0"  # Equator for general calculations
        observer.lon = "0"
        
        # Calculate Moon's current position
        moon = ephem.Moon()
        moon.compute(observer)
        
        # Get Moon longitude
        moon_longitude_rad = float(moon.ra) + float(moon.hlon)
        moon_longitude = self.calculator.degree_to_sign(math.degrees(moon_longitude_rad) % 360)[0]
        moon_sign = self.calculator.degree_to_sign(math.degrees(moon_longitude_rad) % 360)[0]
        moon_longitude_deg = math.degrees(moon_longitude_rad) % 360
        
        # Determine which house Moon transits
        natal_houses = natal_chart.get('houses', [])
        moon_house = self.calculator.get_house_for_planet(
            moon_longitude_deg,
            [{'cusp_degree': h.get('cusp_degree', i * 30) if isinstance(h, dict) else 0} for i, h in enumerate(natal_houses)]
        ) if natal_houses else 1
        
        # Check if Mercury is retrograde
        mercury = ephem.Mercury()
        mercury.compute(observer)
        mercury_speed = float(mercury.hlon) * 3600 * 24 if hasattr(mercury, 'hlon') else 0
        is_mercury_retrograde = mercury_speed < 0
        
        # Check if Moon is void of course (simplified)
        is_moon_void_of_course = False
        void_ends_at = None
        
        # Generate moon advice based on house
        moon_advice = self._get_moon_advice(moon_house)
        
        return {
            "moon_sign": moon_sign,
            "moon_house": moon_house,
            "moon_advice": moon_advice,
            "is_mercury_retrograde": is_mercury_retrograde,
            "is_moon_void_of_course": is_moon_void_of_course,
            "void_ends_at": void_ends_at or "16:30"
        }
    
    def get_future_transits(self, natal_chart: Dict, months_ahead: int = 24) -> List[Dict]:
        """Get future important transits"""
        # Get birth date from chart
        birth_data = natal_chart.get('birth_data', {})
        if not birth_data:
            return []
        
        birth_date_str = birth_data.get('birth_date', '')
        birth_time_str = birth_data.get('birth_time', '00:00')
        
        try:
            birth_dt = datetime.strptime(f"{birth_date_str} {birth_time_str}", "%Y-%m-%d %H:%M")
        except:
            return []
        
        transits = []
        current_date = datetime.now()
        
        # Get natal positions (simplified - would need to recalculate from birth data)
        natal_planets = {}
        if 'planets' in natal_chart:
            for planet in natal_chart['planets']:
                if isinstance(planet, dict):
                    natal_planets[planet.get('planet', '')] = planet.get('longitude', 0)
                elif hasattr(planet, 'longitude'):
                    natal_planets[planet.planet] = planet.longitude
        
        # Check Jupiter transit to natal Sun (conjunction)
        sun_longitude = natal_planets.get('Sol', 0)
        jupiter_transit = self._check_transit_to_position(
            ephem.Jupiter, sun_longitude, current_date, months_ahead, "conjunction"
        )
        if jupiter_transit:
            transits.append({
                "type": "jupiter",
                "title": f"Expansão e Sorte: Júpiter em conjunção com seu Sol",
                "planet": "Júpiter",
                "timeframe": jupiter_transit['timeframe'],
                "description": jupiter_transit['description'],
                "is_active": jupiter_transit['is_active']
            })
        
        # Check Saturn return
        saturn_longitude = natal_planets.get('Saturno', 0)
        saturn_return = self._check_saturn_return(saturn_longitude, birth_dt, current_date, months_ahead)
        if saturn_return:
            transits.append({
                "type": "saturn-return",
                "title": "Marco de Amadurecimento: Seu Retorno de Saturno",
                "planet": "Saturno",
                "timeframe": saturn_return['timeframe'],
                "description": saturn_return['description'],
                "is_active": saturn_return['is_active']
            })
        
        # Check Uranus square to Sun
        if 'Sol' in natal_planets:
            uranus_transit = self._check_transit_to_position(
                ephem.Uranus, sun_longitude, current_date, months_ahead, "square"
            )
            if uranus_transit:
                transits.append({
                    "type": "uranus",
                    "title": "Mudança e Inovação: Urano em quadratura com seu Sol",
                    "planet": "Urano",
                    "timeframe": uranus_transit['timeframe'],
                    "description": uranus_transit['description'],
                    "is_active": uranus_transit['is_active']
                })
        
        return transits
    
    def _check_transit_to_position(
        self, 
        planet_class, 
        target_longitude: float, 
        start_date: datetime, 
        months_ahead: int,
        aspect_type: str
    ) -> Optional[Dict]:
        """Check if a planet will transit to a target position"""
        target_angle = {
            "conjunction": 0,
            "opposition": 180,
            "square": 90,
            "trine": 120
        }.get(aspect_type, 0)
        
        end_date = start_date + timedelta(days=months_ahead * 30)
        check_date = start_date
        
        while check_date <= end_date:
            try:
                observer = ephem.Observer()
                observer.date = check_date.strftime("%Y/%m/%d %H:%M:%S")
                observer.lat = "0"
                observer.lon = "0"
                
                planet = planet_class()
                planet.compute(observer)
                
                planet_longitude_rad = float(planet.ra) + float(planet.hlon)
                planet_longitude = math.degrees(planet_longitude_rad) % 360
                
                angle = abs(planet_longitude - target_longitude)
                if angle > 180:
                    angle = 360 - angle
                
                # Check if within orb
                if abs(angle - target_angle) <= 5:  # 5 degree orb
                    is_active = check_date <= datetime.now() <= check_date + timedelta(days=30)
                    timeframe = "Ativo agora" if is_active else f"Próximos {months_ahead} meses"
                    
                    return {
                        "timeframe": timeframe,
                        "description": f"Este trânsito trará mudanças significativas. Prepare-se para transformações importantes.",
                        "is_active": is_active
                    }
            except:
                pass
            
            check_date += timedelta(days=7)  # Check weekly
        
        return None
    
    def _check_saturn_return(
        self, 
        saturn_longitude: float, 
        birth_date: datetime, 
        current_date: datetime,
        months_ahead: int
    ) -> Optional[Dict]:
        """Check for Saturn return (around age 29 and 58)"""
        import math
        age_years = (current_date - birth_date).days / 365.25
        
        # Saturn return happens around age 29-30 and 58-59
        if 27 <= age_years <= 31 or 56 <= age_years <= 60:
            end_date = current_date + timedelta(days=months_ahead * 30)
            check_date = current_date
            
            while check_date <= end_date:
                try:
                    observer = ephem.Observer()
                    observer.date = check_date.strftime("%Y/%m/%d %H:%M:%S")
                    observer.lat = "0"
                    observer.lon = "0"
                    
                    saturn = ephem.Saturn()
                    saturn.compute(observer)
                    
                    saturn_longitude_rad = float(saturn.ra) + float(saturn.hlon)
                    saturn_current = math.degrees(saturn_longitude_rad) % 360
                    
                    angle = abs(saturn_current - saturn_longitude)
                    if angle > 180:
                        angle = 360 - angle
                    
                    if angle <= 5:  # Within 5 degrees
                        is_active = check_date <= datetime.now() <= check_date + timedelta(days=90)
                        timeframe = "Ativo agora" if is_active else "Próximos 1-2 anos"
                        
                        return {
                            "timeframe": timeframe,
                            "description": "Seu Retorno de Saturno é um período de grandes lições de vida e amadurecimento. Você será recompensado por estruturar suas responsabilidades e levar sua vida a sério.",
                            "is_active": is_active
                        }
                except:
                    pass
                
                check_date += timedelta(days=7)
        
        return None
    
    def _get_moon_advice(self, house: int) -> str:
        """Get advice based on Moon's transit house"""
        import math
        advice_map = {
            1: "Hoje, sua segurança emocional vem de focar em si mesmo. É um bom dia para novos começos e cuidar da sua aparência.",
            2: "Hoje, sua segurança emocional vem de estabilidade financeira. Foque em administrar recursos e valorizar o que já possui.",
            3: "Hoje, sua segurança emocional vem de comunicação e aprendizado. É um bom dia para conversas, estudos e conectar-se com irmãos.",
            4: "Hoje, sua segurança emocional vem do lar e família. Fique perto de quem ama e cuide do seu espaço pessoal.",
            5: "Hoje, sua segurança emocional vem de criatividade e diversão. É um bom dia para hobbies, romance e expressão pessoal.",
            6: "Hoje, sua segurança emocional vem de rotina e produtividade. Organize suas tarefas, cuide da saúde e seja útil.",
            7: "Hoje, sua segurança emocional vem de parcerias. É um bom dia para colaborações, negociações e tempo com parceiros.",
            8: "Hoje, sua segurança emocional vem de transformação e intimidade. Explore questões profundas e compartilhe recursos.",
            9: "Hoje, sua segurança emocional vem de exploração e filosofia. É um bom dia para viagens, estudos superiores e expandir horizontes.",
            10: "Hoje, sua segurança emocional vem de carreira e reconhecimento público. Foque em metas profissionais e sua reputação.",
            11: "Hoje, sua segurança emocional vem de estar com amigos e grupos. É um bom dia para networking e atividades humanitárias.",
            12: "Hoje, sua segurança emocional vem de solitude e reflexão. É um bom dia para meditação, descanso e processos internos."
        }
        return advice_map.get(house, "Sintonize-se com suas emoções hoje.")

# Global instance
transit_service = TransitService()
