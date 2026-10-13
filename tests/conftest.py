"""Pytest fixtures for Valstorm Client SDK tests."""

import pytest


@pytest.fixture
def mock_token():
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c3JfMTIzIiwib3JnX2lkIjoib3JnXzQ1NiIsImV4cCI6OTk5OTk5OTk5OX0.dummy_sig"


@pytest.fixture
def mock_base_url():
    return "http://testserver/v1"
