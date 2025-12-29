#!/bin/bash

# ============================================
# 🧪 Flab2Fabs – Sanity Testing via BASH + curl
# ============================================

# Configuration
BASE_URL="http://localhost:8008"
ADMIN_USERNAME="sashy"
ADMIN_PASSWORD="Welcome2026!"
TEST_USERNAME="test_athlete_$(date +%s)"
TEST_PASSWORD="TestPass123!"
TEST_EMAIL="test_$(date +%s)@flabs2fabs.app"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}🧪 Flab2Fabs Sanity Test Suite${NC}"
echo -e "${BLUE}============================================${NC}"
echo "Server: $BASE_URL"
echo "Timestamp: $(date)"
echo ""

# Function to print test results
print_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
    fi
}

# Function to run curl and check HTTP status
run_curl() {
    local expected_status=$1
    shift
    local response=$(curl -s -w "%{http_code}" "$@")
    local http_code=${response: -3}
    local body=${response%???}
    
    if [ "$http_code" -eq "$expected_status" ]; then
        echo "$body"
        return 0
    else
        echo "HTTP $http_code (expected $expected_status): $body" >&2
        return 1
    fi
}

# ============================================
# 0️⃣ Quick Server Health Check (Always First)
# ============================================
echo -e "${YELLOW}0️⃣ Server Health Check${NC}"
HEALTH_RESPONSE=$(run_curl 200 "$BASE_URL/api/system/health")
if [ $? -eq 0 ]; then
    print_result 0 "Server is running and healthy"
    echo "Response: $HEALTH_RESPONSE"
else
    print_result 1 "Server health check failed"
    echo -e "${RED}❌ Server isn't running or wrong port. Exiting.${NC}"
    exit 1
fi
echo ""

# ============================================
# 1️⃣ AUTH – Login & Token Handling (Critical)
# ============================================
echo -e "${YELLOW}1️⃣ Auth Testing${NC}"

# 1.1 Login as Admin
echo "1.1 Logging in as admin ($ADMIN_USERNAME)..."
LOGIN_RESPONSE=$(run_curl 200 -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"$ADMIN_USERNAME\", \"password\": \"$ADMIN_PASSWORD\"}")

if [ $? -eq 0 ]; then
    print_result 0 "Admin login successful"
    echo "$LOGIN_RESPONSE" | jq . 2>/dev/null || echo "$LOGIN_RESPONSE"
    
    # Extract tokens
    ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token' 2>/dev/null)
    REFRESH_TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.refresh_token' 2>/dev/null)
    
    if [ -n "$ACCESS_TOKEN" ] && [ "$ACCESS_TOKEN" != "null" ]; then
        print_result 0 "Access token obtained"
        echo "Token (first 30 chars): ${ACCESS_TOKEN:0:30}..."
    else
        print_result 1 "Failed to extract access token"
        exit 1
    fi
else
    print_result 1 "Admin login failed"
    exit 1
fi
echo ""

# 1.2 Create Test User (Admin only)
echo "1.2 Creating test user..."
CREATE_USER_RESPONSE=$(run_curl 200 -X POST "$BASE_URL/api/admin/create-user" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d "{
    \"username\": \"$TEST_USERNAME\",
    \"email\": \"$TEST_EMAIL\",
    \"password\": \"$TEST_PASSWORD\",
    \"is_admin\": false
  }")

if [ $? -eq 0 ]; then
    print_result 0 "Test user created: $TEST_USERNAME"
else
    print_result 1 "Failed to create test user"
fi
echo ""

# 1.3 Login as Test User
echo "1.3 Logging in as test user..."
USER_LOGIN_RESPONSE=$(run_curl 200 -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"$TEST_USERNAME\", \"password\": \"$TEST_PASSWORD\"}")

if [ $? -eq 0 ]; then
    USER_TOKEN=$(echo "$USER_LOGIN_RESPONSE" | jq -r '.access_token' 2>/dev/null)
    if [ -n "$USER_TOKEN" ]; then
        print_result 0 "Test user login successful"
    else
        print_result 1 "Failed to extract user token"
    fi
else
    print_result 1 "Test user login failed"
fi
echo ""

# 1.4 Verify User Cannot Access Admin Endpoints
echo "1.4 Verifying user role permissions..."
NON_ADMIN_ATTEMPT=$(run_curl 403 -X POST "$BASE_URL/api/admin/create-user" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $USER_TOKEN" \
  -d '{"username": "should_fail", "email": "fail@test.com", "password": "fail"}')

if [ $? -eq 0 ]; then
    print_result 0 "Non-admin user correctly blocked from admin endpoint"
else
    print_result 1 "Role-based access control might be broken"
fi
echo ""

# ============================================
# 2️⃣ EXERCISE LIBRARY TEST (Admin Only)
# ============================================
echo -e "${YELLOW}2️⃣ Exercise Library Testing${NC}"

# 2.1 Create Strength Exercise
echo "2.1 Creating strength exercise..."
EXERCISE1_RESPONSE=$(run_curl 200 -X POST "$BASE_URL/api/exercises/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Barbell Bench Press",
    "description": "Compound chest movement for building upper body strength",
    "exercise_type": "strength",
    "muscle_group": "Chest, Triceps, Shoulders",
    "equipment_required": "Barbell, Bench"
  }')

if [ $? -eq 0 ]; then
    EXERCISE1_ID=$(echo "$EXERCISE1_RESPONSE" | jq -r '.id' 2>/dev/null)
    print_result 0 "Exercise 1 created (ID: $EXERCISE1_ID)"
    echo "$EXERCISE1_RESPONSE" | jq . 2>/dev/null || echo "$EXERCISE1_RESPONSE"
else
    print_result 1 "Failed to create exercise 1"
    # Try to continue with manual ID
    EXERCISE1_ID=1
fi
echo ""

# 2.2 Create Cardio Exercise
echo "2.2 Creating cardio exercise..."
EXERCISE2_RESPONSE=$(run_curl 200 -X POST "$BASE_URL/api/exercises/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Running (Treadmill)",
    "description": "Cardiovascular endurance training",
    "exercise_type": "cardio",
    "muscle_group": "Legs, Cardiovascular",
    "equipment_required": "Treadmill"
  }')

if [ $? -eq 0 ]; then
    EXERCISE2_ID=$(echo "$EXERCISE2_RESPONSE" | jq -r '.id' 2>/dev/null)
    print_result 0 "Exercise 2 created (ID: $EXERCISE2_ID)"
else
    print_result 1 "Failed to create exercise 2"
    EXERCISE2_ID=2
fi
echo ""

# 2.3 List All Exercises
echo "2.3 Listing all exercises..."
EXERCISES_LIST=$(run_curl 200 -X GET "$BASE_URL/api/exercises/")

if [ $? -eq 0 ]; then
    print_result 0 "Exercises retrieved successfully"
    echo "Found $(echo "$EXERCISES_LIST" | jq '. | length' 2>/dev/null || echo "?") exercises"
    echo "$EXERCISES_LIST" | jq '.[] | {id, name, exercise_type}' 2>/dev/null || echo "Raw: $EXERCISES_LIST"
else
    print_result 1 "Failed to list exercises"
fi
echo ""

# ============================================
# 3️⃣ WORKOUT LOGGING TEST (Truth Test)
# ============================================
echo -e "${YELLOW}3️⃣ Workout Logging Testing${NC}"

# 3.1 Create First Workout (User perspective)
echo "3.1 Logging first workout..."
WORKOUT1_RESPONSE=$(run_curl 200 -X POST "$BASE_URL/api/workouts/" \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"Monday Chest Day\",
    \"notes\": \"Felt strong today\",
    \"exercises\": [
      {
        \"exercise_id\": $EXERCISE1_ID,
        \"sets\": 3,
        \"reps\": 10,
        \"weight_kg\": 60.0,
        \"calories\": 120
      },
      {
        \"exercise_id\": $EXERCISE2_ID,
        \"duration_minutes\": 20.5,
        \"calories\": 180
      }
    ]
  }")

if [ $? -eq 0 ]; then
    WORKOUT1_ID=$(echo "$WORKOUT1_RESPONSE" | jq -r '.id' 2>/dev/null)
    WORKOUT1_CALORIES=$(echo "$WORKOUT1_RESPONSE" | jq -r '.calories_burned' 2>/dev/null)
    print_result 0 "Workout 1 created (ID: $WORKOUT1_ID)"
    echo "Total calories: $WORKOUT1_CALORIES"
    
    # Manual verification
    EXPECTED_CALORIES=$((120 + 180))
    if [ "$WORKOUT1_CALORIES" = "$EXPECTED_CALORIES" ]; then
        print_result 0 "Calorie math correct: 120 + 180 = $EXPECTED_CALORIES"
    else
        print_result 1 "Calorie math incorrect. Expected $EXPECTED_CALORIES, got $WORKOUT1_CALORIES"
    fi
else
    print_result 1 "Failed to create workout 1"
fi
echo ""

# 3.2 Complete the Workout
echo "3.2 Completing workout..."
COMPLETE_RESPONSE=$(run_curl 200 -X POST "$BASE_URL/api/workouts/$WORKOUT1_ID/complete" \
  -H "Authorization: Bearer $USER_TOKEN")

if [ $? -eq 0 ]; then
    print_result 0 "Workout marked as completed"
else
    print_result 1 "Failed to complete workout"
fi
echo ""

# 3.3 List User's Workouts
echo "3.3 Listing user's workouts..."
USER_WORKOUTS=$(run_curl 200 -X GET "$BASE_URL/api/workouts/" \
  -H "Authorization: Bearer $USER_TOKEN")

if [ $? -eq 0 ]; then
    WORKOUT_COUNT=$(echo "$USER_WORKOUTS" | jq '. | length' 2>/dev/null || echo "0")
    print_result 0 "User has $WORKOUT_COUNT workout(s)"
    echo "$USER_WORKOUTS" | jq '.[] | {id, name, calories_burned, total_duration_minutes}' 2>/dev/null || echo "Raw: $USER_WORKOUTS"
else
    print_result 1 "Failed to list workouts"
fi
echo ""

# ============================================
# 4️⃣ Database Sanity Check (Direct Truth)
# ============================================
echo -e "${YELLOW}4️⃣ Database Integrity Check${NC}"

echo "4.1 Checking database contents..."
echo "Users in database:"
sudo mariadb -u root -pWelcome2026 flab2fabs -e "SELECT id, username, email, is_admin, is_active FROM users ORDER BY id;" 2>/dev/null

echo ""
echo "Exercises in database:"
sudo mariadb -u root -pWelcome2026 flab2fabs -e "SELECT id, name, exercise_type, is_active FROM exercises ORDER BY id;" 2>/dev/null

echo ""
echo "Workouts in database:"
sudo mariadb -u root -pWelcome2026 flab2fabs -e "SELECT id, user_id, name, calories_burned FROM workouts ORDER BY id;" 2>/dev/null

echo ""
echo "Workout exercises in database:"
sudo mariadb -u root -pWelcome2026 flab2fabs -e "SELECT id, workout_id, exercise_id, sets, reps, weight_kg, calories FROM workout_exercises ORDER BY workout_id;" 2>/dev/null
print_result 0 "Database checks completed"
echo ""

# ============================================
# 5️⃣ Failure Tests (Error Handling)
# ============================================
echo -e "${YELLOW}5️⃣ Failure Testing${NC}"

# 5.1 Missing Token
echo "5.1 Testing missing token..."
MISSING_TOKEN_RESPONSE=$(run_curl 401 -X POST "$BASE_URL/api/workouts/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Should Fail"}')

if [ $? -eq 0 ]; then
    print_result 0 "Correctly rejected: Missing token"
else
    print_result 1 "Missing token test failed"
fi
echo ""

# 5.2 Invalid Token
echo "5.2 Testing invalid token..."
INVALID_TOKEN_RESPONSE=$(run_curl 401 -X POST "$BASE_URL/api/workouts/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer invalid_token_here_12345" \
  -d '{"name": "Should Fail"}')

if [ $? -eq 0 ]; then
    print_result 0 "Correctly rejected: Invalid token"
else
    print_result 1 "Invalid token test failed"
fi
echo ""

# 5.3 Non-existent Exercise
echo "5.3 Testing non-existent exercise..."
BAD_EXERCISE_RESPONSE=$(run_curl 400 -X POST "$BASE_URL/api/workouts/" \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Bad Exercise Test",
    "exercises": [
      {
        "exercise_id": 99999,
        "sets": 3,
        "reps": 10
      }
    ]
  }')

if [ $? -eq 0 ]; then
    print_result 0 "Correctly rejected: Non-existent exercise"
else
    print_result 1 "Non-existent exercise test failed"
fi
echo ""

# ============================================
# 📊 Test Summary
# ============================================
echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}📊 SANITY TEST SUMMARY${NC}"
echo -e "${BLUE}============================================${NC}"
echo "Server: $BASE_URL"
echo "Test Time: $(date)"
echo ""

echo -e "${YELLOW}✅ Tests that should have passed:${NC}"
echo "1. Server health check"
echo "2. Admin authentication"
echo "3. User creation"
echo "4. Role-based access control"
echo "5. Exercise creation (admin)"
echo "6. Workout logging"
echo "7. Database integrity"
echo "8. Error handling"

echo ""
echo -e "${YELLOW}🔧 Next steps if tests pass:${NC}"
echo "1. Run automated tests regularly"
echo "2. Add more comprehensive test data"
echo "3. Implement CI/CD pipeline"
echo "4. Monitor database growth"
echo "5. Add performance benchmarks"

echo ""
echo -e "${GREEN}🎉 Flab2Fabs Sanity Test Complete!${NC}"
echo -e "${BLUE}============================================${NC}"
