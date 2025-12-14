"""
Component System - Base classes for the component-based agent architecture
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Type, TypeVar, Union
from core.event_bus import EventBus, Event

# Type variable for component types
T = TypeVar('T', bound='Component')


class Component(ABC):
    """
    Abstract base class for all agent components.
    Components handle specific aspects of an agent's behavior (needs, mood, etc.)
    """

    def __init__(self, agent_id: str, event_bus: EventBus):
        """
        Initialize component

        Args:
            agent_id: ID of the agent owning this component
            event_bus: Reference to the system event bus
        """
        self.agent_id = agent_id
        self.event_bus = event_bus
        self.agent = None  # Will be injected by manager
        self.subscribed_events: List[str] = []

    def subscribe(self, event_types: List[str]):
        """
        Subscribe to events

        Args:
            event_types: List of event types to subscribe to
        """
        self.event_bus.subscribe(event_types, self.on_event)
        self.subscribed_events.extend(event_types)

    def emit_event(self, event_type: str, data: Dict[str, Any] = None, priority: int = 5, target: str = "all", **kwargs):
        """
        Emit an event

        Args:
            event_type: Type of event
            data: Event data payload
            priority: Event priority
            target: Target ID or "all"
            **kwargs: Additional event arguments
        """
        if data is None:
            data = {}
            
        event = Event(
            type=event_type,
            source=self.agent_id,
            target=target,
            data=data,
            priority=priority,
            timestamp=self.event_bus.get_current_time(),
            **kwargs
        )
        self.event_bus.emit(event)

    @abstractmethod
    def on_event(self, event: Event):
        """
        Handle events

        Args:
            event: The event to handle
        """
        pass

    def tick(self, delta_time: float):
        """
        Update component state

        Args:
            delta_time: Time elapsed in minutes
        """
        pass

    def get_component_name(self) -> str:
        """
        Get component name (usually class name snake_cased)
        """
        return self.__class__.__name__

    @abstractmethod
    def serialize(self) -> Dict[str, Any]:
        """
        Serialize component state
        """
        pass

    @abstractmethod
    def deserialize(self, data: Dict[str, Any]):
        """
        Deserialize component state
        """
        pass


class ComponentManager:
    """
    Manages components for an agent
    """

    def __init__(self, agent_id: str, event_bus: EventBus, agent=None):
        """
        Initialize manager

        Args:
            agent_id: ID of the agent
            event_bus: Reference to the event bus
            agent: Reference to the agent instance
        """
        self.agent_id = agent_id
        self.event_bus = event_bus
        self.agent = agent
        self._components: Dict[Type[Component], Component] = {}

    def add_component(self, component_class: Type[T], *args, **kwargs) -> T:
        """
        Add a component to the manager

        Args:
            component_class: The class of the component to add
            *args, **kwargs: Arguments to pass to component constructor

        Returns:
            The created component instance
        """
        # Create component instance
        # Note: We assume agent_id and event_bus are the first two args expected by Component
        component = component_class(self.agent_id, self.event_bus, *args, **kwargs)
        
        # Inject agent reference
        component.agent = self.agent
        
        self._components[component_class] = component
        return component

    def get_component(self, component_class: Type[T]) -> Optional[T]:
        """
        Get a component by its class

        Args:
            component_class: The class of the component to retrieve

        Returns:
            Component instance or None
        """
        return self._components.get(component_class)

    def has_component(self, component_class: Type[Component]) -> bool:
        """
        Check if a component exists

        Args:
            component_class: The class of the component to check

        Returns:
            True if component exists
        """
        return component_class in self._components

    def get_all_components(self) -> List[Component]:
        """
        Get all components

        Returns:
            List of all component instances
        """
        return list(self._components.values())

    def tick(self, delta_time: float):
        """
        Update all components

        Args:
            delta_time: Time elapsed in minutes
        """
        for component in self._components.values():
            component.tick(delta_time)

    def serialize(self) -> Dict[str, Any]:
        """
        Serialize all components

        Returns:
            Dictionary mapping component names to their serialized state
        """
        data = {}
        for component in self._components.values():
            data[component.get_component_name()] = component.serialize()
        return data

    def deserialize(self, data: Dict[str, Any]):
        """
        Deserialize all components

        Args:
            data: Dictionary mapping component names to their serialized state
        """
        for component in self._components.values():
            name = component.get_component_name()
            if name in data:
                component.deserialize(data[name])
