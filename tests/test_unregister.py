"""
Tests for POST /activities/{activity_name}/unregister endpoint

Tests follow the AAA (Arrange-Act-Assert) pattern.
"""

import pytest


class TestUnregisterFromActivity:
    """Test suite for the unregister endpoint"""

    def test_unregister_success(self, client, reset_activities):
        """
        Test successful unregister from an activity.
        
        ARRANGE: Select an activity with existing participants
        ACT: POST unregister request with activity name and existing participant email
        ASSERT: Verify response status is 200 and email is removed from participants
        """
        # ARRANGE
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Existing participant
        
        from src.app import activities
        initial_count = len(activities[activity_name]["participants"])
        
        # ACT
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # ASSERT
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
        assert email in response.json()["message"]
        
        # Verify participant was removed
        assert email not in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_count - 1

    def test_unregister_invalid_activity_returns_404(self, client, reset_activities):
        """
        Test that unregister from non-existent activity returns 404.
        
        ARRANGE: Use activity name that doesn't exist
        ACT: POST unregister request with invalid activity name
        ASSERT: Verify response status is 404 and error message is clear
        """
        # ARRANGE
        invalid_activity = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        # ACT
        response = client.post(
            f"/activities/{invalid_activity}/unregister",
            params={"email": email}
        )
        
        # ASSERT
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_unregister_not_registered_returns_400(self, client, reset_activities, test_emails):
        """
        Test that unregister fails when student is not registered.
        
        ARRANGE: Select an activity and an email NOT in participants
        ACT: POST unregister request for unregistered email
        ASSERT: Verify response status is 400 and error indicates not registered
        """
        # ARRANGE
        activity_name = "Basketball Team"
        email = test_emails["new_student"]  # Not a participant
        
        # ACT
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # ASSERT
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]

    def test_unregister_multiple_participants(self, client, reset_activities):
        """
        Test that unregister removes only the specified participant.
        
        ARRANGE: Activity with multiple participants
        ACT: Unregister one participant
        ASSERT: Verify only that participant is removed; others remain
        """
        # ARRANGE
        activity_name = "Chess Club"
        email_to_remove = "michael@mergington.edu"
        email_to_keep = "daniel@mergington.edu"
        
        from src.app import activities
        
        # ACT
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email_to_remove}
        )
        
        # ASSERT
        assert response.status_code == 200
        participants = activities[activity_name]["participants"]
        
        # Removed email should not be present
        assert email_to_remove not in participants
        
        # Other participant should still be present
        assert email_to_keep in participants

    def test_unregister_then_signup_again(self, client, reset_activities):
        """
        Test that after unregistering, a student can sign up again.
        
        ARRANGE: Activity with existing participant
        ACT: Unregister student, then sign up same student again
        ASSERT: Verify student appears in participants after re-signup
        """
        # ARRANGE
        activity_name = "Gym Class"
        email = "john@mergington.edu"  # Existing participant
        
        from src.app import activities
        
        # Verify initially in participants
        assert email in activities[activity_name]["participants"]
        
        # ACT - Unregister
        response_unregister = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # ACT - Sign up again
        response_signup = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # ASSERT
        assert response_unregister.status_code == 200
        assert response_signup.status_code == 200
        assert email in activities[activity_name]["participants"]

    def test_unregister_frees_up_capacity(self, client, reset_activities, test_emails):
        """
        Test that unregistering frees up space for new signups.
        
        ARRANGE: Fill an activity to capacity, then unregister one person
        ACT: Try to sign up another person after freeing space
        ASSERT: Verify the signup succeeds after unregister
        """
        # ARRANGE
        activity_name = "Drama Club"
        from src.app import activities
        
        activity = activities[activity_name]
        # Fill activity to max capacity
        activity["max_participants"] = 2
        activity["participants"] = ["person1@mergington.edu", "person2@mergington.edu"]
        
        person_to_remove = "person1@mergington.edu"
        new_person = test_emails["new_student"]
        
        # Verify activity is full
        assert len(activity["participants"]) >= activity["max_participants"]
        
        # ACT - Unregister one person
        response_unregister = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": person_to_remove}
        )
        
        # ACT - Try to sign up new person
        response_signup = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_person}
        )
        
        # ASSERT
        assert response_unregister.status_code == 200
        assert response_signup.status_code == 200
        assert new_person in activities[activity_name]["participants"]
        assert person_to_remove not in activities[activity_name]["participants"]

    def test_unregister_all_participants(self, client, reset_activities):
        """
        Test that all participants can be unregistered from an activity.
        
        ARRANGE: Activity with multiple participants
        ACT: Unregister each participant one by one
        ASSERT: Verify activity ends up with empty participants list
        """
        # ARRANGE
        activity_name = "Programming Class"
        from src.app import activities
        
        activity = activities[activity_name]
        participants_to_remove = list(activity["participants"])  # Make a copy
        
        # ACT & ASSERT - Remove each participant
        for email in participants_to_remove:
            response = client.post(
                f"/activities/{activity_name}/unregister",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Final assertion - activity should have no participants
        assert len(activities[activity_name]["participants"]) == 0
