def epsilon_closure(state, visited=None):
    # 由于已经去除了 epsilon 转移，这个函数现在只返回当前状态
    if visited is None:
        visited = set()
    if state not in visited:
        visited.add(state)
        return {state}
    return set()

def move(state_set, symbol):
    next_states = set()
    for state in state_set:
        for trans_symbol, next_state in state.transition:
            if trans_symbol == symbol:
                next_states.add(next_state)
    return next_states

def nfa_to_dfa(start_state):
    # 首先去除所有 epsilon 转移
    #remove_epsilon_transitions(start_state)

    initial_set = epsilon_closure(start_state)
    state_queue = [frozenset(initial_set)]
    visited_sets = {frozenset(initial_set): 0}
    dfa_states = [initial_set]
    dfa_transitions = []
    dfa_accept_states = []

    while state_queue:
        current_set = state_queue.pop(0)
        current_state_index = visited_sets[frozenset(current_set)]

        # 处理所有转移
        symbol_set = set(sym for state in current_set for sym, _ in state.transition)
        print(symbol_set)
        for symbol in symbol_set:
            new_set = move(current_set, symbol)
            if frozenset(new_set) not in visited_sets:
                visited_sets[frozenset(new_set)] = len(dfa_states)
                state_queue.append(frozenset(new_set))
                dfa_states.append(new_set)
                dfa_transitions.append((current_state_index, symbol, visited_sets[frozenset(new_set)]))
            else:
                dfa_transitions.append((current_state_index, symbol, visited_sets[frozenset(new_set)]))

    # 标识接收状态
    for index, state_set in enumerate(dfa_states):
        if any(state.isEnd for state in state_set):
            dfa_accept_states.append(index)

    return dfa_states, dfa_transitions, dfa_accept_states

# 使用示例
#start, end = fromSymbol('a')  # 示例 NFA
#nfa = NFA(start, end)
#dfa_states, dfa_transitions, dfa_accept_states = nfa_to_dfa(nfa.start)

# 打印 DFA 状态和转移
#print("DFA States:")
#for i, states in enumerate(dfa_states):
#    print(f"State {i}: {states}")

#print("\nDFA Transitions:")
#for from_state, symbol, to_state in dfa_transitions:
#    print(f"{from_state} --{symbol}--> {to_state}")

#print("\nDFA Accept States:")
#print(dfa_accept_states)
