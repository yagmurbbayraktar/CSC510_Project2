from src.app import app, add, mongodb_client
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for  # noqa: E402

db = mongodb_client.db


def test_upload():
    """
    This test verifies that the upload page works correctly
    """

    assert (render_template('upload.html') == True)



def test_uploader_page():
    """
    This test verifies that search page displays the user input form correctly
    """

    response = app.test_client().get('/upload')
    assert response.status_code == 200
    assert b"Job Title" in response.data
    assert b"Location" in response.data
    assert b"Company Name" in response.data
    assert b"Technical skills" in response.data
    assert b"Job Type" in response.data
