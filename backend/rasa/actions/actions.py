from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from datetime import datetime
import pytz
import sqlite3
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define database path with flexible options for different deployment environments
# 1. Check for environment variable first (useful for Docker/container environments)
# 2. Check for a fixed location in Docker containers
# 3. Fall back to the relative path resolution as before

def get_database_path():
    # First priority: Environment variable
    if os.environ.get('ADVENTURE_WORKS_DB_PATH'):
        db_path = os.environ.get('ADVENTURE_WORKS_DB_PATH')
        logger.info(f"Using database path from environment variable: {db_path}")
        return db_path

    # Second priority: Check common Docker mount locations
    docker_path = '/app/db/AdventureWorks.db'
    if os.path.exists(docker_path):
        logger.info(f"Using database path from Docker mount: {docker_path}")
        return docker_path

    # Third priority: Relative path as before (legacy approach)
    relative_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../db/AdventureWorks.db'))
    logger.info(f"Using relative database path: {relative_path}")
    return relative_path

DB_PATH = get_database_path()

# Helper function to handle database connections with proper error handling
def get_db_connection():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # This enables column access by name
        return conn
    except sqlite3.Error as e:
        logger.error(f"Database connection error: {e}")
        return None

class ActionGetTime(Action):
    def name(self) -> Text:
        return "action_get_time"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        current_time = datetime.now(pytz.utc).strftime("%H:%M")
        dispatcher.utter_message(text=f"The current time is {current_time} UTC.")
        return []

class ActionGetDate(Action):
    def name(self) -> Text:
        return "action_get_date"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        current_date = datetime.now(pytz.utc).strftime("%A, %B %d, %Y")
        dispatcher.utter_message(text=f"Today's date is {current_date}.")
        return []

class ActionTellDateTime(Action):
    def name(self) -> Text:
        return "action_tell_datetime"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        current_datetime = datetime.now(pytz.utc).strftime("%A, %B %d, %Y at %H:%M %Z")
        dispatcher.utter_message(text=f"The current date and time is {current_datetime}.")
        return []

class ActionIncrementFallbackCount(Action):
    def name(self) -> Text:
        return "action_increment_fallback_count"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # This is a placeholder action. You can add logic here if needed.
        return []

class ActionSetLanguage(Action):
    def name(self) -> Text:
        return "action_set_language"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
    
        language = next(tracker.get_latest_entity_values("language"), None)
    
        if language:
            dispatcher.utter_message(text=f"I'll remember you want to speak in {language}.")
            return [SlotSet("language", language)]
        else:
            dispatcher.utter_message(text="I didn't catch which language you'd like to use.")
            return []


class ActionTrackOrder(Action):
    def name(self) -> Text:
        return "action_track_order"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
    
        # Get order_id from slot
        order_id = tracker.get_slot("order_number")
    
        if not order_id:
            dispatcher.utter_message(text="I need an order number to track your order. Can you please provide it?")
            # Create suggested replies for better UX
            suggested_replies = ["I don't have my order number", "My order number is SO12345"]
            dispatcher.utter_message(json_message={"custom": {"suggested_replies": suggested_replies}})
            return []
    
        # Get the connection to the database
        conn = get_db_connection()
        if not conn:
            dispatcher.utter_message(text="I'm sorry, but I'm having trouble accessing our order database right now. Please try again later.")
            return []
    
        try:
            # Use a cursor to query the database
            cursor = conn.cursor()
        
            # Query for order information from SalesOrderHeader
            query = """
            SELECT OrderDate, Status, TotalDue
            FROM SalesOrderHeader
            WHERE SalesOrderID = ?
            """
        
            cursor.execute(query, (order_id,))
            result = cursor.fetchone()
        
            if result:
                order_date = result["OrderDate"]
                status = result["Status"]
                total = result["TotalDue"]
            
                # Format response message
                message = f"Order #{order_id} was placed on {order_date}. Status: {status}. Total amount: ${total:.2f}"
                dispatcher.utter_message(text=message)
            
                # Provide suggested follow-up actions
                suggested_replies = ["Need help with this order", "Track another order", "Return this order"]
                dispatcher.utter_message(json_message={"custom": {"suggested_replies": suggested_replies}})
            
                return []
            else:
                dispatcher.utter_message(text=f"I couldn't find any order with the number {order_id}. Please check and try again.")
                return []
            
        except sqlite3.Error as e:
            dispatcher.utter_message(text="I encountered an error while retrieving your order information. Please try again later.")
            logger.error(f"Database error in action_track_order: {e}")
            return []
        finally:
            # Always close the connection when done
            if conn:
                conn.close()


class ActionLogComplaint(Action):
    def name(self) -> Text:
        return "action_log_complaint"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # This is currently a stub that would be expanded later
        # Get relevant slots
        complaint_type = tracker.get_slot("complaint_type")
        complaint_details = tracker.get_slot("complaint_details")
        customer_email = tracker.get_slot("customer_email")
        # Log the complaint (stub implementation)
        logger.info(f"Complaint received - Type: {complaint_type}, Details: {complaint_details}, Email: {customer_email}")
        # In a complete implementation, you would save this to a database
        # For now, just acknowledge receipt
        dispatcher.utter_message(text="Thank you for bringing this to our attention. Your complaint has been logged with our system.")
        dispatcher.utter_message(text="A customer service representative will review your complaint and contact you soon.")
        # Provide suggested follow-up options
        suggested_replies = ["I have another issue", "Connect me with a human", "What happens next?"]
        dispatcher.utter_message(json_message={"custom": {"suggested_replies": suggested_replies}})
    
        return []


class ActionRecommendProduct(Action):
    def name(self) -> Text:
        return "action_recommend_product"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # This is a stub implementation that returns hardcoded recommendations
        # In a complete implementation, this would query the database based on user preferences
        # We could use product_id to filter recommendations
        # product_id = tracker.get_slot("product_id")
        # Hardcoded recommendations for demonstration purposes
        # These would come from the database in a real implementation
        recommendations = [
            {"id": "BK-M68B-38", "name": "Mountain-300 Black, 38", "price": 1079.99, "category": "Mountain Bikes"},
            {"id": "BK-M38S-42", "name": "Mountain-100 Silver, 42", "price": 3399.99, "category": "Mountain Bikes"},
            {"id": "BK-R68R-52", "name": "Road-250 Red, 52", "price": 2443.35, "category": "Road Bikes"}
        ]
        # Format the recommendations as a message
        message = "Based on your preferences, you might like these products:\n\n"
        for rec in recommendations:
            message += f"• {rec['name']} (${rec['price']:.2f}) - {rec['category']}\n"
    
        dispatcher.utter_message(text=message)
        # Provide suggested follow-up actions
        suggested_replies = ["Tell me more about the first one", "Show me more recommendations", "I'm interested in buying"]
        dispatcher.utter_message(json_message={"custom": {"suggested_replies": suggested_replies}})
    
        return []


class ActionEscalateToHuman(Action):
    def name(self) -> Text:
        return "action_escalate_to_human"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
    
        # Get any relevant context to pass to the human agent
        current_topic = tracker.get_slot("complaint_type") or "general inquiry"
    
        # Inform the user that they're being transferred
        dispatcher.utter_message(text="I understand that you'd like to speak with a human agent.")
        dispatcher.utter_message(text=f"I'm transferring your conversation about '{current_topic}' to one of our customer care specialists now.")
        dispatcher.utter_message(text="Please stand by. A representative will be with you shortly.")
    
        # In a real implementation, this would trigger an API call to a handoff service
        # For now, this is just simulating the handoff
    
        return []
