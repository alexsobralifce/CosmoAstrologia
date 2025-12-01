"""
Testes TDD para API de Birth Chart - Código Crítico
Garante que o mapa astral é gerado e retornado corretamente.
"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from fastapi import status
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Cliente de teste para a API."""
    from app.main import app
    return TestClient(app)


@pytest.fixture
def mock_user():
    """Mock de usuário para testes."""
    mock = MagicMock()
    mock.id = 1
    mock.email = "test@example.com"
    mock.name = "Test User"
    return mock


@pytest.fixture
def mock_birth_chart():
    """Mock de birth chart para testes."""
    mock = MagicMock()
    mock.id = 1
    mock.user_id = 1
    mock.name = "Test User"
    mock.birth_date = datetime(1990, 5, 15)
    mock.birth_time = "10:30"
    mock.birth_place = "São Paulo, SP"
    mock.latitude = -23.5505
    mock.longitude = -46.6333
    mock.sun_sign = "Touro"
    mock.moon_sign = "Escorpião"
    mock.ascendant_sign = "Leão"
    mock.sun_degree = 25.5
    mock.moon_degree = 12.3
    mock.ascendant_degree = 18.7
    mock.is_primary = True
    mock.created_at = datetime.now()
    mock.updated_at = datetime.now()
    return mock


@pytest.fixture
def mock_db_session(mock_birth_chart):
    """Mock de sessão do banco de dados."""
    mock_db = MagicMock()
    mock_query = MagicMock()
    mock_filter = MagicMock()
    mock_filter.first.return_value = mock_birth_chart
    mock_query.filter.return_value = mock_filter
    mock_db.query.return_value = mock_query
    mock_db.commit = MagicMock()
    mock_db.refresh = MagicMock()
    mock_db.rollback = MagicMock()
    
    # Criar um generator que retorna mock_db
    def get_db_generator():
        yield mock_db
    
    return mock_db, get_db_generator


class TestBirthChartAPI:
    """Testes para o endpoint /birth-chart."""
    
    @pytest.mark.critical
    @pytest.mark.api
    @pytest.mark.unit
    def test_get_birth_chart_returns_dict_not_orm_object(self, client, mock_user, mock_db_session):
        """
        TDD: Endpoint deve sempre retornar um dicionário serializável, nunca um objeto ORM.
        Código crítico - corrige bug que estava quebrando em produção.
        """
        # Arrange
        from app.main import app
        from app.core.database import get_db
        
        mock_db, get_db_generator = mock_db_session
        
        # Mock do cálculo do mapa astral
        mock_chart_data = {
            "sun_sign": "Touro",
            "moon_sign": "Escorpião",
            "ascendant_sign": "Leão",
            "mercury_sign": "Gêmeos",
            "venus_sign": "Áries",
            "mars_sign": "Virgem",
        }
        
        # Usar override do FastAPI para mockar a dependência
        app.dependency_overrides[get_db] = get_db_generator
        
        try:
            with patch('app.api.auth.get_current_user', return_value=mock_user):
                with patch('app.services.chart_data_cache.get_or_calculate_chart', return_value=mock_chart_data):
                    # Act
                    response = client.get(
                        "/api/auth/birth-chart",
                        headers={"Authorization": "Bearer fake-token"}
                    )
                    
                    # Assert
                    assert response.status_code == status.HTTP_200_OK
                    data = response.json()
                    
                    # Deve ser um dicionário (JSON), não um objeto ORM
                    assert isinstance(data, dict)
                    assert "id" in data
                    assert "name" in data
                    assert "sun_sign" in data
                    assert "moon_sign" in data
                    assert "ascendant_sign" in data
        finally:
            # Limpar override após o teste
            app.dependency_overrides.clear()
    
    @pytest.mark.critical
    @pytest.mark.api
    @pytest.mark.unit
    def test_get_birth_chart_handles_calculation_error_gracefully(self, client, mock_user, mock_db_session):
        """
        TDD: Endpoint deve retornar dados do banco mesmo quando cálculo falha.
        Código crítico - garante que nunca retorna objeto ORM em caso de erro.
        """
        # Arrange
        from app.main import app
        from app.core.database import get_db
        
        mock_db, get_db_generator = mock_db_session
        
        # Usar override do FastAPI para mockar a dependência
        app.dependency_overrides[get_db] = get_db_generator
        
        try:
            # Mock do cálculo falhando
            with patch('app.api.auth.get_current_user', return_value=mock_user):
                with patch('app.services.chart_data_cache.get_or_calculate_chart', side_effect=Exception("Erro no cálculo")):
                    # Act
                    response = client.get(
                        "/api/auth/birth-chart",
                        headers={"Authorization": "Bearer fake-token"}
                    )
                    
                    # Assert
                    assert response.status_code == status.HTTP_200_OK
                    data = response.json()
                    
                    # Deve retornar dicionário válido mesmo com erro
                    assert isinstance(data, dict)
                    assert "id" in data
                    assert "sun_sign" in data
                    # Dados do banco devem estar presentes
                    assert data["sun_sign"] == "Touro"
        finally:
            # Limpar override após o teste
            app.dependency_overrides.clear()
    
    @pytest.mark.critical
    @pytest.mark.api
    @pytest.mark.unit
    def test_get_birth_chart_returns_401_when_not_authenticated(self, client):
        """
        TDD: Endpoint deve retornar 401 quando usuário não está autenticado.
        Código crítico - garante segurança do endpoint.
        """
        # Act
        response = client.get("/api/auth/birth-chart")
        
        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.critical
    @pytest.mark.api
    @pytest.mark.unit
    def test_get_birth_chart_returns_404_when_chart_not_found(self, client, mock_user):
        """
        TDD: Endpoint deve retornar 404 quando mapa astral não existe.
        Código crítico - garante tratamento adequado de casos não encontrados.
        """
        # Arrange
        from app.main import app
        from app.core.database import get_db
        
        mock_db = MagicMock()
        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_filter.first.return_value = None  # Chart não encontrado
        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query
        
        def get_db_override():
            yield mock_db
        
        # Usar override do FastAPI para mockar a dependência
        app.dependency_overrides[get_db] = get_db_override
        
        try:
            with patch('app.api.auth.get_current_user', return_value=mock_user):
                # Act
                response = client.get(
                    "/api/auth/birth-chart",
                    headers={"Authorization": "Bearer fake-token"}
                )
                
                # Assert
                assert response.status_code == status.HTTP_404_NOT_FOUND
                assert "não encontrado" in response.json()["detail"].lower() or "not found" in response.json()["detail"].lower()
        finally:
            # Limpar override após o teste
            app.dependency_overrides.clear()
    
    @pytest.mark.critical
    @pytest.mark.api
    @pytest.mark.unit
    def test_get_birth_chart_includes_calculated_planets(self, client, mock_user, mock_db_session):
        """
        TDD: Endpoint deve incluir planetas calculados no retorno.
        Código crítico - garante dados completos do mapa astral.
        """
        # Arrange
        from app.main import app
        from app.core.database import get_db
        
        mock_db, get_db_generator = mock_db_session
        
        mock_chart_data = {
            "sun_sign": "Touro",
            "moon_sign": "Escorpião",
            "ascendant_sign": "Leão",
            "mercury_sign": "Gêmeos",
            "venus_sign": "Áries",
            "mars_sign": "Virgem",
            "jupiter_sign": "Peixes",
            "saturn_sign": "Capricórnio",
            "north_node_sign": "Áries",
            "chiron_sign": "Leão",
        }
        
        # Usar override do FastAPI para mockar a dependência
        app.dependency_overrides[get_db] = get_db_generator
        
        try:
            with patch('app.api.auth.get_current_user', return_value=mock_user):
                with patch('app.services.chart_data_cache.get_or_calculate_chart', return_value=mock_chart_data):
                    # Act
                    response = client.get(
                        "/api/auth/birth-chart",
                        headers={"Authorization": "Bearer fake-token"}
                    )
                    
                    # Assert
                    assert response.status_code == status.HTTP_200_OK
                    data = response.json()
                    
                    # Planetas calculados devem estar presentes
                    assert "mercury_sign" in data
                    assert "venus_sign" in data
                    assert "mars_sign" in data
                    assert data["mercury_sign"] == "Gêmeos"
                    assert data["venus_sign"] == "Áries"
        finally:
            # Limpar override após o teste
            app.dependency_overrides.clear()
    
    @pytest.mark.critical
    @pytest.mark.api
    @pytest.mark.unit
    def test_get_birth_chart_handles_null_values(self, client, mock_user, mock_birth_chart, mock_db_session):
        """
        TDD: Endpoint deve lidar corretamente com valores None no banco.
        Código crítico - garante robustez com dados incompletos.
        """
        # Arrange - alguns valores None
        from app.main import app
        from app.core.database import get_db
        
        mock_birth_chart.sun_degree = None
        mock_birth_chart.moon_degree = None
        
        mock_db, get_db_generator = mock_db_session
        
        mock_chart_data = {
            "sun_sign": "Touro",
            "moon_sign": "Escorpião",
            "ascendant_sign": "Leão",
            "sun_degree": 25.5,
            "moon_degree": 12.3,
        }
        
        # Usar override do FastAPI para mockar a dependência
        app.dependency_overrides[get_db] = get_db_generator
        
        try:
            with patch('app.api.auth.get_current_user', return_value=mock_user):
                with patch('app.services.chart_data_cache.get_or_calculate_chart', return_value=mock_chart_data):
                    # Act
                    response = client.get(
                        "/api/auth/birth-chart",
                        headers={"Authorization": "Bearer fake-token"}
                    )
                    
                    # Assert
                    assert response.status_code == status.HTTP_200_OK
                    data = response.json()
                    
                    # Deve retornar valores calculados mesmo se banco tinha None
                    assert "sun_degree" in data
                    assert data["sun_degree"] is not None
        finally:
            # Limpar override após o teste
            app.dependency_overrides.clear()
