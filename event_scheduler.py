"""
Multi-Team Event Scheduling System with Resource Constraints and Dependencies
Handles topological sorting, resource allocation, deadlines, and dynamic task modifications
"""

from typing import List, Dict, Tuple, Optional
from collections import deque, defaultdict
import heapq
from event_class import Event


class EventScheduler:
    def __init__(self, total_resources: int):
        """
        Initialize the Event Scheduler
        
        Args:
            total_resources: Total number of workers/resources available
        """
        self.total_resources = total_resources
        self.events: Dict[str, Event] = {}
        self.schedule: Dict[str, Tuple[int, int]] = {}  # event_name -> (start_time, end_time)
        
    def add_event(self, event: Event) -> None:
        """Add an event to the scheduler"""
        self.events[event.name] = event
        
    def remove_event(self, event_name: str) -> bool:
        """Remove an event from the scheduler"""
        if event_name in self.events:
            del self.events[event_name]
            if event_name in self.schedule:
                del self.schedule[event_name]
            return True
        return False
    
    def modify_event(self, event_name: str, **kwargs) -> bool:
        """
        Modify an existing event's properties
        
        Args:
            event_name: Name of the event to modify
            **kwargs: Properties to update (duration, dependencies, resources_required, priority, deadline)
        """
        if event_name not in self.events:
            return False
            
        event = self.events[event_name]
        if 'duration' in kwargs:
            event.duration = kwargs['duration']
        if 'dependencies' in kwargs:
            event.dependencies = kwargs['dependencies']
        if 'resources_required' in kwargs:
            event.resources_required = kwargs['resources_required']
        if 'priority' in kwargs:
            event.priority = kwargs['priority']
        if 'deadline' in kwargs:
            event.deadline = kwargs['deadline']
        return True
    
    def topological_sort(self) -> List[str]:
        """
        Perform topological sort using Kahn's algorithm with priority and name as tiebreakers
        Returns sorted list of event names
        """
        in_degree = defaultdict(int)
        adj_list = defaultdict(list)

        for event_name in self.events:
            in_degree[event_name] = 0

        for event_name, event in self.events.items():
            for dependency in event.dependencies:
                if dependency not in self.events:
                    raise ValueError(f"Event '{event_name}' depends on unknown event '{dependency}'")
                adj_list[dependency].append(event_name)
                in_degree[event_name] += 1

        # Use (priority, name) for stable ordering
        ready_nodes = [(self.events[name].priority, name) for name in self.events if in_degree[name] == 0]
        ready_nodes.sort()  # sort by (priority, name)
        ready_heap = []
        for item in ready_nodes:
            heapq.heappush(ready_heap, item)

        sorted_order = []


        while ready_heap:
            # Gather all nodes currently available (all with in-degree 0)
            current_level = []
            while ready_heap:
                _, current = heapq.heappop(ready_heap)
                current_level.append(current)
            # Sort current_level by (priority, name) for stability
            current_level = sorted(current_level, key=lambda n: (self.events[n].priority, n))
            newly_ready = []
            for current in current_level:
                sorted_order.append(current)
                for neighbor in adj_list[current]:
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        newly_ready.append(neighbor)
            # Add all newly ready nodes to heap, sorted by (priority, name)
            for neighbor in sorted(newly_ready, key=lambda n: (self.events[n].priority, n)):
                heapq.heappush(ready_heap, (self.events[neighbor].priority, neighbor))

        if len(sorted_order) != len(self.events):
            raise ValueError("Cycle detected in task dependencies!")

        return sorted_order
    
    def schedule_events(self) -> Dict[str, Tuple[int, int]]:
        """
        Schedule events with resource constraints
        Returns a dictionary mapping event names to (start_time, end_time)
        """
        # Clear previous schedule
        self.schedule = {}
        
        # Get topological order
        sorted_events = self.topological_sort()
        
        # Resource allocation using event-based simulation
        scheduled = set()
        
        # Priority queue: (priority, event_name)
        ready_queue = []
        
        # Track events waiting for dependencies
        waiting = {}
        for event_name in sorted_events:
            event = self.events[event_name]
            if not event.dependencies:
                heapq.heappush(ready_queue, (event.priority, event_name))
            else:
                waiting[event_name] = set(event.dependencies)
        
        current_time = 0
        active_resources = 0
        active_events = []  # List of (end_time, event_name, resources_used)
        
        while ready_queue or active_events or waiting:
            # Complete events finishing at current time
            while active_events and active_events[0][0] == current_time:
                _, completed_name, resources_used = heapq.heappop(active_events)
                active_resources -= resources_used
                scheduled.add(completed_name)
                
                # Check if any waiting events can now be ready
                for event_name in list(waiting.keys()):
                    if completed_name in waiting[event_name]:
                        waiting[event_name].remove(completed_name)
                        if len(waiting[event_name]) == 0:
                            event = self.events[event_name]
                            heapq.heappush(ready_queue, (event.priority, event_name))
                            del waiting[event_name]
            
            # Try to schedule ready events that have sufficient resources
            temp_queue = []
            scheduled_this_round = False
            
            while ready_queue:
                priority, event_name = heapq.heappop(ready_queue)
                event = self.events[event_name]
                
                # Check resource availability
                if active_resources + event.resources_required <= self.total_resources:
                    # Calculate start time (max of current time and all dependency end times)
                    start_time = current_time
                    if event.dependencies:
                        dep_end_times = [self.schedule[dep][1] for dep in event.dependencies]
                        start_time = max(start_time, max(dep_end_times))
                    
                    end_time = start_time + event.duration
                    self.schedule[event_name] = (start_time, end_time)
                    
                    active_resources += event.resources_required
                    heapq.heappush(active_events, (end_time, event_name, event.resources_required))
                    scheduled_this_round = True
                else:
                    # Not enough resources, defer
                    temp_queue.append((priority, event_name))
            
            # Restore deferred events
            for item in temp_queue:
                heapq.heappush(ready_queue, item)
            
            # Advance time to next event completion or wait
            if active_events:
                current_time = active_events[0][0]
            elif ready_queue and not scheduled_this_round:
                # Deadlock: need to wait for resources but nothing is completing
                # This shouldn't happen with proper resource management
                break
        
        return self.schedule
    
    def check_deadlines(self) -> List[Tuple[str, int, int]]:
        """
        Check which events missed their deadlines
        Returns list of (event_name, deadline, actual_completion_time)
        """
        missed = []
        for event_name, (start, end) in self.schedule.items():
            event = self.events[event_name]
            if event.deadline > 0 and end > event.deadline:
                missed.append((event_name, event.deadline, end))
        return missed
    
    def get_total_completion_time(self) -> int:
        """Get the total project completion time"""
        if not self.schedule:
            return 0
        return max(end for start, end in self.schedule.values())
    
    def print_schedule(self) -> None:
        """Print the complete schedule with details"""
        sorted_order = self.topological_sort()
        print(f"\nSorted Task Execution Order (Topological Sort): {sorted_order}")
        print("\nTask Schedule:")
        
        for event_name in sorted_order:
            if event_name in self.schedule:
                start, end = self.schedule[event_name]
                event = self.events[event_name]
                deadline_info = f", Deadline: {event.deadline}" if event.deadline > 0 else ""
                print(f"Task {event_name}: Start at {start}, End at {end} "
                      f"(Workers: {event.resources_required}{deadline_info})")
        
        total_time = self.get_total_completion_time()
        print(f"\nTotal Project Completion Time: {total_time}")
        
        # Check deadlines
        missed = self.check_deadlines()
        if missed:
            print("\nDEADLINE VIOLATIONS:")
            for event_name, deadline, actual_end in missed:
                print(f"Task {event_name}: Deadline was {deadline}, finished at {actual_end} "
                      f"(Missed by {actual_end - deadline} days)")
        else:
            print("\nAll deadlines met.")



