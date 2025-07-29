#!/bin/bash
# Test login functionality

echo "🔐 Testing AI Ethics Framework Login"
echo "==================================="

# Test 1: Login page accessible
echo "1. Testing login page accessibility..."
curl -s http://localhost:8010/login | grep -q "Login - AI Ethics" && echo "✅ Login page accessible" || echo "❌ Login page not accessible"

# Test 2: Invalid login
echo "2. Testing invalid login..."
response=$(curl -s -X POST -d "username=wrong&password=wrong" http://localhost:8010/login)
echo "$response" | grep -q "Invalid username or password" && echo "✅ Invalid login handled correctly" || echo "❌ Invalid login not handled"

# Test 3: Valid login
echo "3. Testing valid login..."
curl -s -c test_cookies.txt -X POST -d "username=admin&password=AIethics2025!" http://localhost:8010/login | grep -q "Redirecting" && echo "✅ Valid login redirects correctly" || echo "❌ Valid login failed"

# Test 4: Dashboard access after login
echo "4. Testing dashboard access after login..."
curl -s -b test_cookies.txt http://localhost:8010/ | grep -q "AI Ethics Testing Dashboard" && echo "✅ Dashboard accessible after login" || echo "❌ Dashboard not accessible"

# Cleanup
rm -f test_cookies.txt

echo ""
echo "🎉 Login testing complete!"
echo ""
echo "📝 Login credentials:"
echo "   Username: admin"
echo "   Password: AIethics2025!"
echo "   URL: https://skyforskning.no/login"
