"""Tests para todos los endpoints de la API de Mergington High School"""

import pytest


class TestRootEndpoint:
    """Tests para el endpoint raíz GET /"""

    def test_root_redirects_to_index(self, client):
        """El endpoint raíz debe redirigir a /static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestActivitiesEndpoint:
    """Tests para el endpoint GET /activities"""

    def test_get_activities_returns_all_activities(self, client):
        """Debe retornar todas las actividades disponibles"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data

    def test_activities_have_required_fields(self, client):
        """Cada actividad debe tener los campos requeridos"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)

    def test_participants_list_is_initially_empty(self, client, sample_activity_name):
        """Los participantes deben estar inicialmente vacíos"""
        response = client.get("/activities")
        data = response.json()
        assert data[sample_activity_name]["participants"] == []


class TestSignupEndpoint:
    """Tests para el endpoint POST /activities/{activity_name}/signup"""

    def test_signup_valid_student(self, client, sample_activity_name, sample_email):
        """Un estudiante debe poder registrarse en una actividad válida"""
        response = client.post(
            f"/activities/{sample_activity_name}/signup",
            params={"email": sample_email}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert sample_email in data["message"]
        assert sample_activity_name in data["message"]

    def test_signup_adds_participant_to_activity(self, client, sample_activity_name, sample_email):
        """Registrarse debe añadir el email a la lista de participantes"""
        client.post(
            f"/activities/{sample_activity_name}/signup",
            params={"email": sample_email}
        )
        
        response = client.get("/activities")
        data = response.json()
        assert sample_email in data[sample_activity_name]["participants"]

    def test_signup_multiple_students(self, client, sample_activity_name):
        """Múltiples estudiantes deben poder registrarse en la misma actividad"""
        emails = ["email1@mergington.edu", "email2@mergington.edu", "email3@mergington.edu"]
        
        for email in emails:
            response = client.post(
                f"/activities/{sample_activity_name}/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Verificar que todos están en la lista
        response = client.get("/activities")
        data = response.json()
        for email in emails:
            assert email in data[sample_activity_name]["participants"]

    def test_signup_duplicate_registration_fails(self, client, sample_activity_name, sample_email):
        """No se debe permitir registrar al mismo estudiante dos veces"""
        # Primer registro debe exitoso
        response1 = client.post(
            f"/activities/{sample_activity_name}/signup",
            params={"email": sample_email}
        )
        assert response1.status_code == 200
        
        # Segundo registro debe fallar
        response2 = client.post(
            f"/activities/{sample_activity_name}/signup",
            params={"email": sample_email}
        )
        assert response2.status_code == 400
        data = response2.json()
        assert "Already signed up" in data["detail"]

    def test_signup_nonexistent_activity(self, client, sample_email):
        """Registrarse en una actividad inexistente debe fallar"""
        response = client.post(
            "/activities/Actividad Inexistente/signup",
            params={"email": sample_email}
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_signup_with_invalid_email(self, client, sample_activity_name):
        """Registrarse con un email inválido debe ejecutarse (validación frontend)"""
        # La API acepta cualquier string como email (validación en frontend)
        response = client.post(
            f"/activities/{sample_activity_name}/signup",
            params={"email": "no-es-email"}
        )
        assert response.status_code == 200


class TestUnregisterEndpoint:
    """Tests para el endpoint DELETE /activities/{activity_name}/unregister"""

    def test_unregister_existing_participant(self, client, sample_activity_name, sample_email):
        """Debe poderse desregistrar un participante existente"""
        # Primero registrar
        client.post(
            f"/activities/{sample_activity_name}/signup",
            params={"email": sample_email}
        )
        
        # Luego desregistrar
        response = client.delete(
            f"/activities/{sample_activity_name}/unregister",
            params={"email": sample_email}
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        assert sample_email in data["message"]

    def test_unregister_removes_participant_from_activity(self, client, sample_activity_name, sample_email):
        """Desregistrarse debe remover el email de la lista de participantes"""
        # Registrar
        client.post(
            f"/activities/{sample_activity_name}/signup",
            params={"email": sample_email}
        )
        
        # Desregistrar
        client.delete(
            f"/activities/{sample_activity_name}/unregister",
            params={"email": sample_email}
        )
        
        # Verificar que fue removido
        response = client.get("/activities")
        data = response.json()
        assert sample_email not in data[sample_activity_name]["participants"]

    def test_unregister_nonexistent_participant(self, client, sample_activity_name, sample_email):
        """Desregistrar a un participante que no existe debe fallar"""
        response = client.delete(
            f"/activities/{sample_activity_name}/unregister",
            params={"email": sample_email}
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_unregister_from_nonexistent_activity(self, client, sample_email):
        """Desregistrarse de una actividad inexistente debe fallar"""
        response = client.delete(
            "/activities/Actividad Inexistente/unregister",
            params={"email": sample_email}
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_unregister_can_be_registered_again(self, client, sample_activity_name, sample_email):
        """Después de desregistrarse, se debe poder volver a registrar"""
        # Registrar
        client.post(
            f"/activities/{sample_activity_name}/signup",
            params={"email": sample_email}
        )
        
        # Desregistrar
        client.delete(
            f"/activities/{sample_activity_name}/unregister",
            params={"email": sample_email}
        )
        
        # Volver a registrar (debe ser exitoso)
        response = client.post(
            f"/activities/{sample_activity_name}/signup",
            params={"email": sample_email}
        )
        assert response.status_code == 200


class TestIntegration:
    """Tests de integración con múltiples operaciones"""

    def test_full_signup_unregister_flow(self, client, sample_activity_name):
        """Test completo: registrar 3 estudiantes y desregistrar uno"""
        emails = ["email1@mergington.edu", "email2@mergington.edu", "email3@mergington.edu"]
        
        # Registrar todos
        for email in emails:
            client.post(
                f"/activities/{sample_activity_name}/signup",
                params={"email": email}
            )
        
        # Verificar que los 3 están registrados
        response = client.get("/activities")
        participants = response.json()[sample_activity_name]["participants"]
        assert len(participants) == 3
        
        # Desregistrar uno
        client.delete(
            f"/activities/{sample_activity_name}/unregister",
            params={"email": emails[0]}
        )
        
        # Verificar que quedan 2
        response = client.get("/activities")
        participants = response.json()[sample_activity_name]["participants"]
        assert len(participants) == 2
        assert emails[0] not in participants
        assert emails[1] in participants
        assert emails[2] in participants

    def test_multiple_activities_independent(self, client):
        """Registrarse en una actividad no debe afectar a otras"""
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"
        
        # Registrar mismo email en actividades diferentes
        client.post("/activities/Chess Club/signup", params={"email": email1})
        client.post("/activities/Programming Class/signup", params={"email": email1})
        client.post("/activities/Gym Class/signup", params={"email": email2})
        
        # Verificar que cada actividad tiene sus propios participantes
        response = client.get("/activities")
        data = response.json()
        
        assert email1 in data["Chess Club"]["participants"]
        assert email1 in data["Programming Class"]["participants"]
        assert email1 not in data["Gym Class"]["participants"]
        
        assert email2 in data["Gym Class"]["participants"]
        assert email2 not in data["Chess Club"]["participants"]
