import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime
import pytz
from actions.actions import ActionGetTime, ActionGetDate, ActionTellDateTime

class TestTimeActions(unittest.TestCase):
    def setUp(self):
        self.dispatcher = MagicMock()
        self.tracker = MagicMock()
        
    def test_time_response_format(self):
        """Test that the time response is in the correct format (HH:MM UTC)"""
        action = ActionGetTime()
        action.run(self.dispatcher, self.tracker, {})
        
        # Verify the response format
        self.dispatcher.utter_message.assert_called_once()
        args, kwargs = self.dispatcher.utter_message.call_args
        response = kwargs.get('text', '')
        
        # Check time format (HH:MM UTC)
        self.assertIn("The current time is", response)
        self.assertIn("UTC", response)
        time_str = response.replace("The current time is", "").replace("UTC", "").strip(" .")
        try:
            # Extract just the time part (HH:MM)
            time_part = time_str.strip().split(":")
            self.assertEqual(len(time_part), 2)
            hours, minutes = map(int, time_part)
            self.assertGreaterEqual(hours, 0)
            self.assertLess(hours, 24)
            self.assertGreaterEqual(minutes, 0)
            self.assertLess(minutes, 60)
        except (ValueError, IndexError, AttributeError):
            self.fail(f"Time format is incorrect in response: {response}")
    
    def test_date_response_format(self):
        """Test that the date response is in the correct format"""
        action = ActionGetDate()
        action.run(self.dispatcher, self.tracker, {})
        
        # Verify the response format
        self.dispatcher.utter_message.assert_called_once()
        args, kwargs = self.dispatcher.utter_message.call_args
        response = kwargs.get('text', '')
        
        # Check date format (e.g., "Tuesday, June 24, 2025")
        self.assertTrue(response.startswith("Today's date is "))
        date_str = response.replace("Today's date is ", "").strip(".")
        try:
            datetime.strptime(date_str, "%A, %B %d, %Y")
        except ValueError:
            self.fail(f"Date format is incorrect in response: {response}")
    
    def test_datetime_response_format(self):
        """Test that the datetime response is in the correct format"""
        action = ActionTellDateTime()
        action.run(self.dispatcher, self.tracker, {})
        
        # Verify the response format
        self.dispatcher.utter_message.assert_called_once()
        args, kwargs = self.dispatcher.utter_message.call_args
        response = kwargs.get('text', '')
        
        # Check datetime format (e.g., "Tuesday, June 24, 2025 at 13:30 UTC")
        self.assertTrue(response.startswith("The current date and time is "), 
                       f"Response should start with 'The current date and time is ', got: {response}")
        datetime_str = response.replace("The current date and time is ", "").strip(".")
        try:
            # Parse the datetime string without timezone first
            dt = datetime.strptime(datetime_str, "%A, %B %d, %Y at %H:%M %Z")
            # Verify the parsed time components are valid
            self.assertTrue(1 <= dt.month <= 12)
            self.assertTrue(1 <= dt.day <= 31)
            self.assertTrue(0 <= dt.hour <= 23)
            self.assertTrue(0 <= dt.minute <= 59)
        except ValueError as e:
            self.fail(f"Datetime format is incorrect in response '{response}': {str(e)}")

    @patch('actions.actions.datetime')
    def test_timezone_handling(self, mock_datetime):
        """Test that time is correctly handled in UTC"""
        # Set a fixed datetime for testing
        test_time = datetime(2025, 6, 24, 15, 30, 0, tzinfo=pytz.UTC)
        mock_datetime.now.return_value = test_time
        
        action = ActionGetTime()
        action.run(self.dispatcher, self.tracker, {})
        
        args, kwargs = self.dispatcher.utter_message.call_args
        response = kwargs.get('text', '')
        self.assertIn("15:30 UTC", response)

class TestQuestionVariations(unittest.TestCase):
    def test_time_question_variations(self):
        """Test different ways to ask for the time"""
        questions = [
            ("what time is it?", "The current time is HH:MM UTC"),
            ("can you tell me the current time?", "The current time is HH:MM UTC"),
            ("what's the time right now?", "The current time is HH:MM UTC"),
            ("time please", "The current time is HH:MM UTC"),
            ("what time do you have?", "The current time is HH:MM UTC")
        ]
        print("\nTest these time questions in the Rasa shell:")
        for question, response in questions:
            print(f"  - You: {question}")
            print(f"    Bot: {response} (where HH:MM is the current UTC time)")
            print()
    
    def test_date_question_variations(self):
        """Test different ways to ask for the date"""
        questions = [
            ("what is today's date?", "Today's date is Weekday, Month DD, YYYY"),
            ("what's the date today?", "Today's date is Weekday, Month DD, YYYY"),
            ("can you tell me today's date?", "Today's date is Weekday, Month DD, YYYY"),
            ("what day is it today?", "Today's date is Weekday, Month DD, YYYY"),
            ("date please", "Today's date is Weekday, Month DD, YYYY")
        ]
        print("\nTest these date questions in the Rasa shell:")
        for question, response in questions:
            print(f"  - You: {question}")
            print(f"    Bot: {response} (e.g., 'Tuesday, June 24, 2025')")
            print()
    
    def test_datetime_question_variations(self):
        """Test different ways to ask for date and time"""
        questions = [
            ("what is the date and time?", "The current date and time is Weekday, Month DD, YYYY at HH:MM UTC"),
            ("current date and time please", "The current date and time is Weekday, Month DD, YYYY at HH:MM UTC"),
            ("what's the current date and time?", "The current date and time is Weekday, Month DD, YYYY at HH:MM UTC"),
            ("can you tell me the current date and time?", "The current date and time is Weekday, Month DD, YYYY at HH:MM UTC"),
            ("date and time now", "The current date and time is Weekday, Month DD, YYYY at HH:MM UTC")
        ]
        print("\nTest these datetime questions in the Rasa shell:")
        for question, response in questions:
            print(f"  - You: {question}")
            print(f"    Bot: {response} (e.g., 'Tuesday, June 24, 2025 at 14:00 UTC')")
            print()

def run_tests():
    print("🤖 Starting comprehensive time/date action tests...")
    print("\n=== Testing Core Action Functionality ===")
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
    
    print("\n=== Test Question Variations ===")
    print("The following test cases should be manually tested in the Rasa shell:")
    test_variations = TestQuestionVariations()
    test_variations.test_time_question_variations()
    test_variations.test_date_question_variations()
    test_variations.test_datetime_question_variations()
    
    print("\n✅ All tests completed!")
    print("\nTo test the questions in the Rasa shell, run:")
    print("  python -m rasa shell --model models/model-20250623-101548.tar.gz")

if __name__ == "__main__":
    run_tests()
