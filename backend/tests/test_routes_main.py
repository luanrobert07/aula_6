import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app, Professor, ProfessorAtualizar


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_database():
    """Fixture para mockar a conexão com o banco de dados"""
    with patch("main.get_database") as mock_get_db:
        mock_conn = AsyncMock()
        mock_get_db.return_value = mock_conn
        yield mock_conn


class TestCriarProfessor:

    def test_criar_professor_sucesso(self, client, mock_database):
        mock_database.fetchval.return_value = None
        mock_database.execute.return_value = None

        response = client.post(
            "/api/v1/professores/",
            json={
                "nome": "João Silva",
                "email": "joao@example.com",
                "sala_de_atendimento": "Sala 101"
            }
        )

        assert response.status_code == 201
        assert response.json() == {"message": "Professor cadastrado com sucesso!"}
        mock_database.execute.assert_called_once()

    def test_criar_professor_email_duplicado(self, client, mock_database):
        mock_database.fetchval.return_value = 1

        response = client.post(
            "/api/v1/professores/",
            json={
                "nome": "Maria Santos",
                "email": "maria@example.com",
                "sala_de_atendimento": "Sala 102"
            }
        )

        assert response.status_code == 400
        assert response.json() == {"detail": "Email já cadastrado."}
        mock_database.execute.assert_not_called()

    def test_criar_professor_dados_invalidos(self, client, mock_database):
        response = client.post(
            "/api/v1/professores/",
            json={"nome": "Pedro"}
        )

        assert response.status_code == 422

    def test_criar_professor_email_vazio(self, client, mock_database):
        response = client.post(
            "/api/v1/professores/",
            json={
                "nome": "Ana",
                "email": "",
                "sala_de_atendimento": "Sala 103"
            }
        )

        assert response.status_code == 422


class TestListarProfessores:

    def test_listar_professores_vazio(self, client, mock_database):
        mock_database.fetch.return_value = []

        response = client.get("/api/v1/professores/")

        assert response.status_code == 200
        assert response.json() == []

    def test_listar_professores_com_dados(self, client, mock_database):
        mock_row1 = MagicMock()
        mock_row1.__iter__ = MagicMock(return_value=iter([
            ("id", 1), ("nome", "João"), ("email", "joao@ex.com"), ("sala_de_atendimento", "Sala 101")
        ]))
        mock_row1.__getitem__ = lambda self, key: {
            "id": 1, "nome": "João", "email": "joao@ex.com", "sala_de_atendimento": "Sala 101"
        }[key]

        mock_row2 = MagicMock()
        mock_row2.__iter__ = MagicMock(return_value=iter([
            ("id", 2), ("nome", "Maria"), ("email", "maria@ex.com"), ("sala_de_atendimento", "Sala 102")
        ]))
        mock_row2.__getitem__ = lambda self, key: {
            "id": 2, "nome": "Maria", "email": "maria@ex.com", "sala_de_atendimento": "Sala 102"
        }[key]

        mock_database.fetch.return_value = [mock_row1, mock_row2]

        response = client.get("/api/v1/professores/")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["nome"] == "João"
        assert data[1]["nome"] == "Maria"


class TestObterProfessor:

    def test_obter_professor_existente(self, client, mock_database):
        mock_row = MagicMock()
        mock_row.__iter__ = MagicMock(return_value=iter([
            ("id", 1), ("nome", "João"), ("email", "joao@ex.com"), ("sala_de_atendimento", "Sala 101")
        ]))
        mock_row.__getitem__ = lambda self, key: {
            "id": 1, "nome": "João", "email": "joao@ex.com", "sala_de_atendimento": "Sala 101"
        }[key]

        mock_database.fetchrow.return_value = mock_row

        response = client.get("/api/v1/professores/1")

        assert response.status_code == 200
        assert response.json()["nome"] == "João"
        assert response.json()["id"] == 1

    def test_obter_professor_inexistente(self, client, mock_database):
        mock_database.fetchrow.return_value = None

        response = client.get("/api/v1/professores/999")

        assert response.status_code == 404
        assert response.json() == {"detail": "Professor não encontrado."}

    def test_obter_professor_id_invalido(self, client, mock_database):
        """Testa obtenção com ID em formato inválido"""
        response = client.get("/api/v1/professores/abc")

        assert response.status_code == 422


class TestAtualizarProfessor:

    def test_atualizar_professor_nome(self, client, mock_database):
        mock_row = MagicMock()
        mock_row.__iter__ = MagicMock(return_value=iter([
            ("id", 1), ("nome", "João"), ("email", "joao@ex.com"), ("sala_de_atendimento", "Sala 101")
        ]))
        mock_database.fetchrow.return_value = mock_row
        mock_database.fetchval.return_value = None
        mock_database.execute.return_value = None

        response = client.patch(
            "/api/v1/professores/1",
            json={"nome": "João Silva Atualizado"}
        )

        assert response.status_code == 200
        assert response.json() == {"message": "Professor atualizado com sucesso!"}

    def test_atualizar_professor_email(self, client, mock_database):
        mock_row = MagicMock()
        mock_database.fetchrow.return_value = mock_row
        mock_database.fetchval.return_value = None
        mock_database.execute.return_value = None

        response = client.patch(
            "/api/v1/professores/1",
            json={"email": "novo@example.com"}
        )

        assert response.status_code == 200

    def test_atualizar_professor_email_duplicado(self, client, mock_database):
        mock_row = MagicMock()
        mock_database.fetchrow.return_value = mock_row
        mock_database.fetchval.return_value = 1

        response = client.patch(
            "/api/v1/professores/1",
            json={"email": "existente@example.com"}
        )

        assert response.status_code == 400
        assert response.json() == {"detail": "Email já cadastrado."}

    def test_atualizar_professor_inexistente(self, client, mock_database):
        mock_database.fetchrow.return_value = None

        response = client.patch(
            "/api/v1/professores/999",
            json={"nome": "Novo Nome"}
        )

        assert response.status_code == 404
        assert response.json() == {"detail": "Professor não encontrado."}

    def test_atualizar_professor_todos_campos(self, client, mock_database):
        mock_row = MagicMock()
        mock_database.fetchrow.return_value = mock_row
        mock_database.fetchval.return_value = None
        mock_database.execute.return_value = None

        response = client.patch(
            "/api/v1/professores/1",
            json={
                "nome": "Nome Novo",
                "email": "novo@example.com",
                "sala_de_atendimento": "Sala 201"
            }
        )

        assert response.status_code == 200


class TestRemoverProfessor:

    def test_remover_professor_existente(self, client, mock_database):
        mock_database.execute.return_value = "DELETE 1"

        response = client.delete("/api/v1/professores/1")

        assert response.status_code == 200
        assert response.json() == {"message": "Professor removido com sucesso!"}

    def test_remover_professor_inexistente(self, client, mock_database):
        mock_database.execute.return_value = "DELETE 0"

        response = client.delete("/api/v1/professores/999")

        assert response.status_code == 404
        assert response.json() == {"detail": "Professor não encontrado."}

    def test_remover_professor_id_invalido(self, client, mock_database):
        response = client.delete("/api/v1/professores/abc")

        assert response.status_code == 422


class TestResetarProfessores:

    @patch("builtins.open", create=True)
    def test_resetar_professores_sucesso(self, mock_open, client, mock_database):
        mock_open.return_value.__enter__.return_value.read.return_value = "SQL RESET SCRIPT"
        mock_database.execute.return_value = None

        response = client.delete("/api/v1/professores/")

        assert response.status_code == 200
        assert response.json() == {"message": "Banco de dados restaurado com sucesso!"}

    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_resetar_professores_arquivo_nao_encontrado(self, mock_open, client, mock_database):
        response = client.delete("/api/v1/professores/")

        assert response.status_code == 500


class TestIntegration:

    def test_fluxo_completo_criar_e_obter(self, client, mock_database):
        mock_database.fetchval.return_value = None
        mock_database.execute.return_value = None

        response_criar = client.post(
            "/api/v1/professores/",
            json={
                "nome": "Carlos",
                "email": "carlos@example.com",
                "sala_de_atendimento": "Sala 104"
            }
        )
        assert response_criar.status_code == 201

        mock_row = MagicMock()
        mock_row.__iter__ = MagicMock(return_value=iter([
            ("id", 1), ("nome", "Carlos"), ("email", "carlos@example.com"), ("sala_de_atendimento", "Sala 104")
        ]))
        mock_row.__getitem__ = lambda self, key: {
            "id": 1, "nome": "Carlos", "email": "carlos@example.com", "sala_de_atendimento": "Sala 104"
        }[key]

        mock_database.fetchrow.return_value = mock_row
        response_obter = client.get("/api/v1/professores/1")

        assert response_obter.status_code == 200
        assert response_obter.json()["nome"] == "Carlos"
