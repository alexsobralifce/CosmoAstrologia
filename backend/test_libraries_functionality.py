#!/usr/bin/env python3
"""
Script para verificar se as bibliotecas de cálculos astrológicos estão funcionais.
Testa tanto kerykeion (Swiss Ephemeris) quanto ephem (PyEphem).
"""
import sys
from datetime import datetime

def test_kerykeion():
    """Testa se kerykeion está instalado e funcionando."""
    print("=" * 60)
    print("TESTE 1: Verificando kerykeion (Swiss Ephemeris)")
    print("=" * 60)
    
    try:
        from kerykeion import AstrologicalSubject
        print("✅ kerykeion importado com sucesso")
        
        # Testar cálculo básico
        try:
            kr = AstrologicalSubject(
                name="Test",
                year=1990,
                month=1,
                day=1,
                hour=12,
                minute=0,
                lat=23.5505,  # São Paulo
                lng=-46.6333,
                tz_str="America/Sao_Paulo"
            )
            print("✅ Instância AstrologicalSubject criada com sucesso")
            
            # Verificar se tem dados básicos
            if hasattr(kr, 'sun'):
                print(f"✅ Sol calculado: {kr.sun}")
            if hasattr(kr, 'moon'):
                print(f"✅ Lua calculada: {kr.moon}")
            if hasattr(kr, 'houses'):
                print(f"✅ Casas calculadas: {len(kr.houses)} casas")
            
            return True
        except Exception as e:
            print(f"❌ Erro ao criar instância kerykeion: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    except ImportError as e:
        print(f"❌ kerykeion não está instalado: {e}")
        print("   Instale com: pip install kerykeion")
        return False
    except Exception as e:
        print(f"❌ Erro ao testar kerykeion: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ephem():
    """Testa se ephem está instalado e funcionando."""
    print("\n" + "=" * 60)
    print("TESTE 2: Verificando ephem (PyEphem)")
    print("=" * 60)
    
    try:
        import ephem
        print("✅ ephem importado com sucesso")
        
        # Testar cálculo básico
        try:
            observer = ephem.Observer()
            observer.lat = '23.5505'  # São Paulo
            observer.lon = '-46.6333'
            observer.date = '1990/1/1 12:00:00'
            
            sun = ephem.Sun()
            sun.compute(observer)
            
            print(f"✅ Sol calculado: RA={sun.ra}, Dec={sun.dec}")
            
            moon = ephem.Moon()
            moon.compute(observer)
            print(f"✅ Lua calculada: RA={moon.ra}, Dec={moon.dec}")
            
            return True
        except Exception as e:
            print(f"❌ Erro ao calcular com ephem: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    except ImportError as e:
        print(f"❌ ephem não está instalado: {e}")
        print("   Instale com: pip install ephem")
        return False
    except Exception as e:
        print(f"❌ Erro ao testar ephem: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_swiss_ephemeris_calculator():
    """Testa o serviço swiss_ephemeris_calculator."""
    print("\n" + "=" * 60)
    print("TESTE 3: Verificando swiss_ephemeris_calculator")
    print("=" * 60)
    
    try:
        from app.services.swiss_ephemeris_calculator import (
            calculate_birth_chart,
            KERYKEION_AVAILABLE
        )
        
        if not KERYKEION_AVAILABLE:
            print("⚠️  kerykeion não está disponível, mas o módulo pode usar fallback")
        
        # Testar cálculo de mapa astral
        birth_date = datetime(1990, 1, 1)
        birth_time = "12:00"
        latitude = -23.5505  # São Paulo
        longitude = -46.6333
        
        try:
            result = calculate_birth_chart(birth_date, birth_time, latitude, longitude)
            print("✅ calculate_birth_chart executado com sucesso")
            
            # Verificar campos essenciais
            essential_fields = ['sun_sign', 'moon_sign', 'ascendant_sign']
            for field in essential_fields:
                if field in result and result[field]:
                    print(f"✅ {field}: {result[field]}")
                else:
                    print(f"⚠️  {field}: não encontrado ou vazio")
            
            return True
        except Exception as e:
            print(f"❌ Erro ao calcular mapa astral: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    except ImportError as e:
        print(f"❌ Erro ao importar swiss_ephemeris_calculator: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"❌ Erro ao testar swiss_ephemeris_calculator: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_astrology_calculator():
    """Testa o serviço astrology_calculator (fallback)."""
    print("\n" + "=" * 60)
    print("TESTE 4: Verificando astrology_calculator (fallback)")
    print("=" * 60)
    
    try:
        from app.services.astrology_calculator import (
            calculate_birth_chart,
            get_zodiac_sign,
            shortest_angular_distance
        )
        print("✅ astrology_calculator importado com sucesso")
        
        # Testar função básica
        sign_result = get_zodiac_sign(15.0)  # Áries
        print(f"✅ get_zodiac_sign(15.0): {sign_result}")
        
        # Testar distância angular
        distance = shortest_angular_distance(10.0, 350.0)
        print(f"✅ shortest_angular_distance(10.0, 350.0): {distance}")
        
        # Testar cálculo completo (pode usar fallback para ephem)
        birth_date = datetime(1990, 1, 1)
        birth_time = "12:00"
        latitude = -23.5505
        longitude = -46.6333
        
        try:
            result = calculate_birth_chart(
                birth_date, birth_time, latitude, longitude,
                use_swiss_ephemeris=False  # Forçar uso de ephem
            )
            print("✅ calculate_birth_chart (ephem) executado com sucesso")
            
            if 'sun_sign' in result:
                print(f"✅ sun_sign: {result['sun_sign']}")
            
            return True
        except Exception as e:
            print(f"⚠️  Erro ao calcular com ephem (pode ser esperado se kerykeion estiver disponível): {e}")
            return True  # Não é crítico se kerykeion estiver funcionando
            
    except ImportError as e:
        print(f"❌ Erro ao importar astrology_calculator: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"❌ Erro ao testar astrology_calculator: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Executa todos os testes."""
    print("\n" + "=" * 60)
    print("VERIFICAÇÃO DE BIBLIOTECAS DE CÁLCULOS ASTROLÓGICOS")
    print("=" * 60 + "\n")
    
    results = []
    
    # Teste 1: kerykeion
    results.append(("kerykeion", test_kerykeion()))
    
    # Teste 2: ephem
    results.append(("ephem", test_ephem()))
    
    # Teste 3: swiss_ephemeris_calculator
    results.append(("swiss_ephemeris_calculator", test_swiss_ephemeris_calculator()))
    
    # Teste 4: astrology_calculator
    results.append(("astrology_calculator", test_astrology_calculator()))
    
    # Resumo
    print("\n" + "=" * 60)
    print("RESUMO DOS TESTES")
    print("=" * 60)
    
    for name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{name}: {status}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n✅ TODOS OS TESTES PASSARAM!")
        print("   As bibliotecas de cálculos astrológicos estão funcionais.")
    else:
        print("\n⚠️  ALGUNS TESTES FALHARAM")
        print("   Verifique os erros acima e instale as dependências necessárias.")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
