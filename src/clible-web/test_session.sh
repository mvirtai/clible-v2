#!/bin/bash
COOKIE_FILE="cookie.txt"

# Register a random user
curl -c $COOKIE_FILE -X POST -H "Content-Type: application/json" -d '{"username": "testuser_'$RANDOM'", "password": "password123"}' http://localhost:3000/api/auth/register

# Send the insight request
OUTPUT=$(curl -s -D /dev/stderr -b $COOKIE_FILE -X POST -H "Content-Type: application/json" -d '{"text": "Jesus"}' http://localhost:3000/api/ai/insight)

echo "--- RESPONSE ---"
echo $OUTPUT
