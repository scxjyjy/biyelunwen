# -*- coding: utf-8 -*-
import pandas as pd
import jsonio as jsio
import json
from sendjson import json_to_cli
from NFAtoDFA import nfa_to_dfa
from NFAtoHFA import nfa_to_hfa
from NFAtoHFA import hfa_to_table
from multiStride import simple_increase_table
StatePart = 24
def add_explicit_concatenation(infix):
    # 初始化结果字符串
    output = ""

    # 遍历输入的正则表达式中的每一个字符
    for i in range(len(infix)):
        output += infix[i]

        # 如果当前字符不是最后一个字符，并且满足添加连接符的条件
        if (i < len(infix) - 1 and
            (infix[i] not in '(*|' and infix[i+1] not in ')*|' or
             infix[i] in '+?*' and infix[i+1] not in ')|')):
            output += '.'

    return output
def shunt(infix):
    # Curly braces = dictionary
    # *, | are repetition operators. They take precedence over concatenation and alternation operators
    # * = Zero or more
    # . = Concatenation
    # | =  Alternation
    specials = {'*': 50, '.': 40, '|': 30}

    pofix = ""
    stack = ""

    # Loop through the string one character at a time
    for c in infix:
        if c == '(':
            stack = stack + c
        elif c == ')':
            while stack[-1] != '(':
                pofix, stack = pofix + stack[-1], stack[:-1]
            # Remove '(' from stack
            stack = stack[:-1]
        elif c in specials:
            while stack and specials.get(c, 0) <= specials.get(stack[-1], 0):
                pofix, stack = pofix + stack[-1], stack[:-1]
            stack = stack + c
        else:
            pofix = pofix + c

    while stack:
        pofix, stack = pofix + stack[-1], stack[:-1]

    return pofix


class NFA:
    def __init__(self, start, end):
        self.start = start
        self.end = end

#通过状态记录NFA的信息，类似链表，好处是不需要状态编码，但是如果要变为表还是要进行状态编码
class State:
    def __init__(self, isEnd):
        self.isEnd = isEnd
        self.isBorder = False
        self.transition = []
        self.epsilonTransitions = []
        self.label = None  # 添加 label 属性并初始化为 None，用于全部编码
    def SetBorder(self,isBorder):
        self.isBorder = isBorder
def addEpsilonTransition(come, to):
    come.epsilonTransitions.append(to)

def addTransiton(come, to, symbol):
    come.transition.append((symbol,to))

def fromEpsilon():
    start = State(False)
    end = State(True)
    addEpsilonTransition(start, end)

    return start, end

def fromSymbol(symbol):
    start = State(False)
    end = State(True)
    addTransiton(start, end, symbol)

    return start, end

def createNFA(symbol):
    start, end = fromSymbol(symbol)
    return NFA(start, end)
# both start and end are States
def union(first, second):
    start = State(False);
    addEpsilonTransition(start, first.start)
    addEpsilonTransition(start, second.start)

    end = State(True)
    addEpsilonTransition(first.end, end)
    first.end.isEnd = False
    addEpsilonTransition(second.end, end)
    second.end.isEnd = False

    return NFA(start, end)
def closure(nfa):
    start = State(False)
    end = State(True)

    addEpsilonTransition(start, end)
    addEpsilonTransition(start, nfa.start)

    addEpsilonTransition(nfa.end, end)
    addEpsilonTransition(nfa.end, nfa.start)

    nfa.end.isEnd = False
    start.SetBorder(True)
    return NFA(start, end)

def concat(first, second):
    addEpsilonTransition(first.end, second.start)
    first.end.isEnd = False

    return NFA(first.start, second.end)

def toNFA(postfix):
    if postfix == '':
        return fromEpsilon()

    stack = []
    for c in postfix:
        if c == '.':
            if len(stack) >= 2:
                nfa2 = stack.pop()
                nfa1 = stack.pop()
                new_nfa = concat(nfa1, nfa2)
                stack.append(new_nfa)
            else:
                print("错误：连接操作需要两个操作数，但堆栈中没有足够的元素")
                exit(1)
        elif c == '|':
            if len(stack) >= 2:
                nfa2 = stack.pop()
                nfa1 = stack.pop()
                new_nfa = union(nfa1, nfa2)
                stack.append(new_nfa)
            else:
                print("错误：选择操作需要两个操作数，但堆栈中没有足够的元素")
                exit(1)
        elif c == '*':
            if len(stack) >= 1:
                nfa = stack.pop()
                new_nfa = closure(nfa)
                stack.append(new_nfa)
            else:
                print("错误：闭包操作需要一个操作数，但堆栈中没有足够的元素")
                exit(1)
        else:
            nfa = createNFA(c)
            stack.append(nfa)

    final_nfa = stack.pop()
    # 去空边


    return final_nfa

def encoded_state_value_str(state):
    # 寻找二进制中最后一个1的位置
    state_int = int(state)
    DepthMask = 0xFF
    encoded_state = 0
    positon = state_int%24
    x =  (state_int//24)& DepthMask
    depth = (x << 24)
    encoded_state = depth|(1<<positon)
     # 转换为二进制字符串并去掉前缀 '0b'
    #binary_string = bin(encoded_state)[2:]

    # 确保字符串长度至少为64位，前面用'0'填充
    #binary_string = binary_string.zfill(64)

    return str(encoded_state)

def encoded_state_value_int(state):
    # 寻找二进制中最后一个1的位置
    state_int = int(state)
    DepthMask = 0xFF
    encoded_state = 0
    positon = state_int%24
    x =  (state_int//24)& DepthMask
    depth = (x << 24)
    encoded_state = depth|(1<<positon)
    return encoded_state

def remove_epsilon_transitions(state):
    visited_states = set()

    def dfs_remove_epsilon(current_state):
        if current_state in visited_states:
            return
        visited_states.add(current_state)

        if current_state.epsilonTransitions:
            for epsilon_transition in current_state.epsilonTransitions:
                dfs_remove_epsilon(epsilon_transition)

            # 合并 epsilon 转移
            epsilon_transitions = list(current_state.epsilonTransitions)
            for epsilon_transition in epsilon_transitions:
                for symbol, next_state in epsilon_transition.transition:
                    addTransiton(current_state, next_state, symbol)
                if epsilon_transition.isEnd:
                    current_state.isEnd = True
                if epsilon_transition.isBorder:
                    current_state.isBorder = True
            # 清空当前状态的 epsilon 转移
            current_state.epsilonTransitions = []
        elif current_state.transition:
            for  symbol, next_state in current_state.transition:
                dfs_remove_epsilon(next_state)

    dfs_remove_epsilon(state)

def nfa_to_table(nfa):
    global TransitionTable
    # 创建一个空的DataFrame来存储状态转移信息
    TransitionTable = pd.DataFrame(columns=['State', 'IsEnd', 'Symbol', 'NextState'])
    states = set()
    def get_all_states(current_state):
        if current_state not in states:
            states.add(current_state)
            current_state.label = len(states) - 1  # 分配递增的编码
            for symbol, next_state in current_state.transition:
#               print("nextstate={}{}{}".format(next_state,symbol,len(current_state.transition)))
                get_all_states(next_state)
#  ????
            if current_state.isEnd == True:
                return
    get_all_states(nfa.start)
    # 添加状态转移信息到 DataFrame
    AcceptStates = []
    for state in sorted(list(states), key=lambda x: x.label):
        print("Is accept State? "+str(state.label)+str(state.isEnd))
        print("Is Border State? "+str(state.label)+str(state.isBorder))
        if state.isEnd:
            AcceptStates.append(str(state.label))

        is_end = "True" if state.isEnd else "False"
        for symbol, next_state in state.transition:
#            next_states = []
#            next_states.append(str(next_state.label))
            TransitionTable = TransitionTable.append({'State': state.label, 'IsEnd': is_end, 'Symbol': symbol, 'NextState': str(next_state.label)}, ignore_index=True)

    # 使用 groupby 和 agg 方法来合并 'NextState' 字段
    merged_TransitionTable = TransitionTable.groupby(['State', 'Symbol'])['NextState'].apply(','.join).reset_index()
    # 定义一个函数来确定是否包含接受状态
    def is_end_state(next_states):
        print("Next States:", next_states)
        for state in next_states.split(','):
            print("Checking state:", state)
            if state in AcceptStates:
                return True
        return False

    # 向 merged_TransitionTable 添加一个名为 IsEnd 的新字段
    merged_TransitionTable['IsEnd'] = merged_TransitionTable['NextState'].apply(is_end_state)

    # 打印 DataFrame
    print(TransitionTable.to_string(index=False, justify='left'))
    print(merged_TransitionTable.to_string(index=False, justify='left'))
    print(AcceptStates)
    return merged_TransitionTable

def stack_to_Table(hfa_states_label,hfa_accept_states):
    global StackTable
    # 创建一个空的DataFrame来存储状态转移信息,IntState is  Int format  BitState is bit format
    StackTable = pd.DataFrame(columns=['BitState', 'IsEnd','IntState','ClearMask','BitStateMask'])

    # 填充DataFrame
    depth_mask = (1 << StatePart) - 1
    for label in hfa_states_label:
        print(label)
        is_end = False
        bit_state = encoded_state_value_int(label)
        if label in hfa_accept_states:
            is_end = True
        #bit_state = (1 << label) # 转换为128位的二进制字符串
        clear_mask =  ~(bit_state) & depth_mask  # 1左移label位数并转换为128位二进制字符串
        #bit_state_mask = (1 << label)
        bit_state_mask = bit_state
        StackTable = StackTable.append({
            'BitState': bit_state,
            'IsEnd': is_end,
            'IntState': label,
            'ClearMask': clear_mask,
            'BitStateMask': bit_state_mask
        }, ignore_index=True)
    # 按照 IsEnd 列排序，True 的排在前面
    StackTable = StackTable.sort_values(by='IsEnd', ascending=False).reset_index(drop=True)
    StackTable = StackTable.drop_duplicates()
    print(StackTable)
    return StackTable




def TableTojson(transitionTable,stackTable,k):
    #zhuan huan table bian chen command
    pipeline_name = "MyIngress"
    s1_runtime_config = {}
    s1_runtime_config["target"] = "bmv2"
    s1_runtime_config["p4info"] = "build/calc.p4.p4info.txt"
    s1_runtime_config["bmv2_json"] = "build/calc.json"
    s1_runtime_config["table_entries"] = []
    max_priority = len(transitionTable) + 1
    #cur_priority = max_priority
    cur_priority = 2;
    entry_lst = []

    print("runtime nfa  entries")
    for index, entry_idx in transitionTable.iterrows():
        #print(entry_idx)
        entry = {}
        entry["priority"] = cur_priority
        entry["table"] = pipeline_name + "." + "t_NFA_match_0"
         # 构建 match old字段
        #entry["match"] = {
        #    "meta.state": entry_idx["State"],
        #    "hdr.patrns[0].pattern": ord(entry_idx["Symbol"])
        #}
        # 构建 match new字段
         # 构建 match 字段
        entry["match"] = {
            #"meta.state": [int(entry_idx["State"]),255]
            "meta.state": int(entry_idx["State"])
        }
        chars = entry_idx["chars"]
        for i in range(min(k, len(chars))):
            entry["match"][f"hdr.patrns[{i}].pattern"] = [ord(chars[i]),0 if chars[i] == '*' else 255]

        action_params = {}
        if entry_idx["IsEnd"]:
            entry["action_name"] = pipeline_name + "." + "a_mark_as_to_send_backend"
            entry["action_params"] = action_params
        else:
            # 遍历 NextState 数组，并将值依次放入字典中
            entry["action_name"] = pipeline_name + "." + "pushNextStateVector"
            for i, value in enumerate(entry_idx["NextState"].split(','), start=1):
                if "StateMask" not in action_params:
                    action_params["StateMask"] = 0
                int_value = int(value)
                #action_params["StateMask"] |= (1 << int_value)
                action_params["StateMask"] |= encoded_state_value_int(int_value)

            entry["action_params"] = action_params

        cur_priority += 1
        s1_runtime_config["table_entries"].append(entry)

    print("Pop Stack  entries")
    for index1, entry_idx1 in stackTable.iterrows():
        #print(entry_idx)
        entry = {}
        entry["priority"] = cur_priority
        entry["table"] = pipeline_name + "." + "t_popFirstStack"
         # 构建 match 字段
        entry["match"] = {
            "meta.Stack.CurrentStateVector":[entry_idx1["BitState"], entry_idx1["BitStateMask"]]
        }
        action_params = {}
        entry["action_name"] = pipeline_name + "." + "popCurrentStateVector"
        action_params["pop_value"] = entry_idx1["IntState"]
        action_params["clearMask"] = entry_idx1["ClearMask"]
        entry["action_params"] = action_params

        cur_priority += 1
        s1_runtime_config["table_entries"].append(entry)

    jsio.store(s1_runtime_config)

    with open("testNFA-runtime.json", 'w') as outfile:
        json.dump(s1_runtime_config, outfile, indent=2)
    return


if __name__ == "__main__":
    # 在这里编写主要的程序逻辑
    K = 2
    #regex = 'bc(ac)*tt|(ac)*bmkk|eeeeeeeeeeabcd|opopop'
    #regex = 'a*.b|a.c'
    regex = 'abc|abmd'
    regex = add_explicit_concatenation(regex)
    print(regex)
    postfix1 = shunt(regex)
    print(postfix1)
    nfa = toNFA(postfix1)
    remove_epsilon_transitions(nfa.start)
    dfa_states, hfa_states_label,dfa_transitions, nfa_transitions,hfa_transitions,dfa_accept_states,nfa_accept_states,hfa_accept_states = nfa_to_hfa(nfa.start)
    transitionTable = hfa_to_table(hfa_transitions,hfa_accept_states)
    print(transitionTable)
    #k-stride
    transitionTableKstride = simple_increase_table(transitionTable,K)
    print(transitionTableKstride)
    #transitionTable['State'] = transitionTable['State'].apply(encoded_state_value)
    #print("encoded transitionTable")
    #print(transitionTable)
    #transitionTable = nfa_to_table(nfa)
    PopStackTable = stack_to_Table(hfa_states_label,hfa_accept_states)
    TableTojson(transitionTableKstride,PopStackTable,K)
    json_to_cli()

    #print("\nDFA Transitions:")
    #for from_state, symbol, to_state in dfa_transitions:
    #    print(f"{from_state} --{symbol}--> {to_state}")
    #print("\nNFA Transitions:")
    #for from_state, symbol, to_state in nfa_transitions:
    #    print(f"{from_state} --{symbol}--> {to_state}")
    #print("\nHFA Transitions:")
    #for from_state, symbol, to_state in hfa_transitions:
    #    print(f"{from_state} --{symbol}--> {to_state}")
    #print("\nDFA Accept States:")
    #print(dfa_accept_states)
    #print("\nNFA Accept States:")
    #print(nfa_accept_states)
