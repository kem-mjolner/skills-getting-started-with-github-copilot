"""
Tests for POST /activities/{activity_name}/signup endpoint

Tests follow the AAA (Arrange-Act-Assert) pattern.
"""

import pytest


class TestSignupForActivity:
    """Test suite for the signup endpoint"""

    def test_signup_success(self, client, reset_activities, test_emails):
        """
        Test successful signup for an activity.
        
        ARRANGE: Select an activity with available space and a new email
        ACT: POST signup request with activity name and email
        ASSERT: Verify response status is 200 and email is added to participants
        """
        # ARRANGE
        activity_name = "Basketball Team"
        email = test_emails["new_student"]
        initial_count = len(
            [a for a in __import__("src.app", fromlist=["activities"]).activities[activity_name]["participants"]]
        )
        
        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # ASSERT
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert email in response.json()["message"]
        
        # Verify participant was added
        from src.app import activities
        assert email in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_count + 1

    def test_signup_invalid_activity_returns_404(self, client, reset_activities, test_emails):
        """
        Test that signup to non-existent activity returns 404.
        
        ARRANGE: Use activity name that doesn't exist and a valid email
        ACT: POST signup request with invalid activity name
        ASSERT: Verify response status is 404 and error message is clear
        """
        # ARRANGE
        invalid_activity = "Nonexistent Activity"
        email = test_emails["new_student"]
        
        # ACT
        response = client.post(
            f"/activities/{invalid_activity}/signup",
            params={"email": email}
        )
        
        # ASSERT
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_duplicate_email_returns_400(self, client, reset_activities):
        """
        Test that duplicate signup is rejected with 400.
        
        ARRANGE: Select an activity and an email already in participants
        ACT: POST signup request for already-registered email
        ASSERT: Verify response status is 400 and error indicates duplicate
        """
        # ARRANGE
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already a participant
        
        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # ASSERT
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_activity_full_returns_400(self, client, reset_activities, test_emails):
        """
        Test that signup is rejected when activity is at capacity.
        
        ARRANGE: Create an activity with only one available spot, fill it,
                 then try to add another participant
        ACT: Sign up until activity is full, then attempt one more signup
        ASSERT: Verify the final signup returns 400 with full activity error
        """
        # ARRANGE - Use Debate Club which has max 16 and currently 0 participants
        activity_name = "Debate Club"
        from src.app import activities
        
        # Fill the activity to capacity
        activity = activities[activity_name]
        original_max = activity["max_participants"]
        activity["max_participants"] = 1  # Set max to 1
        activity["participants"] = ["existing@mergington.edu"]  # Fill to capacity
        
        new_email = test_emails["new_student"]
        
        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_email}
        )
        
        # ASSERT
        assert response.status_code == 400
        assert "full" in response.json()["detail"].lower()

    def test_signup_multiple_users_same_activity(self, client, reset_activities, test_emails):
        """
        Test that multiple different users can sign up for the same activity.
        
        ARRANGE: Select an activity with space for multiple signups
        ACT: Sign up multiple different users sequentially
        ASSERT: Verify all users are added to participants list
        """
        # ARRANGE
        activity_name = "Track and Field"
        emails = [test_emails["new_student"], test_emails["another_student"]]
        
        from src.app import activities
        initial_participants = list(activities[activity_name]["participants"])
        
        # ACT - Sign up first user
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": emails[0]}
        )
        
        # ACT - Sign up second user
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": emails[1]}
        )
        
        # ASSERT
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Both should be in participants
        participants = activities[activity_name]["participants"]
        assert emails[0] in participants
        assert emails[1] in participants
        assert len(participants) == len(initial_participants) + 2

    def test_signup_different_activities(self, client, reset_activities, test_emails):
        """
        Test that a user can sign up for multiple different activities.
        
        ARRANGE: Select two different activities and one email
        ACT: Sign up the same user for both activities
        ASSERT: Verify user appears in both activity participant lists
        """
        # ARRANGE
        activity1 = "Art Club"
        activity2 = "Science Club"
        email = test_emails["new_student"]
        
        from src.app import activities
        
        # ACT
        response1 = client.post(
            f"/activities/{activity1}/signup",
            params={"email": email}
        )
        response2 = client.post(
            f"/activities/{activity2}/signup",
            params={"email": email}
        )
        
        # ASSERT
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert email in activities[activity1]["participants"]
        assert email in activities[activity2]["participants"]
