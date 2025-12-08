#!/bin/bash
# Test email endpoint on production server
# Usage: ./test_email_production.sh [your-email@example.com]

BASE_URL="https://api.niko-free.com"
ADMIN_EMAIL="admin@nikofree.com"
ADMIN_PASSWORD="Admin@1234"
TEST_EMAIL="${1:-$ADMIN_EMAIL}"

echo "=========================================="
echo "  Email Endpoint Test - PRODUCTION"
echo "=========================================="
echo ""
echo "Step 1: Logging in as admin..."
echo "  Email: $ADMIN_EMAIL"
echo ""

# Login and get token
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/admin/login" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$ADMIN_EMAIL\",
    \"password\": \"$ADMIN_PASSWORD\"
  }")

# Check for errors
if echo "$LOGIN_RESPONSE" | grep -q '"error"'; then
  echo "❌ Login failed!"
  echo "$LOGIN_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$LOGIN_RESPONSE"
  exit 1
fi

# Extract token
ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

if [ -z "$ACCESS_TOKEN" ]; then
  echo "❌ Failed to get access token"
  echo "Response: $LOGIN_RESPONSE"
  exit 1
fi

echo "✅ Login successful!"
echo "  Token: ${ACCESS_TOKEN:0:30}..."
echo ""
echo "Step 2: Testing email endpoint on PRODUCTION..."
echo "  Sending test email to: $TEST_EMAIL"
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
  echo ""
  echo "📧 Email sent from PRODUCTION server!"
  echo "   Check your inbox and spam folder: $TEST_EMAIL"
  echo "   Check Azure logs for delivery status"
else
  echo "❌ Email test may have failed. Check the response above."
fi

