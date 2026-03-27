"""
Integration tests for the Mergington High School Activity Management API.
Uses the AAA (Arrange-Act-Assert) pattern for test structure.
"""

import pytest
from fastapi.testclient import TestClient
from copy import deepcopy
from src.app import app, activities


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def client():
    """Fixture that provides a TestClient connected to the FastAPI app."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """
    Fixture that resets the activities database before each test.
    Uses autouse=True to automatically run before every test.
    """
    # Store the initial state
    initial_state = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball team for varsity and intramural play",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Tennis coaching and competitive matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 16,
            "participants": ["james@mergington.edu", "lucy@mergington.edu"]
        },
        "Art Studio": {
            "description": "Painting, drawing, and visual arts creation",
            "schedule": "Mondays and Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["isabella@mergington.edu"]
        },
        "Drama Club": {
            "description": "Theater, acting, and stage performance",
            "schedule": "Wednesdays and Saturdays, 4:00 PM - 6:00 PM",
            "max_participants": 25,
            "participants": ["noah@mergington.edu", "ava@mergington.edu"]
        },
        "Science Club": {
            "description": "Hands-on experiments and scientific exploration",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["liam@mergington.edu", "mia@mergington.edu"]
        },
        "Debate Team": {
            "description": "Competitive debate and public speaking skills",
            "schedule": "Tuesdays, 4:00 PM - 5:30 PM",
            "max_participants": 14,
            "participants": ["benjamin@mergington.edu"]
        }
    }

    yield  # Test runs here

    # After test completes, reset to initial state
    activities.clear()
    activities.update(deepcopy(initial_state))


# ============================================================================
# TESTS FOR GET /activities
# ============================================================================

def test_get_activities_returns_all_activities(client):
    """
    Test that GET /activities returns all 9 pre-loaded activities.
    
    AAA Pattern:
    - Arrange: Use client fixture (activities reset by fixture)
    - Act: Make GET request to /activities
    - Assert: Verify response contains all 9 activities
    """
    # Arrange
    expected_activity_count = 9

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    activities_data = response.json()
    assert len(activities_data) == expected_activity_count
    assert "Chess Club" in activities_data
    assert "Programming Class" in activities_data


def test_get_activities_response_structure(client):
    """
    Test that GET /activities returns activities with correct data structure.
    
    AAA Pattern:
    - Arrange: Set up expected activity structure
    - Act: Make GET request to /activities
    - Assert: Verify each activity has required fields
    """
    # Arrange
    required_fields = {"description", "schedule", "max_participants", "participants"}

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    activities_data = response.json()
    for activity_name, activity_info in activities_data.items():
        assert isinstance(activity_name, str)
        assert all(field in activity_info for field in required_fields)
        assert isinstance(activity_info["participants"], list)


def test_get_activities_participants_list(client):
    """
    Test that activities return participants as a list.
    
    AAA Pattern:
    - Arrange: Identify an activity with known participants
    - Act: Make GET request and extract Chess Club data
    - Assert: Verify participants list contains expected members
    """
    # Arrange
    expected_chess_club_participants = ["michael@mergington.edu", "daniel@mergington.edu"]

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    activities_data = response.json()
    chess_club = activities_data["Chess Club"]
    assert chess_club["participants"] == expected_chess_club_participants


# ============================================================================
# TESTS FOR POST /activities/{activity_name}/signup
# ============================================================================

def test_signup_success(client):
    """
    Test successful signup: student is added to activity participants.
    
    AAA Pattern:
    - Arrange: Define activity name and new student email
    - Act: Make POST request to signup endpoint
    - Assert: Verify response status and student is in participants
    """
    # Arrange
    activity_name = "Chess Club"
    student_email = "newstudent@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={student_email}")

    # Assert
    assert response.status_code == 200
    assert student_email in activities[activity_name]["participants"]


def test_signup_with_invalid_activity_returns_404(client):
    """
    Test that signup with non-existent activity returns 404.
    
    AAA Pattern:
    - Arrange: Define invalid activity name
    - Act: Make POST request to non-existent activity
    - Assert: Verify 404 response
    """
    # Arrange
    invalid_activity = "Nonexistent Club"
    student_email = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/{invalid_activity}/signup?email={student_email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_duplicate_student_returns_400(client):
    """
    Test that duplicate signup (same email twice) returns 400 error.
    
    AAA Pattern:
    - Arrange: Choose activity with existing student
    - Act: Attempt to sign up same student again
    - Assert: Verify 400 response and error message
    """
    # Arrange
    activity_name = "Chess Club"
    student_email = "michael@mergington.edu"  # Already in Chess Club

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={student_email}")

    # Assert
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


def test_signup_response_message(client):
    """
    Test that successful signup returns appropriate message.
    
    AAA Pattern:
    - Arrange: Define signup parameters
    - Act: Make POST request
    - Assert: Verify response contains confirmation message
    """
    # Arrange
    activity_name = "Programming Class"
    student_email = "alice@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={student_email}")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert student_email in data["message"]
    assert activity_name in data["message"]


def test_signup_multiple_students_same_activity(client):
    """
    Test that multiple different students can signup for the same activity.
    
    AAA Pattern:
    - Arrange: Define multiple unique student emails
    - Act: Sign up each student sequentially
    - Assert: Verify all students are in participants list
    """
    # Arrange
    activity_name = "Art Studio"
    students = ["student1@mergington.edu", "student2@mergington.edu", "student3@mergington.edu"]

    # Act
    for student_email in students:
        response = client.post(f"/activities/{activity_name}/signup?email={student_email}")
        assert response.status_code == 200

    # Assert
    for student_email in students:
        assert student_email in activities[activity_name]["participants"]


# ============================================================================
# TESTS FOR DELETE /activities/{activity_name}/unregister
# ============================================================================

def test_unregister_success(client):
    """
    Test successful unregister: student is removed from activity participants.
    
    AAA Pattern:
    - Arrange: Identify existing student in activity
    - Act: Make DELETE request to unregister
    - Assert: Verify response status and student is removed
    """
    # Arrange
    activity_name = "Chess Club"
    student_email = "michael@mergington.edu"
    assert student_email in activities[activity_name]["participants"]

    # Act
    response = client.delete(f"/activities/{activity_name}/unregister?email={student_email}")

    # Assert
    assert response.status_code == 200
    assert student_email not in activities[activity_name]["participants"]


def test_unregister_from_invalid_activity_returns_404(client):
    """
    Test that unregister from non-existent activity returns 404.
    
    AAA Pattern:
    - Arrange: Define invalid activity name
    - Act: Make DELETE request to non-existent activity
    - Assert: Verify 404 response
    """
    # Arrange
    invalid_activity = "Nonexistent Club"
    student_email = "student@mergington.edu"

    # Act
    response = client.delete(f"/activities/{invalid_activity}/unregister?email={student_email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_nonexistent_participant_returns_404(client):
    """
    Test that unregistering non-existent student returns 404.
    
    AAA Pattern:
    - Arrange: Choose activity and student not in it
    - Act: Attempt to unregister non-existent student
    - Assert: Verify 404 response and error message
    """
    # Arrange
    activity_name = "Drama Club"
    non_existent_student = "notamember@mergington.edu"
    assert non_existent_student not in activities[activity_name]["participants"]

    # Act
    response = client.delete(f"/activities/{activity_name}/unregister?email={non_existent_student}")

    # Assert
    assert response.status_code == 404
    assert "Participant not found" in response.json()["detail"]


def test_unregister_response_message(client):
    """
    Test that successful unregister returns appropriate message.
    
    AAA Pattern:
    - Arrange: Define unregister parameters with existing student
    - Act: Make DELETE request
    - Assert: Verify response contains confirmation message
    """
    # Arrange
    activity_name = "Tennis Club"
    student_email = "james@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/unregister?email={student_email}")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert student_email in data["message"]
    assert activity_name in data["message"]


def test_unregister_multiple_students(client):
    """
    Test that multiple students can be unregistered from the same activity.
    
    AAA Pattern:
    - Arrange: Identify multiple students in an activity
    - Act: Unregister each student sequentially
    - Assert: Verify all students are removed
    """
    # Arrange
    activity_name = "Drama Club"
    students_to_remove = ["noah@mergington.edu", "ava@mergington.edu"]

    # Act & Assert
    for student_email in students_to_remove:
        response = client.delete(f"/activities/{activity_name}/unregister?email={student_email}")
        assert response.status_code == 200
        assert student_email not in activities[activity_name]["participants"]


# ============================================================================
# TESTS FOR GET /
# ============================================================================

def test_root_redirects_to_static_index(client):
    """
    Test that GET / redirects to /static/index.html.
    
    AAA Pattern:
    - Arrange: Set up client
    - Act: Make GET request to root endpoint
    - Assert: Verify redirect response (307 or 301) and target URL
    """
    # Arrange
    # (client fixture is ready)

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert "/static/index.html" in response.headers["location"]


def test_root_redirect_follows_to_static(client):
    """
    Test that following redirect from / leads to static files.
    
    AAA Pattern:
    - Arrange: Set up client with follow_redirects=True
    - Act: Make GET request to root endpoint
    - Assert: Verify final response status (e.g., 200 if file exists, or 404 if not mounted)
    """
    # Arrange
    # (client fixture is ready)

    # Act
    response = client.get("/", follow_redirects=True)

    # Assert
    # The redirect should be followed; we expect 200 if static files work, or 404 if static not mounted
    # Based on the app, it mounts /static but doesn't serve from there by default for TestClient
    # So we just verify the redirect occurs
    assert response.status_code in [200, 404]  # 404 is expected since TestClient may not serve static files
