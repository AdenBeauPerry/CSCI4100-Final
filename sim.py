"""
Interactive Simulation for Event Scheduling System
Allows user to input tasks dynamically and manage the schedule
"""

import json
from event_class import Event
from event_scheduler import EventScheduler


def print_menu():
    """Display the main menu"""
    print("\n" + "=" * 70)
    print("Event Scheduling System - Main Menu")
    print("=" * 70)
    print("1. Add a new task")
    print("2. View all tasks")
    print("3. Remove a task")
    print("4. Modify a task")
    print("5. Generate schedule")
    print("6. View current schedule")
    print("7. Check deadlines")
    print("8. Load tasks from JSON file")
    print("9. Save tasks to JSON file")
    print("0. Exit")
    print("=" * 70)


def get_int_input(prompt, default=None, allow_negative=False):
    """Get integer input with validation"""
    while True:
        try:
            value = input(prompt)
            if value == "" and default is not None:
                return default
            num = int(value)
            if not allow_negative and num < 0:
                print("Please enter a non-negative number.")
                continue
            return num
        except ValueError:
            print("Invalid input. Please enter a number.")


def get_list_input(prompt):
    """Get list input (comma-separated)"""
    value = input(prompt)
    if not value.strip():
        return []
    return [item.strip() for item in value.split(",")]


def add_task_interactive(scheduler):
    """Add a task interactively"""
    print("\n--- Add New Task ---")
    name = input("Task name: ").strip()
    
    if not name:
        print("Task name cannot be empty!")
        return
    
    if name in scheduler.events:
        print(f"Task '{name}' already exists!")
        return
    
    duration = get_int_input("Duration (days): ")
    dependencies = get_list_input("Dependencies (comma-separated, leave empty for none): ")
    resources_required = get_int_input("Workers required: ", default=1)
    priority = get_int_input("Priority (1=highest): ", default=1)
    deadline = get_int_input("Deadline (days, -1 for no deadline): ", default=-1, allow_negative=True)
    
    event = Event(
        name=name,
        duration=duration,
        dependencies=dependencies,
        resources_required=resources_required,
        priority=priority,
        deadline=deadline
    )
    
    scheduler.add_event(event)
    print(f"Task '{name}' added.")


def view_all_tasks(scheduler):
    """Display all tasks"""
    if not scheduler.events:
        print("\nNo tasks in the system.")
        return
    
    print("\n--- All Tasks ---")
    for name, event in sorted(scheduler.events.items()):
        deps = ", ".join(event.dependencies) if event.dependencies else "None"
        deadline_str = f"{event.deadline} days" if event.deadline > 0 else "No deadline"
        print(f"\nTask: {name}")
        print(f"  Duration: {event.duration} days")
        print(f"  Dependencies: {deps}")
        print(f"  Workers Required: {event.resources_required}")
        print(f"  Priority: {event.priority}")
        print(f"  Deadline: {deadline_str}")


def remove_task_interactive(scheduler):
    """Remove a task interactively"""
    if not scheduler.events:
        print("\nNo tasks to remove.")
        return
    
    print("\n--- Remove Task ---")
    name = input("Task name to remove: ").strip()
    
    if scheduler.remove_event(name):
        print(f"Task '{name}' removed.")
    else:
        print(f"Task '{name}' not found.")


def modify_task_interactive(scheduler):
    """Modify a task interactively"""
    if not scheduler.events:
        print("\nNo tasks to modify.")
        return
    
    print("\n--- Modify Task ---")
    name = input("Task name to modify: ").strip()
    
    if name not in scheduler.events:
        print(f"Task '{name}' not found.")
        return
    
    event = scheduler.events[name]
    print(f"\nCurrent values for task '{name}':")
    print(f"  Duration: {event.duration}")
    print(f"  Dependencies: {', '.join(event.dependencies) if event.dependencies else 'None'}")
    print(f"  Workers Required: {event.resources_required}")
    print(f"  Priority: {event.priority}")
    print(f"  Deadline: {event.deadline}")
    
    print("\nEnter new values (press Enter to keep current value):")
    
    updates = {}
    
    duration_input = input(f"Duration [{event.duration}]: ").strip()
    if duration_input:
        updates['duration'] = int(duration_input)
    
    deps_input = input(f"Dependencies [{', '.join(event.dependencies) if event.dependencies else 'None'}]: ").strip()
    if deps_input:
        updates['dependencies'] = [d.strip() for d in deps_input.split(",")] if deps_input else []
    
    resources_input = input(f"Workers Required [{event.resources_required}]: ").strip()
    if resources_input:
        updates['resources_required'] = int(resources_input)
    
    priority_input = input(f"Priority [{event.priority}]: ").strip()
    if priority_input:
        updates['priority'] = int(priority_input)
    
    deadline_input = input(f"Deadline [{event.deadline}]: ").strip()
    if deadline_input:
        updates['deadline'] = int(deadline_input)
    
    if updates:
        scheduler.modify_event(name, **updates)
        print(f"Task '{name}' modified.")
    else:
        print("No changes made.")


def generate_schedule(scheduler):
    """Generate and display the schedule"""
    if not scheduler.events:
        print("\nNo tasks to schedule.")
        return
    
    try:
        print("\n--- Generating Schedule ---")
        scheduler.schedule_events()
        scheduler.print_schedule()
    except ValueError as e:
        print(f"\nError generating schedule: {e}")


def view_schedule(scheduler):
    """View the current schedule without regenerating"""
    if not scheduler.schedule:
        print("\nNo schedule generated yet. Use option 5 to generate a schedule.")
        return
    
    scheduler.print_schedule()


def check_deadlines(scheduler):
    """Check and display deadline status"""
    if not scheduler.schedule:
        print("\nNo schedule generated yet. Use option 5 to generate a schedule.")
        return
    
    missed = scheduler.check_deadlines()
    
    print("\n--- Deadline Status ---")
    if not missed:
        print("All deadlines met.")
    else:
        print("Deadline Violations:")
        for event_name, deadline, actual_end in missed:
            print(f"  Task {event_name}: Deadline was {deadline}, finished at {actual_end} (Missed by {actual_end - deadline} days)")


def load_tasks_from_json(scheduler, filename):
    """Load tasks from a JSON file"""
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
        
        # Clear existing tasks if requested
        if scheduler.events:
            response = input("Clear existing tasks? (y/n): ").strip().lower()
            if response == 'y':
                scheduler.events = {}
                scheduler.schedule = {}
        
        # Load tasks
        for task_data in data['tasks']:
            event = Event(
                name=task_data['name'],
                duration=task_data['duration'],
                dependencies=task_data.get('dependencies', []),
                resources_required=task_data.get('resources_required', 1),
                priority=task_data.get('priority', 1),
                deadline=task_data.get('deadline', -1)
            )
            scheduler.add_event(event)
        
        # Update total resources if specified
        if 'total_resources' in data:
            scheduler.total_resources = data['total_resources']
        
        print(f"Loaded {len(data['tasks'])} tasks from '{filename}'")
        print(f"Total resources available: {scheduler.total_resources}")
        
    except FileNotFoundError:
        print(f"File '{filename}' not found.")
    except json.JSONDecodeError:
        print(f"Invalid JSON format in '{filename}'.")
    except Exception as e:
        print(f"Error loading file: {e}")


def save_tasks_to_json(scheduler, filename):
    """Save tasks to a JSON file"""
    try:
        tasks_data = []
        for name, event in scheduler.events.items():
            tasks_data.append({
                'name': event.name,
                'duration': event.duration,
                'dependencies': event.dependencies,
                'resources_required': event.resources_required,
                'priority': event.priority,
                'deadline': event.deadline
            })
        
        data = {
            'total_resources': scheduler.total_resources,
            'tasks': tasks_data
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Saved {len(tasks_data)} tasks to '{filename}'")
        
    except Exception as e:
        print(f"Error saving file: {e}")


def main():
    """Main simulation loop"""
    print("\n" + "=" * 70)
    print("Welcome to the Event Scheduling System")
    print("=" * 70)
    
    # Get total resources
    total_resources = get_int_input("\nEnter total workers/resources available: ", default=4)
    scheduler = EventScheduler(total_resources=total_resources)
    
    print(f"\nScheduler initialized with {total_resources} workers.")
    
    # Ask if user wants to load from file
    load_file = input("\nLoad tasks from JSON file? (y/n): ").strip().lower()
    if load_file == 'y':
        filename = input("Enter filename: ").strip()
        load_tasks_from_json(scheduler, filename)
    
    # Main loop
    while True:
        print_menu()
        choice = input("\nEnter your choice (0-9): ").strip()
        
        if choice == '1':
            add_task_interactive(scheduler)
        elif choice == '2':
            view_all_tasks(scheduler)
        elif choice == '3':
            remove_task_interactive(scheduler)
        elif choice == '4':
            modify_task_interactive(scheduler)
        elif choice == '5':
            generate_schedule(scheduler)
        elif choice == '6':
            view_schedule(scheduler)
        elif choice == '7':
            check_deadlines(scheduler)
        elif choice == '8':
            filename = input("Enter filename to load: ").strip()
            load_tasks_from_json(scheduler, filename)
        elif choice == '9':
            filename = input("Enter filename to save: ").strip()
            save_tasks_to_json(scheduler, filename)
        elif choice == '0':
            print("\nThank you for using the Event Scheduling System!")
            break
        else:
            print("\nInvalid choice.")
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
