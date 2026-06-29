"""
API Tests — 7+ test cases for the Hero Missions API

Test coverage:
1.  User registration
2.  Login returns token
3.  Create hero requires authentication
4.  Create hero with token
5.  Create mission for missing hero returns 404
6.  Normal user cannot delete hero
7.  Admin can delete mission
8.  Normal user cannot create hero with level > 1
9.  Admin can create hero with custom level
10. Cannot delete hero with active missions
"""

import pytest 
from fastapi.testclient import TestClient

from app.main import app
from tests.conftest import client, test_user, test_admin

class TestAuth:
    """Authentication tests"""
    
    def test_register_user(self, client):
        """Test 1: User registration"""
        response = client.post(
            "/auth/register",
            json={
                "username": "newuser",
                "password": "newpassword123"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert "id" in data
        assert "password" not in data  # Should not return password
    
    def test_login_returns_token(self, client):
        """Test 2: Login returns access token"""
        # Register user first
        client.post(
            "/auth/register",
            json={
                "username": "logintest",
                "password": "loginpass123"
            }
        )
        
        # Login
        response = client.post(
            "/auth/login",
            data={
                "username": "logintest",
                "password": "loginpass123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_username(self, client):
        """Test login with invalid username"""
        response = client.post(
            "/auth/login",
            data={
                "username": "nonexistent",
                "password": "loginpass123"
            }
        )
        assert response.status_code == 401
        assert "Incorrect username or password" in response.text

    def test_login_invalid_password(self, client):
        """Test login with invalid username"""
        response = client.post(
            "/auth/login",
            data={
                "username": "nonexistent",
                "password": "wrongpass123"
            }
        )
        assert response.status_code == 401
        assert "Incorrect username or password" in response.text


class TestHeroes:
    """Hero CRUD tests"""
    
    def test_create_hero_requires_authentication(self, client):
        """Test 3: Create hero requires authentication"""
        response = client.post(
            "/heroes/",
            json={
                "name": "Unauthorized Hero",
                "power": "No token"
            }
        )
        assert response.status_code == 401
    
    def test_create_hero_with_token(self, client, test_user):
        """Test 4: Create hero with valid token"""
        response = client.post(
            "/heroes/",
            json={
                "name": "Auth Hero",
                "power": "Token Power"
            },
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Auth Hero"
        assert data["power"] == "Token Power"
        assert data["level"] == 1  # Normal users get level 1
        assert data["active"] == True
    
    def test_normal_user_cannot_create_hero_with_level(self, client, test_user):
        """Test 8: Normal user cannot set custom level"""
        response = client.post(
            "/heroes/",
            json={
                "name": "Level Hero",
                "power": "Test Power",
                "level": 50,  # Trying to set level
                "active": False  # Trying to set active
            },
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
        # Should succeed but level will be ignored/forced to 1
        assert response.status_code == 201
        data = response.json()
        assert data["level"] == 1  # Forced to 1
        assert data["active"] == True  # Forced to True
    
    def test_admin_can_create_hero_with_custom_level(self, client, test_admin):
        """Test 9: Admin can create hero with custom level"""
        response = client.post(
            "/heroes/",
            json={
                "name": "Admin Hero",
                "power": "Admin Power",
                "level": 75,
                "active": False
            },
            headers={"Authorization": f"Bearer {test_admin['token']}"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["level"] == 75
        assert data["active"] == False
    
    def test_get_heroes_public(self, client, test_user):
        """Test list heroes is public"""
        # Create a heroes first
        client.post(
            "/heroes/",
            json={
                "name": "Public Hero",
                "power": "Public Power"
            },
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )

        client.post(
            "/heroes/",
            json={
                "name": "Level Hero",
                "power": "Test Power", 
            },
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
        
        # Public GET should work without token
        response = client.get("/heroes/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
    
    def test_get_hero_by_id_public(self, client, test_hero):
        """Test get hero by ID is public"""
        response = client.get(f"/heroes/{test_hero['id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Hero"
    
    def test_normal_user_cannot_delete_hero(self, client, test_user, test_hero):
        """Test 6: Normal user cannot delete hero"""
        # Try to delete the hero created by test_hero fixture
        response = client.delete(
            f"/heroes/{test_hero['id']}",
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
        assert response.status_code == 403  # Forbidden
    
    def test_normal_user_cannot_update_hero_level(self, client, test_user, test_hero):
        """Test normal user cannot update hero level"""
        response = client.patch(
            f"/heroes/{test_hero['id']}",
            json={
                "level": 99  # Trying to change level
            },
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
        # Should succeed but level unchanged
        assert response.status_code == 200
        data = response.json()
        assert data["level"] == 1  # Still level 1 (from fixture)
    
    def test_normal_user_can_update_hero_name(self, client, test_user, test_hero):
        """Test normal user can update hero name and power"""
        response = client.patch(
            f"/heroes/{test_hero['id']}",
            json={
                "name": "Updated Hero Name",
                "power": "Updated Power"
            },
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Hero Name"
        assert data["power"] == "Updated Power"
    
    def test_admin_can_delete_hero(self, client, test_admin, test_hero):
        """Test admin can delete hero with no missions"""
        response = client.delete(
            f"/heroes/{test_hero['id']}",
            headers={"Authorization": f"Bearer {test_admin['token']}"}
        )
        assert response.status_code == 204  # No content

class TestMissions:
    """Mission CRUD tests"""
    
    def test_create_mission_for_missing_hero_returns_404(self, client, test_user):
        """Test 5: Create mission for missing hero returns 404"""
        response = client.post(
            "/missions/",
            json={
                "title": "Impossible Mission",
                "difficulty": 5,
                "hero_id": 99999  # Non-existent hero
            },
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
        assert response.status_code == 404
        assert "Hero not found" in response.text
    
    def test_create_mission_with_valid_hero(self, client, test_user, test_hero):
        """Test create mission for existing hero"""
        response = client.post(
            "/missions/",
            json={
                "title": "Save the City",
                "difficulty": 7,
                "hero_id": test_hero["id"]
            },
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Save the City"
        assert data["difficulty"] == 7
        assert data["completed"] == False
        assert data["hero_id"] == test_hero["id"]
    
    def test_get_missions_public(self, client, test_user, test_hero):
        """Test list missions is public"""
        # Create missions first
        client.post(
            "/missions/",
            json={
                "title": "Public Mission",
                "difficulty": 3,
                "hero_id": test_hero["id"]
            },
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )

        client.post(
            "/missions/",
            json={
                "title": "Public second Mission",
                "difficulty": 4,
                "hero_id": test_hero["id"]
            },
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
        
        # Public GET should work without token
        response = client.get("/missions/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
    
    def test_update_mission(self, client, test_user, test_hero):
        """Test update mission"""
        # Create mission
        create = client.post(
            "/missions/",
            json={
                "title": "Update This Mission",
                "difficulty": 5,
                "hero_id": test_hero["id"]
            },
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
        assert create.status_code == 201
        mission_id = create.json()["id"]
        
        # Update mission
        response = client.patch(
            f"/missions/{mission_id}",
            json={
                "title": "Updated Mission Title",
                "difficulty": 8,
                "completed": True
            },
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Mission Title"
        assert data["difficulty"] == 8
        assert data["completed"] == True
    
    def test_normal_user_cannot_delete_mission(self, client, test_user, test_hero):
        """Test normal user cannot delete mission"""
        # Create mission
        create = client.post(
            "/missions/",
            json={
                "title": "Mission to Delete",
                "difficulty": 3,
                "hero_id": test_hero["id"]
            },
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
        assert create.status_code == 201
        mission_id = create.json()["id"]
        
        # Try to delete
        response = client.delete(
            f"/missions/{mission_id}",
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
        assert response.status_code == 403  # Forbidden
    
    def test_admin_can_delete_mission(self, client, test_admin, test_hero):
        """Test 7: Admin can delete mission"""
        # First create a user to create mission
        user = client.post(
            "/auth/register",
            json={
                "username": "missioncreator",
                "password": "mission123"
            }
        )
        assert user.status_code == 201
        
        # Login as user
        login = client.post(
            "/auth/login",
            data={
                "username": "missioncreator",
                "password": "mission123"
            }
        )
        assert login.status_code == 200
        user_token = login.json()["access_token"]
        
        # Create mission
        create = client.post(
            "/missions/",
            json={
                "title": "Admin Delete This",
                "difficulty": 4,
                "hero_id": test_hero["id"]
            },
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert create.status_code == 201
        mission_id = create.json()["id"]
        
        # Delete as admin
        response = client.delete(
            f"/missions/{mission_id}",
            headers={"Authorization": f"Bearer {test_admin['token']}"}
        )
        assert response.status_code == 204
    
    def test_cannot_delete_hero_with_active_missions(self, client, test_admin, test_hero):
        """Test 10: Cannot delete hero with active missions"""
        # Create mission for hero
        user = client.post(
            "/auth/register",
            json={
                "username": "missionuser",
                "password": "missionpass123"
            }
        )
        assert user.status_code == 201
        
        login = client.post(
            "/auth/login",
            data={
                "username": "missionuser",
                "password": "missionpass123"
            }
        )
        assert login.status_code == 200
        token = login.json()["access_token"]
        
        # Create mission
        create = client.post(
            "/missions/",
            json={
                "title": "Active Mission",
                "difficulty": 5,
                "hero_id": test_hero["id"],
                "completed": False
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert create.status_code == 201
        
        # Try to delete hero (admin required)
        response = client.delete(
            f"/heroes/{test_hero['id']}",
            headers={"Authorization": f"Bearer {test_admin['token']}"}
        )
        assert response.status_code == 400
        assert "Cannot delete hero with active missions" in response.text