from core.event_bus import EventBus, EventType
from agent.agent import Agent
from agent.decision_and_actions import EatAction, ActionQueue
from agent.needs import NeedsSystem
from agent.body import Body
import time

def test_eat_action():
    print("🧪 Testing EatAction execution flow...")
    
    # Setup
    bus = EventBus()
    agent = Agent("test_agent", "Test Bot", 30, bus)
    
    # Initialize components
    needs = agent.add_component(NeedsSystem)
    body = agent.add_component(Body)
    queue = agent.add_component(ActionQueue)
    
    # Set initial bad state
    needs.get_need("hunger").value = 0.0  # Starving
    body.energy = 0.1  # Exhausted
    
    print(f"Initial State: Hunger={needs.get_need('hunger').value}, Energy={body.energy}")
    
    # Manually trigger EatAction start
    eat_action = EatAction()
    print(f"Starting EatAction (duration={eat_action.duration})...")
    
    # Simulate DecisionEngine handing off to ActionQueue
    queue._start_action(eat_action)
    
    # Simulate time passing
    # We need to pump the event bus and tick the agent
    total_ticks = 0
    # Run while busy OR for a few ticks to catch up events
    while (queue.is_busy() or total_ticks < 40) and total_ticks < 100:
        bus.tick()
        agent.tick(1.0) # 1 minute per tick
        total_ticks += 1
        
        if total_ticks % 10 == 0:
            print(f"Tick {total_ticks}: Action Progress={queue.action_progress}/{eat_action.duration}")
            
    print(f"Final State: Hunger={needs.get_need('hunger').value}, Energy={body.energy}")
    
    if needs.get_need("hunger").value > 0.1:
        print("✅ SUCCESS: Hunger increased!")
    else:
        print("❌ FAILURE: Hunger did not increase.")

if __name__ == "__main__":
    test_eat_action()
