# Bugfix Requirements Document

## Introduction

The chat interface fails for all user queries with the error message "Sorry, I encountered an error. Please try again." This prevents users from getting responses to any questions about government services (e.g., "how to change the aadhaar name"). 

The root cause is a CORS (Cross-Origin Resource Sharing) misconfiguration in the backend API. The error logs show:
- 404 error from the Railway backend API
- CORS policy blocking: "No 'Access-Control-Allow-Origin' header is present on the requested resource"
- Network error when the frontend (Vercel) attempts to communicate with the backend (Railway)

The backend CORS middleware in `backend/app/main.py` incorrectly uses both `allow_origin_regex` and `allow_origins` parameters simultaneously, which causes undefined behavior and CORS request failures.

## Bug Analysis

### Current Behavior (Defect)

1.1 WHEN a user submits any chat message from the Vercel-hosted frontend THEN the backend API returns a CORS error and blocks the request

1.2 WHEN the CORS preflight request is sent to the Railway backend THEN the response does not include the required 'Access-Control-Allow-Origin' header

1.3 WHEN the CORSMiddleware is configured with both `allow_origin_regex` and `allow_origins` parameters THEN the middleware exhibits undefined behavior and fails to properly handle cross-origin requests

### Expected Behavior (Correct)

2.1 WHEN a user submits any chat message from the Vercel-hosted frontend THEN the backend API SHALL accept the request and return a proper response

2.2 WHEN the CORS preflight request is sent to the Railway backend THEN the response SHALL include the appropriate 'Access-Control-Allow-Origin' header matching the requesting origin

2.3 WHEN the CORSMiddleware is configured THEN it SHALL use only `allow_origins` parameter with a list containing both the Vercel domain pattern and localhost URLs for development

### Unchanged Behavior (Regression Prevention)

3.1 WHEN requests are made from localhost:3000 during local development THEN the system SHALL CONTINUE TO accept these requests

3.2 WHEN requests are made from localhost:3001 during local development THEN the system SHALL CONTINUE TO accept these requests

3.3 WHEN the API receives requests to /health or / endpoints THEN the system SHALL CONTINUE TO respond correctly

3.4 WHEN credentials are included in cross-origin requests THEN the system SHALL CONTINUE TO allow credentials

3.5 WHEN any HTTP method is used in cross-origin requests THEN the system SHALL CONTINUE TO allow all methods

3.6 WHEN any headers are included in cross-origin requests THEN the system SHALL CONTINUE TO allow all headers
