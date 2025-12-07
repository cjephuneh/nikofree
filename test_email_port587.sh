#!/bin/bash
# Test email with port 587 (TLS) instead of 465 (SSL)
# This script temporarily changes email config to use port 587

BASE_URL="http://localhost:8000"
ADMIN_EMAIL="admin@nikofree.com"
ADMIN_PASSWORD="Admin@1234"
TEST_EMAIL="${1:-$ADMIN_EMAIL}"

echo "=========================================="
echo "  Email Test - Port 587 (TLS)"
echo "=========================================="
echo ""
echo "⚠️  This will temporarily use port 587 with TLS"
echo "   Make sure your .env has:"
echo "   MAIL_PORT=587"
echo "   MAIL_USE_TLS=True"
echo "   MAIL_USE_SSL=False"
echo ""
read -p "Press Enter to continue or Ctrl+C to cancel..."

echo ""
echo "Step 1: Logging in as admin..."
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/admin/login" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$ADMIN_EMAIL\",
    \"password\": \"$ADMIN_PASSWORD\"
  }")

if echo "$LOGIN_RESPONSE" | grep -q '"error"'; then
  echo "❌ Login failed!"
  echo "$LOGIN_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$LOGIN_RESPONSE"
  exit 1
fi

ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

if [ -z "$ACCESS_TOKEN" ]; then
  echo "❌ Failed to get access token"
  exit 1
fi

echo "✅ Login successful!"
echo ""
echo "Step 2: Testing email with port 587..."
echo "  Sending test email to: $TEST_EMAIL"
echo ""

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
  echo "✅ Email test queued!"
  echo ""
  echo "Check server console for email delivery status."
  echo "If you see timeout errors, port 587 is also blocked."
  echo "If you see success, port 587 works!"
else
  echo "❌ Email test may have failed."
fi

