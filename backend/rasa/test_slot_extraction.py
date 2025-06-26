from rasa.core.agent import Agent
from rasa.core.interpreter import RasaNLUInterpreter
import asyncio
import nest_asyncio
import os

# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()

# Path to your model
model_path = "models/latest_rasa_model.tar.gz"

# Create an agent
agent = Agent.load(model_path)

# Test message
test_message = "My order number is ORD12345"

async def test_slot_extraction():
    # Process the message
    response = await agent.parse_message_using_nlu_interpreter(test_message)
    print("NLU Response:")
    print(response)
    
    # Get the tracker with the latest conversation state
    tracker = agent.tracker_store.get_or_create_tracker("test_user")
    
    # Update the tracker with the latest message
    await agent.tracker_store.update(tracker)
    
    # Print the slots
    print("\nCurrent Slots:")
    for slot_name, slot_value in tracker.slots.items():
        if slot_value is not None and slot_value.value is not None:
            print(f"{slot_name}: {slot_value.value}")

# Run the test
if __name__ == "__main__":
    asyncio.run(test_slot_extraction())
