#!/usr/bin/env python3
"""
Main entry point for running the WikiContest Flask application.

This script starts the Flask API server.

Note: Database migrations are handled separately by Alembic.
"""

# Local application imports
from app import app

if __name__ == '__main__':
    # Main application entry point.
    # This section runs when the script is executed directly (not imported).

    # Start the Flask server
    # Debug mode is enabled for development (disable in production)
    print("🚀 Starting WikiContest API server...")
    print("📡 Server will be available at: http://localhost:5000")
    print("🔧 Debug mode: ENABLED")

    app.run(
        debug=True,        # Enable debug mode for development
        host='0.0.0.0',    # Allow connections from any IP
        port=5000          # Default Flask development port
    )

