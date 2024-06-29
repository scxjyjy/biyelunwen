import copy
import pandas as pd

def root_pad_chars(entries, K):
    for entry in entries:
        chars = entry['chars']
        if len(chars) < K:
            entry['chars'] = chars.rjust(K, '*')
    return entries

def nonroot_pad_chars(entries, K):
    for entry in entries:
        chars = entry['chars']
        if len(chars) < K:
            entry['chars'] = chars.ljust(K, '*')
    return entries

def simple_increase_nonroot_table(entry,transitionTable,K):
    sub_lst_si_k = [{'State': entry.State, 'chars': entry.Symbol, 'NextState': entry.NextState,'IsEnd': entry.IsEnd}]
    StateKs = entry.State
    for k in range(1, K):
        suffix_path = []
        sub_lst_si_kp1 = []
        for entry in sub_lst_si_k:
            input_str = entry['chars']
            dst_state_str = entry['NextState']
            filtered_entries = transitionTable[transitionTable['State'] == dst_state_str]
            for entry1 in filtered_entries.itertuples(index=False):
                char = entry1.Symbol
                dst_state_str1 = entry1.NextState
                new_entry = {'State': StateKs, 'chars': input_str + char, 'NextState': dst_state_str1,'IsEnd': entry1.IsEnd}
                sub_lst_si_kp1.append(new_entry)
        if sub_lst_si_kp1:
            sub_lst_si_k = copy.deepcopy(sub_lst_si_kp1)
        print(sub_lst_si_k)
    sub_lst_si_k = nonroot_pad_chars(sub_lst_si_k, K)
    return sub_lst_si_k

def simple_increase_root_table(entry,transitionTable,K):
    sub_lst_si_k = [{'State': entry.State, 'chars': entry.Symbol, 'NextState': entry.NextState,'IsEnd': entry.IsEnd}]
    sub_lst_si_k_final = [{'State': entry.State, 'chars': entry.Symbol, 'NextState': entry.NextState,'IsEnd': entry.IsEnd}]
    print("******************************************************")
    print(sub_lst_si_k_final)
    StateKs = entry.State
    for k in range(1, K):
        suffix_path = []
        sub_lst_si_kp1 = []
        for entry in sub_lst_si_k:
            input_str = entry['chars']
            dst_state_str = entry['NextState']
            filtered_entries = transitionTable[transitionTable['State'] == dst_state_str]
            for entry1 in filtered_entries.itertuples(index=False):
                char = entry1.Symbol
                dst_state_str1 = entry1.NextState
                new_entry = {'State': StateKs, 'chars': input_str + char, 'NextState': dst_state_str1,'IsEnd': entry1.IsEnd}
                sub_lst_si_kp1.append(new_entry)
        if sub_lst_si_kp1:
            sub_lst_si_k = copy.deepcopy(sub_lst_si_kp1)
            sub_lst_si_k_final.extend(sub_lst_si_k)

    sub_lst_si_k_final = root_pad_chars(sub_lst_si_k_final, K)
    print(sub_lst_si_k_final)
    return sub_lst_si_k_final



def simple_increase_table(TransitionTable,K):
    combined_results = []
    for entry in TransitionTable.itertuples(index=False):
        #zhu yi zhei  li  shi  zi  fu
        if entry.State == '0':
            result = simple_increase_root_table(entry,TransitionTable,K)
        else:
            result = simple_increase_nonroot_table(entry,TransitionTable,K)
        combined_results.extend(result)
    df = pd.DataFrame(combined_results)
    return df

if __name__ == '__main__':
# 示例数据
    data = {
        'State': ['0', '1', '2'],
        'Symbol': ['d', 'o', 'g'],
        'NextState': [1, 2, 3],
        'IsEnd': [False, False, True]
    }

    # 创建 DataFrame
    transitionTable = pd.DataFrame(data)
    print(transitionTable)


    # 设定 K 值
    K = 2

    # 调用函数并打印结果
    result = simple_increase_table(transitionTable, K)
    print("********************************************")
    print(result)
