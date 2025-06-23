import asyncio
import json
from rasa.core.agent import Agent
from rasa.core.channels.channel import UserMessage
from rasa.core.dispatcher import CollectingDispatcher
from rasa.core.events import UserUttered

async def test_action():
    # Load the agent with the model
    agent = Agent.load("models/20250620-232016-nice-raspberry.tar.gz")
    
    # Create a test message
    sender_id = "test_user"
    message = UserMessage("what time is it", sender_id=sender_id)
    
    # Handle the message to get the tracker
    tracker = await agent.tracker_store.get_or_create_tracker(sender_id)
    
    # Get the action to execute
    action_name = "action_tell_time"
    action = agent.create_processor().create_action(action_name, None)
    
    if action is None:
        print(f"Could not create action {action_name}")
        return
    
    print(f"Executing action: {action.name()}")
    
    # Execute the action
    try:
        events = await action.run(
            CollectingDispatcher(),
            tracker,
            agent.domain
        )
        print("Action executed successfully!")
        print("Generated events:", [e.as_dict() for e in events])
    except Exception as e:
        print(f"Error executing action: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_action())
