"""
Tests for edge cases, error handling, and validation

Tests follow the AAA (Arrange-Act-Assert) pattern.
"""

import pytest


class TestEdgeCasesAndValidation:
    """Test suite for edge cases and error scenarios"""

    def test_empty_email_signup(self, client, reset_activities):
        """
        Test signup with empty email parameter.
        
        ARRANGE: Prepare signup request with empty email
        ACT: POST signup with empty email string
        ASSERT: Verify endpoint handles empty email gracefully
        """
        # ARRANGE
        activity_name = "Chess Club"
        empty_email = ""
        
        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": empty_email}
        )
        
        # ASSERT - Should either reject or handle gracefully
        assert response.status_code in [200, 400]

    def test_empty_email_unregister(self, client, reset_activities):
        """
        Test unregister with empty email parameter.
        
        ARRANGE: Prepare unregister request with empty email
        ACT: POST unregister with empty email string
        ASSERT: Verify endpoint handles empty email gracefully
        """
        # ARRANGE
        activity_name = "Chess Club"
        empty_email = ""
        
        # ACT
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": empty_email}
        )
        
        # ASSERT
        assert response.status_code in [400, 404]

    def test_whitespace_in_email_signup(self, client, reset_activities):
        """
        Test signup with whitespace in email.
        
        ARRANGE: Prepare signup with email containing spaces
        ACT: POST signup with whitespace email
        ASSERT: Verify handling of whitespace in email
        """
        # ARRANGE
        activity_name = "Art Club"
        email_with_spaces = "  student@mergington.edu  "
        
        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email_with_spaces}
        )
        
        # ASSERT - Should either trim or reject
        # The current implementation will treat it as a different email
        assert response.status_code in [200, 400]

    def test_activity_name_case_sensitivity(self, client, reset_activities):
        """
        Test that activity names are case-sensitive.
        
        ARRANGE: Use different case for activity name
        ACT: Try to access activity with wrong case
        ASSERT: Verify case-sensitive matching (should return 404)
        """
        # ARRANGE
        correct_name = "Chess Club"
        wrong_case_name = "chess club"
        email = "student@mergington.edu"
        
        # ACT
        response = client.post(
            f"/activities/{wrong_case_name}/signup",
            params={"email": email}
        )
        
        # ASSERT
        assert response.status_code == 404

    def test_special_characters_in_email(self, client, reset_activities):
        """
        Test signup with special characters in email.
        
        ARRANGE: Prepare email with special characters
        ACT: POST signup with special character email
        ASSERT: Verify handling of special characters
        """
        # ARRANGE
        activity_name = "Science Club"
        special_email = "student+test@mergington.edu"
        
        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": special_email}
        )
        
        # ASSERT - Should succeed (valid email format)
        assert response.status_code == 200
        
        from src.app import activities
        assert special_email in activities[activity_name]["participants"]

    def test_very_long_email(self, client, reset_activities):
        """
        Test signup with very long email address.
        
        ARRANGE: Create an extremely long email address
        ACT: POST signup with long email
        ASSERT: Verify handling of long email
        """
        # ARRANGE
        activity_name = "Debate Club"
        long_email = "a" * 100 + "@mergington.edu"
        
        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": long_email}
        )
        
        # ASSERT - Should succeed (valid email format, just long)
        assert response.status_code == 200

    def test_unicode_email(self, client, reset_activities):
        """
        Test signup with unicode characters in email.
        
        ARRANGE: Create email with unicode characters
        ACT: POST signup with unicode email
        ASSERT: Verify handling of unicode email
        """
        # ARRANGE
        activity_name = "Track and Field"
        unicode_email = "café@mergington.edu"
        
        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": unicode_email}
        )
        
        # ASSERT - Should handle unicode gracefully
        assert response.status_code in [200, 400]

    def test_max_participants_enforcement(self, client, reset_activities, test_emails):
        """
        Test that max_participants limit is strictly enforced.
        
        ARRANGE: Set activity max to 1 and fill it
        ACT: Try to add a second participant
        ASSERT: Verify second signup is rejected
        """
        # ARRANGE
        activity_name = "Basketball Team"
        from src.app import activities
        
        activity = activities[activity_name]
        activity["max_participants"] = 1
        activity["participants"] = ["first@mergington.edu"]
        
        second_email = test_emails["new_student"]
        
        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": second_email}
        )
        
        # ASSERT
        assert response.status_code == 400
        assert "full" in response.json()["detail"].lower()

    def test_zero_max_participants(self, client, reset_activities, test_emails):
        """
        Test activity with zero max_participants (edge case).
        
        ARRANGE: Set max_participants to 0
        ACT: Try to sign up
        ASSERT: Verify signup is rejected
        """
        # ARRANGE
        activity_name = "Art Club"
        from src.app import activities
        
        activity = activities[activity_name]
        activity["max_participants"] = 0
        activity["participants"] = []
        
        email = test_emails["new_student"]
        
        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # ASSERT
        assert response.status_code == 400

    def test_participant_count_consistency(self, client, reset_activities, test_emails):
        """
        Test that participant count remains accurate through operations.
        
        ARRANGE: Perform series of signups and unregisters
        ACT: Track participant count through operations
        ASSERT: Verify count is always accurate
        """
        # ARRANGE
        activity_name = "Drama Club"
        from src.app import activities
        
        emails = [test_emails["new_student"], test_emails["another_student"]]
        activity = activities[activity_name]
        initial_count = len(activity["participants"])
        
        # ACT & ASSERT
        # Sign up first
        client.post(f"/activities/{activity_name}/signup", params={"email": emails[0]})
        assert len(activity["participants"]) == initial_count + 1
        
        # Sign up second
        client.post(f"/activities/{activity_name}/signup", params={"email": emails[1]})
        assert len(activity["participants"]) == initial_count + 2
        
        # Unregister first
        client.post(f"/activities/{activity_name}/unregister", params={"email": emails[0]})
        assert len(activity["participants"]) == initial_count + 1
        
        # Unregister second
        client.post(f"/activities/{activity_name}/unregister", params={"email": emails[1]})
        assert len(activity["participants"]) == initial_count

    def test_error_message_clarity(self, client, reset_activities):
        """
        Test that error messages are clear and helpful.
        
        ARRANGE: Trigger various error conditions
        ACT: Collect error messages
        ASSERT: Verify messages are descriptive
        """
        # ARRANGE
        invalid_activity = "Nonexistent"
        existing_participant = "michael@mergington.edu"
        activity_name = "Chess Club"
        
        # ACT & ASSERT - Invalid activity
        response = client.post(
            f"/activities/{invalid_activity}/signup",
            params={"email": "test@mergington.edu"}
        )
        assert response.status_code == 404
        assert response.json()["detail"] != ""
        
        # ACT & ASSERT - Duplicate signup
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": existing_participant}
        )
        assert response.status_code == 400
        assert response.json()["detail"] != ""

    def test_response_message_content(self, client, reset_activities, test_emails):
        """
        Test that success response messages contain relevant information.
        
        ARRANGE: Perform signup action
        ACT: Check response message content
        ASSERT: Verify message includes activity name and email
        """
        # ARRANGE
        activity_name = "Gym Class"
        email = test_emails["new_student"]
        
        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # ASSERT
        assert response.status_code == 200
        message = response.json()["message"]
        assert email in message
        assert activity_name in message

    def test_concurrent_signup_simulation(self, client, reset_activities, test_emails):
        """
        Test that multiple rapid signups are handled correctly.
        
        ARRANGE: Prepare multiple signup requests
        ACT: Execute signup requests in sequence
        ASSERT: Verify all succeed without conflicts
        """
        # ARRANGE
        activity_name = "Track and Field"
        emails = [
            test_emails["new_student"],
            test_emails["another_student"],
            test_emails["third_student"]
        ]
        
        from src.app import activities
        activity = activities[activity_name]
        activity["max_participants"] = 10  # Ensure space for all
        
        # ACT
        responses = []
        for email in emails:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            responses.append(response)
        
        # ASSERT
        for response in responses:
            assert response.status_code == 200
        
        # Verify all were added
        for email in emails:
            assert email in activity["participants"]
