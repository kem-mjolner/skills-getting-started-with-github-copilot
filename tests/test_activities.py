"""
Tests for GET /activities endpoint and root endpoint

Tests follow the AAA (Arrange-Act-Assert) pattern.
"""

import pytest


class TestRootEndpoint:
    """Test suite for the root endpoint"""

    def test_root_redirects_to_static_index(self, client):
        """
        Test that GET / redirects to /static/index.html.
        
        ARRANGE: No setup needed
        ACT: Make GET request to root endpoint with follow_redirects=False
        ASSERT: Verify response is a redirect (307) to /static/index.html
        """
        # ACT
        response = client.get("/", follow_redirects=False)
        
        # ASSERT
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]


class TestGetActivities:
    """Test suite for the GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """
        Test that GET /activities returns all activities with correct structure.
        
        ARRANGE: No setup needed; using default activities from fixtures
        ACT: Make GET request to /activities endpoint
        ASSERT: Verify response status is 200 and all activities are returned
        """
        # ACT
        response = client.get("/activities")
        
        # ASSERT
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        assert len(activities) == 9
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Gym Class" in activities
        assert "Basketball Team" in activities
        assert "Track and Field" in activities
        assert "Art Club" in activities
        assert "Drama Club" in activities
        assert "Debate Club" in activities
        assert "Science Club" in activities

    def test_get_activities_has_correct_structure(self, client, reset_activities):
        """
        Test that each activity has required fields with correct types.
        
        ARRANGE: No setup needed; using default activities
        ACT: Make GET request and inspect activity structure
        ASSERT: Verify each activity has description, schedule, max_participants, participants
        """
        # ACT
        response = client.get("/activities")
        activities = response.json()
        
        # ASSERT - Check structure of each activity
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data, dict), f"{activity_name} should be a dict"
            assert "description" in activity_data, f"{activity_name} missing 'description'"
            assert "schedule" in activity_data, f"{activity_name} missing 'schedule'"
            assert "max_participants" in activity_data, f"{activity_name} missing 'max_participants'"
            assert "participants" in activity_data, f"{activity_name} missing 'participants'"
            
            # Verify field types
            assert isinstance(activity_data["description"], str)
            assert isinstance(activity_data["schedule"], str)
            assert isinstance(activity_data["max_participants"], int)
            assert isinstance(activity_data["participants"], list)

    def test_get_activities_participants_are_strings(self, client, reset_activities):
        """
        Test that all participant entries are email strings.
        
        ARRANGE: No setup needed
        ACT: Get activities and inspect participants list
        ASSERT: All participants are strings (email addresses)
        """
        # ACT
        response = client.get("/activities")
        activities = response.json()
        
        # ASSERT
        for activity_name, activity_data in activities.items():
            participants = activity_data["participants"]
            for participant in participants:
                assert isinstance(participant, str), \
                    f"{activity_name}: participant {participant} is not a string"
                assert "@" in participant, \
                    f"{activity_name}: {participant} does not look like an email"

    def test_get_activities_max_participants_positive(self, client, reset_activities):
        """
        Test that max_participants values are positive integers.
        
        ARRANGE: No setup needed
        ACT: Get activities and check max_participants values
        ASSERT: All max_participants values are positive
        """
        # ACT
        response = client.get("/activities")
        activities = response.json()
        
        # ASSERT
        for activity_name, activity_data in activities.items():
            max_participants = activity_data["max_participants"]
            assert max_participants > 0, \
                f"{activity_name}: max_participants should be positive, got {max_participants}"

    def test_get_activities_participants_within_limit(self, client, reset_activities):
        """
        Test that participant count never exceeds max_participants.
        
        ARRANGE: No setup needed
        ACT: Get activities and compare counts
        ASSERT: Verify participant count <= max_participants for all activities
        """
        # ACT
        response = client.get("/activities")
        activities = response.json()
        
        # ASSERT
        for activity_name, activity_data in activities.items():
            participant_count = len(activity_data["participants"])
            max_participants = activity_data["max_participants"]
            assert participant_count <= max_participants, \
                f"{activity_name}: {participant_count} participants exceeds max {max_participants}"
