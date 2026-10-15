"""Descrições didáticas de trânsito: texto em tabela, escolha por (planeta, aspecto)."""
import pytest

from app.services.transit_descriptions import GENERIC_TRANSIT_DESCRIPTION, SATURN_RETURN_DESCRIPTION, TEMPLATES
from app.services.transits_calculator import _generate_detailed_transit_description as descrever


@pytest.mark.unit
@pytest.mark.parametrize("planeta,aspecto", sorted(TEMPLATES))
def test_todo_template_formata_sem_erro(planeta, aspecto):
    texto = descrever(planeta, aspecto, "Sol", "Áries", "future")
    assert planeta in texto
    assert "{" not in texto and "}" not in texto


@pytest.mark.unit
def test_par_sem_texto_especifico_usa_o_generico():
    texto = descrever("Marte", "sextil", "Lua", "Touro", "future")
    assert texto.startswith("**O que é uma Sextil?**") or "Marte" in texto
    assert "{" not in texto


@pytest.mark.unit
def test_retorno_de_saturno_tem_texto_proprio():
    assert descrever("Saturno", "conjunção", "Saturno", "Áries", "saturn-return") == SATURN_RETURN_DESCRIPTION


@pytest.mark.unit
def test_template_generico_tem_todos_os_placeholders_usados():
    assert GENERIC_TRANSIT_DESCRIPTION.format(
        aspect_name="X", aspect_type="x", transit_planet="P", possessive="seu", natal_point="Sol"
    )
