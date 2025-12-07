#!/bin/bash
# Script to test email endpoint
# First gets admin JWT token, then tests email endpoint

BASE_URL="http://localhost:8000"
ADMIN_EMAIL="${ADMIN_EMAIL:-admin@nikofree.com}"
ADMIN_PASSWORD="${ADMIN_PASSWORD:-admin123}"  # Change this to your admin password

echo "🔐 Step 1: Getting admin JWT token..."
echo "   Email: $ADMIN_EMAIL"
echo ""

# Login as admin
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/admin/login" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$ADMIN_EMAIL\",
    \"password\": \"$ADMIN_PASSWORD\"
  }")

# Check if login was successful
if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
  # Extract access token
  ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
  
  if [ -z "$ACCESS_TOKEN" ]; then
    echo "❌ Failed to extract access token from response:"
    echo "$LOGIN_RESPONSE"
    exit 1
  fi
  
  echo "✅ Login successful!"
  echo "   Token: ${ACCESS_TOKEN:0:50}..."
  echo ""
  
  # Get email from user or use default
  TEST_EMAIL="${1:-$ADMIN_EMAIL}"
  
  echo "📧 Step 2: Testing email endpoint..."
  echo "   Sending test email to: $TEST_EMAIL"
  echo ""
  
  # Test email endpoint
  EMAIL_RESPONSE=$(curl -s -X POST "$BASE_URL/api/admin/test-email" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
      \"email\": \"$TEST_EMAIL\"
    }")
  
  echo "Response:"
  echo "$EMAIL_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$EMAIL_RESPONSE"
  echo ""
  
  if echo "$EMAIL_RESPONSE" | grep -q "Test email sent"; then
    echo "✅ Email test successful!"
    echo "   Check your inbox and spam folder for the test email."
  else
    echo "❌ Email test failed. Check the error message above."
  fi
  
else
  echo "❌ Login failed!"
  echo "Response:"
  echo "$LOGIN_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$LOGIN_RESPONSE"
  echo ""
  echo "💡 Make sure:"
  echo "   1. Server is running on $BASE_URL"
  echo "   2. Admin user exists with email: $ADMIN_EMAIL"
  echo "   3. Password is correct (set ADMIN_PASSWORD env var if different)"
  exit 1
fi

