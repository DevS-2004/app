import requests
import sys
import json
from datetime import datetime

class WumpusGameTester:
    def __init__(self, base_url="https://hunt-the-wumpus.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.game_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
        
        self.test_results.append({
            "test": name,
            "success": success,
            "details": details
        })

    def run_test(self, name, method, endpoint, expected_status, data=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            else:
                self.log_test(name, False, f"Unsupported method: {method}")
                return False, {}

            print(f"   Status: {response.status_code}")
            
            success = response.status_code == expected_status
            
            if success:
                try:
                    response_data = response.json()
                    self.log_test(name, True)
                    return True, response_data
                except json.JSONDecodeError:
                    self.log_test(name, False, "Invalid JSON response")
                    return False, {}
            else:
                error_msg = f"Expected {expected_status}, got {response.status_code}"
                try:
                    error_detail = response.json()
                    error_msg += f" - {error_detail}"
                except:
                    error_msg += f" - {response.text[:200]}"
                self.log_test(name, False, error_msg)
                return False, {}

        except requests.exceptions.RequestException as e:
            self.log_test(name, False, f"Request error: {str(e)}")
            return False, {}

    def test_api_root(self):
        """Test API root endpoint"""
        success, response = self.run_test(
            "API Root",
            "GET",
            "",
            200
        )
        return success

    def test_start_game(self):
        """Test starting a new game"""
        success, response = self.run_test(
            "Start Game",
            "POST",
            "game/start",
            200
        )
        
        if success:
            # Validate response structure
            required_fields = ['game_id', 'player_position', 'arrows_remaining', 
                             'moves_count', 'has_gold', 'game_status', 'score', 
                             'visited_cells', 'sensory_info']
            
            for field in required_fields:
                if field not in response:
                    self.log_test("Start Game - Response Structure", False, f"Missing field: {field}")
                    return False
            
            # Validate initial values
            if response['player_position']['x'] != 0 or response['player_position']['y'] != 0:
                self.log_test("Start Game - Initial Position", False, "Player should start at (0,0)")
                return False
            
            if response['arrows_remaining'] != 3:
                self.log_test("Start Game - Initial Arrows", False, "Should start with 3 arrows")
                return False
            
            if response['game_status'] != 'active':
                self.log_test("Start Game - Initial Status", False, "Game should be active")
                return False
            
            if len(response['visited_cells']) != 8 or len(response['visited_cells'][0]) != 8:
                self.log_test("Start Game - Grid Size", False, "Should have 8x8 grid")
                return False
            
            self.game_id = response['game_id']
            self.log_test("Start Game - Response Structure", True)
            return True
        
        return False

    def test_get_game(self):
        """Test getting game state"""
        if not self.game_id:
            self.log_test("Get Game", False, "No game_id available")
            return False
        
        success, response = self.run_test(
            "Get Game State",
            "GET",
            f"game/{self.game_id}",
            200
        )
        return success

    def test_move_player(self):
        """Test player movement"""
        if not self.game_id:
            self.log_test("Move Player", False, "No game_id available")
            return False
        
        # Test valid move
        success, response = self.run_test(
            "Move Player - Right",
            "POST",
            "game/move",
            200,
            data={"game_id": self.game_id, "direction": "right"}
        )
        
        if success:
            # Check if position changed
            if response['player_position']['x'] != 1 or response['player_position']['y'] != 0:
                self.log_test("Move Player - Position Update", False, "Position not updated correctly")
                return False
            
            if response['moves_count'] != 1:
                self.log_test("Move Player - Move Count", False, "Move count not incremented")
                return False
            
            self.log_test("Move Player - Position Update", True)
        
        # Test invalid move (boundary)
        invalid_success, _ = self.run_test(
            "Move Player - Invalid Direction",
            "POST",
            "game/move",
            200,  # Should return 200 with message about invalid move
            data={"game_id": self.game_id, "direction": "invalid"}
        )
        
        return success

    def test_shoot_arrow(self):
        """Test shooting arrows"""
        if not self.game_id:
            self.log_test("Shoot Arrow", False, "No game_id available")
            return False
        
        success, response = self.run_test(
            "Shoot Arrow",
            "POST",
            "game/shoot",
            200,
            data={"game_id": self.game_id, "direction": "up"}
        )
        
        if success:
            # Check if arrows decreased
            if response['arrows_remaining'] != 2:  # Should be 2 after shooting once
                self.log_test("Shoot Arrow - Arrow Count", False, "Arrow count not decremented")
                return False
            
            self.log_test("Shoot Arrow - Arrow Count", True)
        
        return success

    def test_leaderboard_get(self):
        """Test getting leaderboard"""
        success, response = self.run_test(
            "Get Leaderboard",
            "GET",
            "leaderboard",
            200
        )
        
        if success:
            # Should return a list (even if empty)
            if not isinstance(response, list):
                self.log_test("Get Leaderboard - Response Type", False, "Should return a list")
                return False
            
            self.log_test("Get Leaderboard - Response Type", True)
        
        return success

    def test_leaderboard_submit(self):
        """Test submitting to leaderboard"""
        test_entry = {
            "player_name": f"TestPlayer_{datetime.now().strftime('%H%M%S')}",
            "score": 850,
            "moves": 15
        }
        
        success, response = self.run_test(
            "Submit Leaderboard",
            "POST",
            "leaderboard",
            200,
            data=test_entry
        )
        
        if success:
            # Validate response structure
            required_fields = ['entry_id', 'player_name', 'score', 'moves', 'timestamp']
            for field in required_fields:
                if field not in response:
                    self.log_test("Submit Leaderboard - Response Structure", False, f"Missing field: {field}")
                    return False
            
            if response['player_name'] != test_entry['player_name']:
                self.log_test("Submit Leaderboard - Player Name", False, "Player name mismatch")
                return False
            
            self.log_test("Submit Leaderboard - Response Structure", True)
        
        return success

    def test_error_handling(self):
        """Test error handling"""
        # Test with invalid game_id
        success, _ = self.run_test(
            "Error Handling - Invalid Game ID",
            "POST",
            "game/move",
            404,
            data={"game_id": "invalid-id", "direction": "up"}
        )
        
        return success

    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting Wumpus Game Backend Tests")
        print("=" * 50)
        
        # Test sequence
        tests = [
            self.test_api_root,
            self.test_start_game,
            self.test_get_game,
            self.test_move_player,
            self.test_shoot_arrow,
            self.test_leaderboard_get,
            self.test_leaderboard_submit,
            self.test_error_handling
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                print(f"❌ {test.__name__} - EXCEPTION: {str(e)}")
                self.tests_run += 1
        
        # Print summary
        print("\n" + "=" * 50)
        print(f"📊 Backend Tests Summary:")
        print(f"   Total Tests: {self.tests_run}")
        print(f"   Passed: {self.tests_passed}")
        print(f"   Failed: {self.tests_run - self.tests_passed}")
        print(f"   Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        return self.tests_passed, self.tests_run, self.test_results

def main():
    tester = WumpusGameTester()
    passed, total, results = tester.run_all_tests()
    
    # Return appropriate exit code
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())