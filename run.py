import heapq
import sys


COST_PER_STEP = {'A': 1, 'B': 10, 'C': 100, 'D': 1000}
TARGET_ROOM_INDEX = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
HALLWAY_ALLOWED_STOPS = [0, 1, 3, 5, 7, 9, 10]
ROOM_HALLWAY_POSITIONS = [2, 4, 6, 8]


def parse_initial_state(lines):
    hallway = tuple(lines[1][1:12])
    room_depth = len(lines) - 3
    rooms = []
    for room_index in range(4):
        room = []
        for depth_index in range(room_depth):
            room.append(lines[2 + depth_index][3 + 2 * room_index])
        rooms.append(tuple(room))
    return hallway, tuple(rooms)

def is_hallway_path_clear(hallway, start_pos, end_pos):
    path_range = range(start_pos + 1, end_pos + 1) if start_pos < end_pos else range(end_pos, start_pos)
    for pos in path_range:
        if hallway[pos] != '.':
            return False
    return True

def get_available_room_depth_for_entry(rooms, amphipod_type):
    target_room = TARGET_ROOM_INDEX[amphipod_type]
    room = rooms[target_room]
    for occupant in room:
        if occupant not in ('.', amphipod_type):
            return None
    for depth_index in range(len(room) - 1, -1, -1):
        if room[depth_index] == '.':
            return depth_index
    return None

def generate_moves_from_room_to_hallway(state):
    hallway, rooms = state
    for room_index, room in enumerate(rooms):
        for depth_index, amphipod_type in enumerate(room):
            if amphipod_type != '.':
                break
        else:
            continue
        all_correct = all(occupant == '.' or TARGET_ROOM_INDEX[occupant] == room_index for occupant in room)
        if all_correct:
            continue
        hall_pos = ROOM_HALLWAY_POSITIONS[room_index]
        for stop_pos in HALLWAY_ALLOWED_STOPS:
            if is_hallway_path_clear(hallway, hall_pos, stop_pos):
                steps = depth_index + 1 + abs(stop_pos - hall_pos)
                move_cost = steps * COST_PER_STEP[amphipod_type]
                new_hallway = list(hallway)
                new_rooms = [list(r) for r in rooms]
                new_hallway[stop_pos] = amphipod_type
                new_rooms[room_index][depth_index] = '.'
                yield (tuple(new_hallway), tuple(tuple(r) for r in new_rooms)), move_cost

def generate_moves_from_hallway_to_room(state):
    hallway, rooms = state
    for pos, amphipod_type in enumerate(hallway):
        if amphipod_type == '.':
            continue
        target_room = TARGET_ROOM_INDEX[amphipod_type]
        room_pos = ROOM_HALLWAY_POSITIONS[target_room]
        if not is_hallway_path_clear(hallway, pos, room_pos):
            continue
        depth_index = get_available_room_depth_for_entry(rooms, amphipod_type)
        if depth_index is None:
            continue
        steps = abs(pos - room_pos) + depth_index + 1
        move_cost = steps * COST_PER_STEP[amphipod_type]
        new_hallway = list(hallway)
        new_rooms = [list(r) for r in rooms]
        new_hallway[pos] = '.'
        new_rooms[target_room][depth_index] = amphipod_type
        yield (tuple(new_hallway), tuple(tuple(r) for r in new_rooms)), move_cost

def generate_valid_moves(state):
    for move in generate_moves_from_room_to_hallway(state):
        yield move
    for move in generate_moves_from_hallway_to_room(state):
        yield move

def estimate_remaining_cost(state):
    hallway, rooms = state
    total = 0
    for pos, amphipod_type in enumerate(hallway):
        if amphipod_type == '.':
            continue
        target_room = TARGET_ROOM_INDEX[amphipod_type]
        target_pos = ROOM_HALLWAY_POSITIONS[target_room]
        total += (abs(pos - target_pos) + 1) * COST_PER_STEP[amphipod_type]
    for room_index, room in enumerate(rooms):
        for depth_index, amphipod_type in enumerate(room):
            if amphipod_type == '.':
                continue
            target_room = TARGET_ROOM_INDEX[amphipod_type]
            blocking = any(occupant not in ('.', amphipod_type) for occupant in room[depth_index:])
            if target_room != room_index or blocking:
                from_pos = ROOM_HALLWAY_POSITIONS[room_index]
                to_pos = ROOM_HALLWAY_POSITIONS[target_room]
                total += (depth_index + 1 + abs(from_pos - to_pos) + 1) * COST_PER_STEP[amphipod_type]
    return total

def solve_amphipod_sorting(lines):
    start_state = parse_initial_state(lines)
    room_depth = len(start_state[1][0])
    target_rooms = tuple(tuple(amphipod for _ in range(room_depth)) for amphipod in ('A', 'B', 'C', 'D'))
    target_state = (tuple('.' for _ in range(11)), target_rooms)

    priority_queue = [(estimate_remaining_cost(start_state), 0, start_state)]
    best_costs = {start_state: 0}

    while priority_queue:
        estimated_total, current_cost, current_state = heapq.heappop(priority_queue)
        if current_state == target_state:
            return current_cost
        if current_cost > best_costs[current_state]:
            continue
        for next_state, move_cost in generate_valid_moves(current_state):
            new_cost = current_cost + move_cost
            if next_state not in best_costs or new_cost < best_costs[next_state]:
                best_costs[next_state] = new_cost
                heapq.heappush(priority_queue, (new_cost + estimate_remaining_cost(next_state), new_cost, next_state))
    return -1


def main():
    lines = []
    for line in sys.stdin:
        lines.append(line.rstrip('\n'))
    print(solve_amphipod_sorting(lines))


if __name__ == "__main__":
    main()
