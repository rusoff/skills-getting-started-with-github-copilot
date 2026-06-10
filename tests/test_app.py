"""
Unit tests for the High School Management System API (src/app.py)

Tests follow the AAA (Arrange-Act-Assert) pattern for clarity and maintainability.
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException
from src.app import app, get_activities, signup_for_activity, activities


class TestRootEndpoint:
    """Tests for the root() endpoint"""

    def test_root_returns_redirect_to_static(self):
        """Test that root() returns a redirect response to /static/index.html"""
        # Arrange
        client = TestClient(app)

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivitiesEndpoint:
    """Tests for the get_activities() endpoint"""

    def test_get_activities_returns_all_activities(self):
        """Test that get_activities() returns the complete activities dictionary"""
        # Arrange
        expected_keys = {
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Soccer Team",
            "Swimming Club",
            "Art Club",
            "Drama Club",
            "Math Olympiad",
            "Debate Team"
        }

        # Act
        result = get_activities()

        # Assert
        assert isinstance(result, dict)
        assert set(result.keys()) == expected_keys

    def test_get_activities_returns_correct_structure(self):
        """Test that each activity has required fields"""
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}

        # Act
        result = get_activities()

        # Assert
        for activity_name, activity_data in result.items():
            assert isinstance(activity_data, dict), f"{activity_name} should be a dict"
            assert required_fields.issubset(activity_data.keys()), \
                f"{activity_name} missing required fields"
            assert isinstance(activity_data["participants"], list), \
                f"{activity_name} participants should be a list"

    def test_get_activities_has_participants(self):
        """Test that activities have initial participants"""
        # Arrange
        # (no setup needed)

        # Act
        result = get_activities()

        # Assert
        for activity_name, activity_data in result.items():
            assert len(activity_data["participants"]) > 0, \
                f"{activity_name} should have at least one participant"


class TestSignupForActivityEndpoint:
    """Tests for the signup_for_activity() endpoint"""

    def test_signup_for_activity_success(self):
        """Test successful signup for an existing activity with a new email"""
        # Arrange
        activity_name = "Chess Club"
        new_email = "newstudent@mergington.edu"
        initial_count = len(activities[activity_name]["participants"])

        # Act
        response = signup_for_activity(activity_name, new_email)

        # Assert
        assert response["message"] == f"Signed up {new_email} for {activity_name}"
        assert new_email in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_count + 1

        # Cleanup: remove the test email for other tests
        activities[activity_name]["participants"].remove(new_email)

    def test_signup_for_activity_not_found(self):
        """Test signup for a non-existent activity raises 404 HTTPException"""
        # Arrange
        non_existent_activity = "NonExistent Activity"
        email = "student@mergington.edu"

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            signup_for_activity(non_existent_activity, email)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Activity not found"

    def test_signup_for_activity_already_signed_up(self):
        """Test signup for an activity when student is already enrolled raises 400 HTTPException"""
        # Arrange
        activity_name = "Chess Club"
        existing_email = activities[activity_name]["participants"][0]

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            signup_for_activity(activity_name, existing_email)

        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Student already signed up for this activity"

    def test_signup_for_activity_multiple_success_cases(self):
        """Test multiple successful signups for different activities"""
        # Arrange
        test_cases = [
            ("Programming Class", "alice@mergington.edu"),
            ("Gym Class", "bob@mergington.edu"),
            ("Art Club", "charlie@mergington.edu"),
        ]
        initial_counts = {
            activity: len(activities[activity]["participants"])
            for activity, _ in test_cases
        }

        # Act
        for activity_name, email in test_cases:
            response = signup_for_activity(activity_name, email)

        # Assert
        for activity_name, email in test_cases:
            assert email in activities[activity_name]["participants"]
            assert len(activities[activity_name]["participants"]) == initial_counts[activity_name] + 1

        # Cleanup
        for activity_name, email in test_cases:
            activities[activity_name]["participants"].remove(email)

    def test_signup_for_activity_case_sensitive_activity_name(self):
        """Test that activity names are case-sensitive"""
        # Arrange
        email = "student@mergington.edu"
        wrong_case_activity = "chess club"  # lowercase instead of "Chess Club"

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            signup_for_activity(wrong_case_activity, email)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Activity not found"
