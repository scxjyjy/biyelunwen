import pandas as pd

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
    next_border_states = set()
    IsEnd = False
    for state in state_set:
        for trans_symbol, next_state in state.transition:
            if trans_symbol == symbol:
                if next_state.isBorder:
                    next_border_states.add(next_state)
                else:
                    next_states.add(next_state)
                if next_state.isEnd:
                    IsEnd = True
    return next_border_states,next_states,IsEnd


def nfa_to_hfa(start_state):
    # 首先去除所有 epsilon 转移
    #remove_epsilon_transitions(start_state)
    #initial_set = epsilon_closure(start_state)
    initial_set = [start_state]
    state_queue = [frozenset(initial_set)]
    visited_sets = {frozenset(initial_set): 0}
    dfa_states = [initial_set]
    nfa_states = set()
    nfa_visited_states = set()
    dfa_transitions = []
    nfa_transitions = []
    Hfa_states_label = [visited_sets[frozenset(initial_set)]]
    hfa_transitions = []
    dfa_accept_states = []
    nfa_accept_states = []
    hfa_accept_states = []
    bordertoNFA_states = {}
    while state_queue:
        current_set = state_queue.pop(0)
        current_state_index = visited_sets[frozenset(current_set)]
        isEnd = False
        # 处理所有转移
        symbol_set = set(sym for state in current_set for sym, _ in state.transition)
        print(symbol_set)
        for symbol in symbol_set:
            border_set,new_set,isEnd = move(current_set, symbol)
            if frozenset(new_set) not in visited_sets:
                visited_sets[frozenset(new_set)] = len(dfa_states)
                state_queue.append(frozenset(new_set))
                dfa_states.append(new_set)
                dfa_transitions.append((current_state_index, symbol, visited_sets[frozenset(new_set)]))
                hfa_transitions.append((current_state_index, symbol, visited_sets[frozenset(new_set)]))
                Hfa_states_label.append(visited_sets[frozenset(new_set)])
            else:
                dfa_transitions.append((current_state_index, symbol, visited_sets[frozenset(new_set)]))
                hfa_transitions.append((current_state_index, symbol, visited_sets[frozenset(new_set)]))
                Hfa_states_label.append(visited_sets[frozenset(new_set)])
            if border_set:
                for borderstate in border_set:
                    bordertoNFA_states[borderstate] = visited_sets[frozenset(new_set)]
                    print("borderstate:")
                    print(bordertoNFA_states[borderstate])
                    nfa_states.add(borderstate)
    def get_all_states(current_state,NFALabel):
        if current_state not in nfa_visited_states:
            nfa_visited_states.add(current_state)
            bordertoNFA_states[current_state] = NFALabel
            NFALabel = NFALabel + 1
            if current_state.isEnd == True:
                return
            #ru guo  shi  zhong  jian  yi duan  jiu  ke ke yi shi  yon  IsborderEnd zuo  wei  zhong zhi tiao jian
            for symbol, next_state in current_state.transition:
                get_all_states(next_state,NFALabel)


    nfa_non_border_initlabel = len(dfa_states)
    print(nfa_non_border_initlabel)
    StateVectorSize = 24
    NumberofborderState = len(nfa_states)
    #Ensure that the next state for sub-regular expressions in an NFA is at the same level.
    if len(nfa_states)%StateVectorSize > 24:
        NumberofborderState = len(nfa_states)-len(nfa_states)%StateVectorSize + 24

    nfa_visited_states = nfa_states.copy()
    #xian dui dfa  bian ma, zai dui nfa bianma,liang ge  bian ma lian  xu
    for borderstate in nfa_states:
        print("borderstate:")
        print(bordertoNFA_states[borderstate])
        for symbol, next_state in borderstate.transition:
            get_all_states(next_state,nfa_non_border_initlabel)
            nfa_non_border_initlabel = nfa_non_border_initlabel + len(nfa_visited_states)


    nfa_states = nfa_visited_states.copy()
    for state in nfa_states:
        for symbol, next_state in state.transition:
            nfa_transitions.append((bordertoNFA_states[state], symbol, bordertoNFA_states[next_state]))
            hfa_transitions.append((bordertoNFA_states[state], symbol, bordertoNFA_states[next_state]))

    # 标识接收状态
    for index, state_set in enumerate(dfa_states):
        if any(state.isEnd for state in state_set):
            dfa_accept_states.append(visited_sets[frozenset(state_set)])
            hfa_accept_states.append(visited_sets[frozenset(state_set)])

    for state in nfa_states:
        Hfa_states_label.append(bordertoNFA_states[state])
        if state.isEnd:
            nfa_accept_states.append(bordertoNFA_states[state])
            hfa_accept_states.append(bordertoNFA_states[state])

    return dfa_states, Hfa_states_label,dfa_transitions,nfa_transitions, hfa_transitions,dfa_accept_states,nfa_accept_states,hfa_accept_states

def hfa_to_table(hfa_transitions,hfa_accept_states):
    global TransitionTable
    # 创建一个空的DataFrame来存储状态转移信息
    TransitionTable = pd.DataFrame(columns=['State','Symbol', 'NextState','IsEnd'])
    # 填充 DataFrame
    for start_state, symbol, next_state in hfa_transitions:
        # 检查 next_state 是否在接受状态列表中
        is_end = next_state in hfa_accept_states
        hfa_accept_states_str = [str(state) for state in hfa_accept_states]
        # 添加新行到 DataFrame
        TransitionTable = TransitionTable.append({
            'State': str(start_state),
            'Symbol': symbol,
            'NextState': str(next_state),
            'IsEnd': is_end
        }, ignore_index=True)
    merged_TransitionTable = TransitionTable.groupby(['State', 'Symbol'])['NextState'].apply(','.join).reset_index()
    # 定义一个函数来确定是否包含接受状态
    def is_end_state(next_states):
        print("Next States:", next_states)
        for state in next_states.split(','):
            print("Checking state:", state)
            if state in hfa_accept_states_str:
                return True
        return False

    # 向 merged_TransitionTable 添加一个名为 IsEnd 的新字段
    merged_TransitionTable['IsEnd'] = merged_TransitionTable['NextState'].apply(is_end_state)

    # 打印 DataFrame
    print(TransitionTable.to_string(index=False, justify='left'))
    print(merged_TransitionTable.to_string(index=False, justify='left'))
    print(hfa_accept_states)
    return merged_TransitionTable
