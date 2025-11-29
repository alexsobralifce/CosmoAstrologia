"""
Serviço para cálculo de mapa numerológico.
Calcula números pessoais baseados no nome completo e data de nascimento.
"""

from datetime import datetime
from typing import Dict, Any, List
import re


class NumerologyCalculator:
    """Calculadora de números numerológicos."""
    
    # Tabela de correspondência letra-número (Pitagórica)
    LETTER_TO_NUMBER = {
        'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8, 'I': 9,
        'J': 1, 'K': 2, 'L': 3, 'M': 4, 'N': 5, 'O': 6, 'P': 7, 'Q': 8, 'R': 9,
        'S': 1, 'T': 2, 'U': 3, 'V': 4, 'W': 5, 'X': 6, 'Y': 7, 'Z': 8
    }
    
    @staticmethod
    def reduce_to_single_digit(number: int, master_numbers: bool = True) -> int:
        """
        Reduz um número a um único dígito (1-9) ou mantém números mestres (11, 22, 33).
        
        Args:
            number: Número a reduzir
            master_numbers: Se True, mantém 11, 22, 33 como números mestres
        
        Returns:
            Número reduzido ou número mestre
        """
        if master_numbers and number in [11, 22, 33]:
            return number
        
        while number > 9:
            number = sum(int(digit) for digit in str(number))
            if master_numbers and number in [11, 22, 33]:
                return number
        
        return number
    
    @staticmethod
    def normalize_name(name: str) -> str:
        """
        Normaliza o nome removendo acentos e convertendo para maiúsculas.
        
        Args:
            name: Nome a normalizar
        
        Returns:
            Nome normalizado
        """
        # Remover acentos
        import unicodedata
        name = unicodedata.normalize('NFD', name)
        name = ''.join(char for char in name if unicodedata.category(char) != 'Mn')
        
        # Converter para maiúsculas e remover espaços extras
        name = name.upper().strip()
        name = re.sub(r'\s+', ' ', name)
        
        return name
    
    @staticmethod
    def calculate_name_number(name: str) -> Dict[str, Any]:
        """
        Calcula o número do nome (Expressão/Personalidade).
        
        Args:
            name: Nome completo
        
        Returns:
            Dicionário com número do nome e detalhes
        """
        normalized = NumerologyCalculator.normalize_name(name)
        total = 0
        
        for char in normalized:
            if char in NumerologyCalculator.LETTER_TO_NUMBER:
                total += NumerologyCalculator.LETTER_TO_NUMBER[char]
        
        number = NumerologyCalculator.reduce_to_single_digit(total)
        
        return {
            'number': number,
            'raw_total': total,
            'is_master': number in [11, 22, 33]
        }
    
    @staticmethod
    def calculate_life_path(birth_date: datetime) -> Dict[str, Any]:
        """
        Calcula o Caminho de Vida (Life Path) baseado na data de nascimento.
        
        Args:
            birth_date: Data de nascimento
        
        Returns:
            Dicionário com número do caminho de vida e detalhes
        """
        day = birth_date.day
        month = birth_date.month
        year = birth_date.year
        
        # Reduzir dia, mês e ano
        day_reduced = NumerologyCalculator.reduce_to_single_digit(day, master_numbers=False)
        month_reduced = NumerologyCalculator.reduce_to_single_digit(month, master_numbers=False)
        year_reduced = NumerologyCalculator.reduce_to_single_digit(year, master_numbers=False)
        
        # Somar os três números reduzidos
        total = day_reduced + month_reduced + year_reduced
        life_path = NumerologyCalculator.reduce_to_single_digit(total)
        
        return {
            'number': life_path,
            'day': day,
            'day_reduced': day_reduced,
            'month': month,
            'month_reduced': month_reduced,
            'year': year,
            'year_reduced': year_reduced,
            'raw_total': total,
            'is_master': life_path in [11, 22, 33]
        }
    
    @staticmethod
    def calculate_destiny_number(full_name: str) -> Dict[str, Any]:
        """
        Calcula o Número do Destino (Destiny Number) baseado no nome completo.
        Também conhecido como Número da Expressão ou Número do Nome.
        
        Args:
            full_name: Nome completo
        
        Returns:
            Dicionário com número do destino e detalhes
        """
        return NumerologyCalculator.calculate_name_number(full_name)
    
    @staticmethod
    def calculate_soul_number(full_name: str) -> Dict[str, Any]:
        """
        Calcula o Número da Alma (Soul Number) baseado nas vogais do nome.
        Também conhecido como Número do Desejo do Coração.
        
        Args:
            full_name: Nome completo
        
        Returns:
            Dicionário com número da alma e detalhes
        """
        normalized = NumerologyCalculator.normalize_name(full_name)
        vowels = 'AEIOU'
        total = 0
        
        for char in normalized:
            if char in vowels and char in NumerologyCalculator.LETTER_TO_NUMBER:
                total += NumerologyCalculator.LETTER_TO_NUMBER[char]
        
        number = NumerologyCalculator.reduce_to_single_digit(total)
        
        return {
            'number': number,
            'raw_total': total,
            'is_master': number in [11, 22, 33]
        }
    
    @staticmethod
    def calculate_personality_number(full_name: str) -> Dict[str, Any]:
        """
        Calcula o Número da Personalidade baseado nas consoantes do nome.
        
        Args:
            full_name: Nome completo
        
        Returns:
            Dicionário com número da personalidade e detalhes
        """
        normalized = NumerologyCalculator.normalize_name(full_name)
        vowels = 'AEIOU'
        total = 0
        
        for char in normalized:
            if char not in vowels and char in NumerologyCalculator.LETTER_TO_NUMBER:
                total += NumerologyCalculator.LETTER_TO_NUMBER[char]
        
        number = NumerologyCalculator.reduce_to_single_digit(total)
        
        return {
            'number': number,
            'raw_total': total,
            'is_master': number in [11, 22, 33]
        }
    
    @staticmethod
    def calculate_birthday_number(birth_date: datetime) -> Dict[str, Any]:
        """
        Calcula o Número do Aniversário (Birthday Number) baseado no dia do nascimento.
        
        Args:
            birth_date: Data de nascimento
        
        Returns:
            Dicionário com número do aniversário e detalhes
        """
        day = birth_date.day
        number = NumerologyCalculator.reduce_to_single_digit(day, master_numbers=False)
        
        return {
            'number': number,
            'day': day,
            'is_master': False  # Número do aniversário não usa números mestres
        }
    
    @staticmethod
    def calculate_maturity_number(life_path: int, expression: int) -> Dict[str, Any]:
        """
        Calcula o Número da Maturidade (Maturity Number).
        Soma do Caminho de Vida + Número da Expressão.
        
        Args:
            life_path: Número do caminho de vida
            expression: Número da expressão/destino
        
        Returns:
            Dicionário com número da maturidade e detalhes
        """
        total = life_path + expression
        number = NumerologyCalculator.reduce_to_single_digit(total)
        
        return {
            'number': number,
            'raw_total': total,
            'is_master': number in [11, 22, 33]
        }
    
    @staticmethod
    def calculate_pinnacles(birth_date: datetime) -> List[Dict[str, Any]]:
        """
        Calcula os 4 Pinnacles (Pináculos) da vida.
        
        Args:
            birth_date: Data de nascimento
        
        Returns:
            Lista com os 4 pináculos e suas idades
        """
        day = birth_date.day
        month = birth_date.month
        
        day_reduced = NumerologyCalculator.reduce_to_single_digit(day, master_numbers=False)
        month_reduced = NumerologyCalculator.reduce_to_single_digit(month, master_numbers=False)
        
        # Primeiro Pináculo: Mês + Dia
        pinnacle1 = NumerologyCalculator.reduce_to_single_digit(month_reduced + day_reduced)
        
        # Segundo Pináculo: Dia + Ano
        year_reduced = NumerologyCalculator.reduce_to_single_digit(birth_date.year, master_numbers=False)
        pinnacle2 = NumerologyCalculator.reduce_to_single_digit(day_reduced + year_reduced)
        
        # Terceiro Pináculo: Primeiro + Segundo
        pinnacle3 = NumerologyCalculator.reduce_to_single_digit(pinnacle1 + pinnacle2)
        
        # Quarto Pináculo: Mês + Ano
        pinnacle4 = NumerologyCalculator.reduce_to_single_digit(month_reduced + year_reduced)
        
        # Idades aproximadas dos pináculos (baseado em ciclo de 9 anos)
        # Ajustar conforme necessário
        return [
            {
                'number': pinnacle1,
                'period': '0-27 anos',
                'start_age': 0,
                'end_age': 27
            },
            {
                'number': pinnacle2,
                'period': '28-54 anos',
                'start_age': 28,
                'end_age': 54
            },
            {
                'number': pinnacle3,
                'period': '55-81 anos',
                'start_age': 55,
                'end_age': 81
            },
            {
                'number': pinnacle4,
                'period': '82+ anos',
                'start_age': 82,
                'end_age': None
            }
        ]
    
    @staticmethod
    def calculate_challenges(birth_date: datetime) -> List[Dict[str, Any]]:
        """
        Calcula os 3 Desafios (Challenges) da vida.
        
        Args:
            birth_date: Data de nascimento
        
        Returns:
            Lista com os 3 desafios
        """
        day = birth_date.day
        month = birth_date.month
        year = birth_date.year
        
        day_reduced = NumerologyCalculator.reduce_to_single_digit(day, master_numbers=False)
        month_reduced = NumerologyCalculator.reduce_to_single_digit(month, master_numbers=False)
        year_reduced = NumerologyCalculator.reduce_to_single_digit(year, master_numbers=False)
        
        # Primeiro Desafio: |Mês - Dia|
        challenge1 = abs(month_reduced - day_reduced)
        challenge1 = NumerologyCalculator.reduce_to_single_digit(challenge1, master_numbers=False)
        
        # Segundo Desafio: |Dia - Ano|
        challenge2 = abs(day_reduced - year_reduced)
        challenge2 = NumerologyCalculator.reduce_to_single_digit(challenge2, master_numbers=False)
        
        # Terceiro Desafio: |Primeiro - Segundo|
        challenge3 = abs(challenge1 - challenge2)
        challenge3 = NumerologyCalculator.reduce_to_single_digit(challenge3, master_numbers=False)
        
        return [
            {
                'number': challenge1,
                'period': '0-27 anos',
                'start_age': 0,
                'end_age': 27
            },
            {
                'number': challenge2,
                'period': '28-54 anos',
                'start_age': 28,
                'end_age': 54
            },
            {
                'number': challenge3,
                'period': '55+ anos',
                'start_age': 55,
                'end_age': None
            }
        ]
    
    @staticmethod
    def calculate_personal_year(birth_date: datetime, target_year: int = None) -> Dict[str, Any]:
        """
        Calcula o Ano Pessoal para um ano específico.
        
        Args:
            birth_date: Data de nascimento
            target_year: Ano alvo (se None, usa o ano atual)
        
        Returns:
            Dicionário com número do ano pessoal e detalhes
        """
        from datetime import date
        if target_year is None:
            target_year = date.today().year
        
        day = birth_date.day
        month = birth_date.month
        
        day_reduced = NumerologyCalculator.reduce_to_single_digit(day, master_numbers=False)
        month_reduced = NumerologyCalculator.reduce_to_single_digit(month, master_numbers=False)
        year_reduced = NumerologyCalculator.reduce_to_single_digit(target_year, master_numbers=False)
        
        total = day_reduced + month_reduced + year_reduced
        personal_year = NumerologyCalculator.reduce_to_single_digit(total)
        
        return {
            'number': personal_year,
            'year': target_year,
            'raw_total': total,
            'is_master': personal_year in [11, 22, 33]
        }
    
    @staticmethod
    def calculate_birth_grid(full_name: str, birth_date: datetime) -> Dict[str, Any]:
        """
        Calcula a Grade de Nascimento (Birth Grid) 3x3.
        Identifica setas de força e fraqueza.
        
        Args:
            full_name: Nome completo
            birth_date: Data de nascimento
        
        Returns:
            Dicionário com a grade e análise de setas
        """
        normalized = NumerologyCalculator.normalize_name(full_name)
        
        # Criar grade 3x3 (1-9)
        grid = {i: 0 for i in range(1, 10)}
        
        # Contar letras no nome
        for char in normalized:
            if char in NumerologyCalculator.LETTER_TO_NUMBER:
                num = NumerologyCalculator.LETTER_TO_NUMBER[char]
                grid[num] = grid.get(num, 0) + 1
        
        # Adicionar números da data de nascimento
        day = birth_date.day
        month = birth_date.month
        year = birth_date.year
        
        # Reduzir e adicionar à grade
        day_reduced = NumerologyCalculator.reduce_to_single_digit(day, master_numbers=False)
        month_reduced = NumerologyCalculator.reduce_to_single_digit(month, master_numbers=False)
        year_reduced = NumerologyCalculator.reduce_to_single_digit(year, master_numbers=False)
        
        grid[day_reduced] = grid.get(day_reduced, 0) + 1
        grid[month_reduced] = grid.get(month_reduced, 0) + 1
        grid[year_reduced] = grid.get(year_reduced, 0) + 1
        
        # Identificar setas (linhas completas = força, linhas vazias = fraqueza)
        # Linhas horizontais
        row1 = [1, 2, 3]
        row2 = [4, 5, 6]
        row3 = [7, 8, 9]
        
        # Linhas verticais
        col1 = [1, 4, 7]
        col2 = [2, 5, 8]
        col3 = [3, 6, 9]
        
        # Diagonais
        diag1 = [1, 5, 9]
        diag2 = [3, 5, 7]
        
        arrows_strength = []
        arrows_weakness = []
        
        # Verificar linhas completas (força)
        for line, name in [
            (row1, "Linha Superior"),
            (row2, "Linha do Meio"),
            (row3, "Linha Inferior"),
            (col1, "Coluna Esquerda"),
            (col2, "Coluna do Meio"),
            (col3, "Coluna Direita"),
            (diag1, "Diagonal Principal"),
            (diag2, "Diagonal Secundária")
        ]:
            if all(grid[num] > 0 for num in line):
                arrows_strength.append(name)
            elif all(grid[num] == 0 for num in line):
                arrows_weakness.append(name)
        
        return {
            'grid': grid,
            'arrows_strength': arrows_strength,
            'arrows_weakness': arrows_weakness,
            'missing_numbers': [num for num in range(1, 10) if grid[num] == 0]
        }
    
    @staticmethod
    def check_karmic_debt(numbers: List[int]) -> List[int]:
        """
        Verifica se há números de dívida cármica (13, 14, 16, 19).
        
        Args:
            numbers: Lista de números a verificar
        
        Returns:
            Lista de números de dívida cármica encontrados
        """
        karmic_debts = [13, 14, 16, 19]
        found = []
        
        for num in numbers:
            if num in karmic_debts:
                found.append(num)
        
        return found
    
    @staticmethod
    def calculate_life_cycle(birth_date: datetime) -> Dict[str, Any]:
        """
        Calcula o ciclo de vida atual baseado no Triângulo Divino.
        Ciclos: Juventude (0-27), Poder (28-54), Sabedoria (55+)
        
        Args:
            birth_date: Data de nascimento
        
        Returns:
            Dicionário com ciclo atual e número do ciclo
        """
        from datetime import date
        today = date.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        
        if age < 28:
            cycle = "Juventude"
            cycle_number = NumerologyCalculator.reduce_to_single_digit(
                birth_date.day + birth_date.month, master_numbers=False
            )
        elif age < 55:
            cycle = "Poder"
            cycle_number = NumerologyCalculator.reduce_to_single_digit(
                birth_date.day + birth_date.year, master_numbers=False
            )
        else:
            cycle = "Sabedoria"
            cycle_number = NumerologyCalculator.reduce_to_single_digit(
                birth_date.month + birth_date.year, master_numbers=False
            )
        
        return {
            'cycle': cycle,
            'cycle_number': cycle_number,
            'age': age
        }
    
    @staticmethod
    def calculate_full_numerology_map(full_name: str, birth_date: datetime) -> Dict[str, Any]:
        """
        Calcula o mapa numerológico completo.
        
        Args:
            full_name: Nome completo
            birth_date: Data de nascimento
        
        Returns:
            Dicionário completo com todos os números numerológicos
        """
        life_path = NumerologyCalculator.calculate_life_path(birth_date)
        destiny = NumerologyCalculator.calculate_destiny_number(full_name)
        soul = NumerologyCalculator.calculate_soul_number(full_name)
        personality = NumerologyCalculator.calculate_personality_number(full_name)
        birthday = NumerologyCalculator.calculate_birthday_number(birth_date)
        maturity = NumerologyCalculator.calculate_maturity_number(
            life_path['number'],
            destiny['number']
        )
        pinnacles = NumerologyCalculator.calculate_pinnacles(birth_date)
        challenges = NumerologyCalculator.calculate_challenges(birth_date)
        personal_year = NumerologyCalculator.calculate_personal_year(birth_date)
        birth_grid = NumerologyCalculator.calculate_birth_grid(full_name, birth_date)
        life_cycle = NumerologyCalculator.calculate_life_cycle(birth_date)
        
        # Verificar dívidas cármicas (verificar nos raw_total antes da redução)
        # Para birthday, o número original é o próprio dia
        all_raw_totals = [
            life_path['raw_total'],
            destiny['raw_total'],
            soul['raw_total'],
            personality['raw_total'],
            birthday['day']  # Para birthday, usar o dia original
        ]
        karmic_debts = NumerologyCalculator.check_karmic_debt(all_raw_totals)
        
        return {
            'full_name': full_name,
            'birth_date': birth_date.isoformat(),
            'life_path': life_path,
            'destiny': destiny,
            'soul': soul,
            'personality': personality,
            'birthday': birthday,
            'maturity': maturity,
            'pinnacles': pinnacles,
            'challenges': challenges,
            'personal_year': personal_year,
            'birth_grid': birth_grid,
            'life_cycle': life_cycle,
            'karmic_debts': karmic_debts
        }

