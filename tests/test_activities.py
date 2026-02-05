"""Tests for the Mergington High School Activities API"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state after each test"""
    # Store original state
    from app import activities
    original_state = {k: {"participants": v["participants"].copy()} 
                      for k, v in activities.items()}
    
    yield
    
    # Restore original state
    for activity_name, original_data in original_state.items():
        if activity_name in activities:
            activities[activity_name]["participants"] = original_data["participants"].copy()


class TestRoot:
    """Test the root endpoint"""
    
    def test_root_redirect(self, client):
        """Test that root redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Test the get activities endpoint"""
    
    def test_get_all_activities(self, client):
        """Test retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
        
        # Verify structure of each activity
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)
    
    def test_activities_contain_expected_activities(self, client):
        """Test that expected activities are present"""
        response = client.get("/activities")
        data = response.json()
        
        expected_activities = ["Chess Club", "Programming Class", "Gym Class", 
                              "Basketball Team", "Soccer Club", "Art Workshop", 
                              "Drama Club", "Math Olympiad Training", "Debate Club"]
        
        for activity in expected_activities:
            assert activity in data


class TestSignup:
    """Test the signup endpoint"""
    
    def test_signup_valid_student(self, client, reset_activities):
        """Test signing up a new student for an activity"""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]
    
    def test_signup_adds_participant(self, client, reset_activities):
        """Test that signup actually adds the participant"""
        email = "newstudent@mergington.edu"
        
        # Get initial participant count
        response_before = client.get("/activities")
        participants_before = response_before.json()["Chess Club"]["participants"]
        count_before = len(participants_before)
        
        # Sign up
        client.post("/activities/Chess Club/signup", params={"email": email})
        
        # Check participant was added
        response_after = client.get("/activities")
        participants_after = response_after.json()["Chess Club"]["participants"]
        count_after = len(participants_after)
        
        assert count_after == count_before + 1
        assert email in participants_after
    
    def test_signup_duplicate_student(self, client, reset_activities):
        """Test that duplicate signup raises an error"""
        # Try to sign up a student who is already signed up
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_nonexistent_activity(self, client):
        """Test signing up for non-existent activity"""
        response = client.post(
            "/activities/NonexistentActivity/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_signup_multiple_activities(self, client, reset_activities):
        """Test that a student can sign up for multiple activities"""
        email = "versatile@mergington.edu"
        
        # Sign up for first activity
        response1 = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Sign up for second activity
        response2 = client.post(
            "/activities/Programming Class/signup",
            params={"email": email}
        )
        assert response2.status_code == 200
        
        # Verify both signups
        response = client.get("/activities")
        data = response.json()
        assert email in data["Chess Club"]["participants"]
        assert email in data["Programming Class"]["participants"]


class TestUnregister:
    """Test the unregister endpoint"""
    
    def test_unregister_valid_participant(self, client, reset_activities):
        """Test unregistering an existing participant"""
        # First sign up
        email = "tempstudent@mergington.edu"
        client.post("/activities/Chess Club/signup", params={"email": email})
        
        # Then unregister
        response = client.post(
            "/activities/Chess Club/unregister",
            params={"email": email}
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        assert email in data["message"]
    
    def test_unregister_removes_participant(self, client, reset_activities):
        """Test that unregister actually removes the participant"""
        email = "tempstudent@mergington.edu"
        
        # Sign up first
        client.post("/activities/Chess Club/signup", params={"email": email})
        
        # Verify they were added
        response = client.get("/activities")
        assert email in response.json()["Chess Club"]["participants"]
        
        # Unregister
        client.post("/activities/Chess Club/unregister", params={"email": email})
        
        # Verify they were removed
        response = client.get("/activities")
        assert email not in response.json()["Chess Club"]["participants"]
    
    def test_unregister_nonexistent_activity(self, client):
        """Test unregistering from non-existent activity"""
        response = client.post(
            "/activities/NonexistentActivity/unregister",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_unregister_not_signed_up(self, client, reset_activities):
        """Test unregistering someone who isn't signed up"""
        response = client.post(
            "/activities/Chess Club/unregister",
            params={"email": "notsignup@mergington.edu"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]
    
    def test_unregister_participant_already_registered(self, client, reset_activities):
        """Test unregistering a participant who was originally registered"""
        # Try to unregister someone who is already registered
        response = client.post(
            "/activities/Chess Club/unregister",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 200
        
        # Verify they were removed
        response = client.get("/activities")
        assert "michael@mergington.edu" not in response.json()["Chess Club"]["participants"]
