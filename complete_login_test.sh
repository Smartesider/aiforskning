#!/bin/bash
# Complete login test for both web form and API

echo "🔐 Complete AI Ethics Framework Login Test"
echo "=========================================="

echo ""
echo "1. Testing API login endpoint..."
echo "--------------------------------"

# Test valid API login
echo "✓ Testing valid API login:"
response=$(curl -s -X POST -H "Content-Type: application/json" -d '{"username":"admin","password":"AIethics2025!"}' http://localhost:8010/api/auth/login)
echo "$response" | grep -q '"success":true' && echo "  ✅ Valid API login successful" || echo "  ❌ Valid API login failed"

# Test invalid API login
echo "✓ Testing invalid API login:"
response=$(curl -s -X POST -H "Content-Type: application/json" -d '{"username":"wrong","password":"wrong"}' http://localhost:8010/api/auth/login)
echo "$response" | grep -q '"error"' && echo "  ✅ Invalid API login properly rejected" || echo "  ❌ Invalid API login not handled"

echo ""
echo "2. Testing web form login..."
echo "----------------------------"

# Test login page accessibility
echo "✓ Testing login page:"
curl -s http://localhost:8010/login | grep -q "Login - AI Ethics" && echo "  ✅ Login page accessible" || echo "  ❌ Login page not accessible"

# Test web form login (should redirect)
echo "✓ Testing web form login:"
response=$(curl -s -X POST -d "username=admin&password=AIethics2025!" http://localhost:8010/login)
echo "$response" | grep -q "Redirecting" && echo "  ✅ Web form login successful" || echo "  ❌ Web form login failed"

echo ""
echo "3. Final verification..."
echo "------------------------"

# Test that both endpoints exist
echo "✓ Checking endpoints:"
curl -s -I http://localhost:8010/login | grep -q "200 OK" && echo "  ✅ /login endpoint responding" || echo "  ❌ /login endpoint not responding"
curl -s -I -X POST http://localhost:8010/api/auth/login | grep -q "400\|401" && echo "  ✅ /api/auth/login endpoint responding" || echo "  ❌ /api/auth/login endpoint not responding"

echo ""
echo "🎉 LOGIN TEST COMPLETE!"
echo ""
echo "📋 SUMMARY:"
echo "   ✅ API Endpoint: POST /api/auth/login (JSON)"
echo "   ✅ Web Form: POST /login (form data)"
echo "   ✅ Login Page: GET /login"
echo ""
echo "🔑 Credentials:"
echo "   Username: admin"
echo "   Password: AIethics2025!"
echo ""
echo "🌐 URLs:"
echo "   Login Page: https://skyforskning.no/login"
echo "   Dashboard: https://skyforskning.no/"
