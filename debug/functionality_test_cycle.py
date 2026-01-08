"""
Functionality Test Cycle
Tests all Penelope functionality one by one, logs responses, and debugs issues
"""
import subprocess
import sys
import os
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from penelope.core.agent import PenelopeAgent

class FunctionalityTester:
    """Tests all Penelope functionality systematically"""
    
    def __init__(self, penelope_dir: Path):
        self.penelope_dir = penelope_dir
        self.log_dir = penelope_dir / "debug" / "test_logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.test_results = []
        
        # Load environment
        load_dotenv(penelope_dir / ".env")
        
        # Initialize agent
        try:
            self.agent = PenelopeAgent()
        except Exception as e:
            print(f"[!] Failed to initialize agent: {e}")
            raise
    
    def log_response(self, test_name: str, query: str, response: str, success: bool, error: str = None):
        """Log test response"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = self.log_dir / f"test_{test_name}_{timestamp}.log"
        
        log_content = f"""
Test: {test_name}
Timestamp: {datetime.now().isoformat()}
Query: {query}
Success: {success}
Response:
{response}
"""
        if error:
            log_content += f"\nError: {error}\n"
        
        with open(log_file, "w", encoding="utf-8") as f:
            f.write(log_content)
        
        self.test_results.append({
            "test": test_name,
            "query": query,
            "success": success,
            "response": response[:200],  # Truncate for summary
            "error": error,
            "log_file": str(log_file)
        })
        
        return log_file
    
    def test_tool(self, tool_name: str, query: str, expected_keywords: List[str] = None) -> Tuple[bool, str]:
        """Test a specific tool by asking Penelope to use it"""
        print(f"\n[*] Testing: {tool_name}")
        print(f"[*] Query: {query}")
        
        try:
            response = self.agent.chat(query)
            print(f"[*] Response: {response[:200]}...")
            
            # Check if response indicates tool usage
            success = True
            if expected_keywords:
                response_lower = response.lower()
                success = any(keyword.lower() in response_lower for keyword in expected_keywords)
            
            # Check if tool was actually called (look for tool indicators)
            tool_used = tool_name.lower() in response.lower() or any(
                tool_name.lower() in str(self.agent.history[-1]).lower() 
                for _ in range(min(3, len(self.agent.history)))
            )
            
            if not tool_used:
                success = False
            
            return success, response
        
        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            print(f"[!] Error: {error_msg}")
            return False, error_msg
    
    def run_all_tests(self):
        """Run all functionality tests"""
        print("=" * 70)
        print("[*] PENELOPE FUNCTIONALITY TEST CYCLE")
        print("=" * 70)
        
        # Define test cases
        test_cases = [
            # File operations
            ("read_file", "Read the contents of README.md", ["read", "file", "readme"]),
            ("list_dir", "List all files in the current directory", ["list", "directory", "files"]),
            ("grep_search", "Search for 'def' in Python files", ["search", "grep", "def"]),
            
            # IDE operations - Cursor
            ("control_cursor_open", "Open Cursor IDE", ["cursor", "open"]),
            ("control_cursor_project", "Open project in Cursor at current directory", ["cursor", "project"]),
            
            # IDE operations - VS Code
            ("control_vscode_open", "Open VS Code", ["code", "vscode", "open"]),
            
            # Git operations
            ("git_status", "Check git status of current directory", ["git", "status"]),
            ("git_log", "Show git log", ["git", "log"]),
            
            # Android Studio
            ("android_studio_open", "Open Android Studio", ["android", "studio"]),
            ("android_gemini_open", "Open Gemini in Android Studio", ["gemini", "android"]),
            
            # Python tools
            ("python_run", "Run a Python command: print('Hello')", ["python", "run"]),
            
            # System operations
            ("open_app", "Open notepad", ["notepad", "open"]),
            ("run_command", "Run command: echo Hello", ["command", "run", "echo"]),
        ]
        
        print(f"\n[*] Running {len(test_cases)} tests...\n")
        
        for test_name, query, expected_keywords in test_cases:
            success, response = self.test_tool(test_name, query, expected_keywords)
            
            error = None if success else "Tool not used or unexpected response"
            log_file = self.log_response(test_name, query, response, success, error)
            
            status = "[+]" if success else "[!]"
            print(f"{status} {test_name}: {'PASS' if success else 'FAIL'}")
            print(f"    Log: {log_file.name}")
            
            time.sleep(1)  # Small delay between tests
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary"""
        summary_file = self.log_dir / f"test_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r["success"])
        failed = total - passed
        
        summary = f"""
PENELOPE FUNCTIONALITY TEST SUMMARY
====================================
Timestamp: {datetime.now().isoformat()}
Total Tests: {total}
Passed: {passed}
Failed: {failed}
Success Rate: {(passed/total*100):.1f}%

DETAILED RESULTS:
"""
        for result in self.test_results:
            status = "PASS" if result["success"] else "FAIL"
            summary += f"\n[{status}] {result['test']}"
            summary += f"\n  Query: {result['query']}"
            summary += f"\n  Response: {result['response'][:100]}..."
            if result["error"]:
                summary += f"\n  Error: {result['error']}"
            summary += f"\n  Log: {result['log_file']}\n"
        
        with open(summary_file, "w", encoding="utf-8") as f:
            f.write(summary)
        
        print("\n" + "=" * 70)
        print(f"[*] TEST SUMMARY")
        print("=" * 70)
        print(f"Total: {total} | Passed: {passed} | Failed: {failed}")
        print(f"Success Rate: {(passed/total*100):.1f}%")
        print(f"\nSummary saved to: {summary_file}")
        print("=" * 70)
        
        return summary_file

def run_test_cycle(max_iterations: int = 3):
    """Run test cycle with debugging"""
    penelope_dir = Path("F:/penelope")
    
    print("=" * 70)
    print("[*] PENELOPE FUNCTIONALITY TEST CYCLE")
    print("=" * 70)
    print(f"[*] Max iterations: {max_iterations}")
    print("[*] This will test all functionality and log responses")
    print("-" * 70)
    
    iteration = 0
    all_passed = False
    
    while iteration < max_iterations:
        iteration += 1
        print(f"\n{'=' * 70}")
        print(f"[=== ITERATION {iteration}/{max_iterations} ===]")
        print(f"{'=' * 70}\n")
        
        try:
            tester = FunctionalityTester(penelope_dir)
            tester.run_all_tests()
            
            # Check if all tests passed
            total = len(tester.test_results)
            passed = sum(1 for r in tester.test_results if r["success"])
            
            if passed == total:
                print(f"\n[+] All tests passed!")
                all_passed = True
                break
            else:
                print(f"\n[!] {total - passed} tests failed. Continuing to next iteration...")
        
        except Exception as e:
            print(f"\n[!] Error in test cycle: {e}")
            import traceback
            traceback.print_exc()
        
        time.sleep(2)
    
    if all_passed:
        print(f"\n{'=' * 70}")
        print("[+] ALL TESTS PASSED!")
        print("[+] Functionality test cycle complete!")
        print(f"{'=' * 70}")
        return True
    else:
        print(f"\n{'=' * 70}")
        print(f"[!] Test cycle completed with failures")
        print(f"{'=' * 70}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Penelope Functionality Test Cycle")
    parser.add_argument("--max-iterations", type=int, default=3, help="Maximum iterations")
    
    args = parser.parse_args()
    
    success = run_test_cycle(max_iterations=args.max_iterations)
    sys.exit(0 if success else 1)
