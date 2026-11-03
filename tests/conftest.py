"""
Shared pytest fixtures for testing the Mergington High School API

This module provides:
- Fresh app instance for each test
- TestClient connected to the test app
- Default test data with activities
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """
    Provide a TestClient connected to the FastAPI app.
    
    This fixture ensures each test gets a fresh client without
    any shared state between tests.
    """
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """
    Reset the activities dictionary to its initial state.
    
    This fixture runs before each test to ensure clean state
    for activity data. It captures the initial state and restores
    it after the test completes.
    """
    from src.app import activities
    
    # Store the initial activities state
    initial_activities = {
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
            "description": "Practice basketball skills and compete in team games",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": []
        },
        "Track and Field": {
            "description": "Train for running, jumping, and throwing events",
            "schedule": "Mondays and Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": []
        },
        "Art Club": {
            "description": "Explore drawing, painting, and other visual art projects",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": []
        },
        "Drama Club": {
            "description": "Develop acting skills and put on stage performances",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": []
        },
        "Debate Club": {
            "description": "Research topics and practice persuasive argumentation",
            "schedule": "Mondays, 3:30 PM - 4:30 PM",
            "max_participants": 16,
            "participants": []
        },
        "Science Club": {
            "description": "Investigate scientific questions through experiments and projects",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": []
        }
    }
    
    yield
    
    # After test completes, restore to initial state
    activities.clear()
    activities.update(initial_activities)


@pytest.fixture
def activity_names():
    """
    Provide a list of all valid activity names for testing.
    
    Useful for parameterized tests and as a reference for
    valid activity names that exist in the activities dictionary.
    """
    return [
        "Chess Club",
        "Programming Class",
        "Gym Class",
        "Basketball Team",
        "Track and Field",
        "Art Club",
        "Drama Club",
        "Debate Club",
        "Science Club"
    ]


@pytest.fixture
def test_emails():
    """
    Provide test email addresses for signup/unregister tests.
    
    These are distinct from existing participants to avoid conflicts
    during positive test cases.
    """
    return {
        "new_student": "new_student@mergington.edu",
        "another_student": "another_student@mergington.edu",
        "third_student": "third_student@mergington.edu",
        "fourth_student": "fourth_student@mergington.edu"
    }
