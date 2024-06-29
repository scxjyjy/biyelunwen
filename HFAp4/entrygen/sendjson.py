import json
import subprocess

def run_shell_command(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()
    return output, error

def clear_table():
    with open('testNFA-runtime.json') as file:
        config = json.load(file)
    cli_command = 'sudo -S simple_switch_CLI --thrift-port 9090'
    for entry in config['table_entries']:
        table = entry['table']
        command = f'echo  "table_clear {table}"| {cli_command}'
        output, error = run_shell_command(command)
        print(command)
    if error:
        print(f'error{error.decode("utf-8")}')

def delete_table():
    with open('testNFA-runtime.json') as file:
        config = json.load(file)
    cli_command = 'sudo -S simple_switch_CLI --thrift-port 9090'
    for entry in config['table_entries']:
        table = entry['table']
        command = f'echo  "table_delete {table}"| {cli_command}'
        output, error = run_shell_command(command)
        print(command)
    if error:
        print(f'error{error.decode("utf-8")}')

def json_to_cli():
    # 读取 JSON 文件
    with open('testNFA-runtime.json') as file:
        config = json.load(file)
    cli_command = 'sudo -S simple_switch_CLI --thrift-port 9090'

    #clear table_entry
    executed_tables = set()  # 用于跟踪已执行的表名
    for entry in config['table_entries']:
        table = entry['table']
        if table in executed_tables:
            # 如果表名已经在集合中，跳过执行命令
            continue
        command = f'echo  "table_clear {table}"| {cli_command}'
        output, error = run_shell_command(command)
        print(command)
        executed_tables.add(table)  # 将表名添加到已执行集合中
    if error:
        print(f'error{error.decode("utf-8")}')


    # 解析 JSON 文件并生成 CLI 命令
    for entry in config['table_entries']:
        table = entry['table']
        action_name = entry['action_name']
        action_params = ' '.join([f'{v}' for k, v in entry['action_params'].items()])
        priority = entry.get('priority', '')
        #zhi neng  fen  biao chuli  mei  you  tong  yon
        if 'match' in entry:
            if 't_NFA_match_0' in table:
                #match = ' '.join([f'{v[0]}&&&{v[1]}' for k, v in entry['match'].items()])
                match_parts = []
                for k, v in entry['match'].items():
                    if isinstance(v, list) and len(v) == 2:
                        match_parts.append(f'{v[0]}&&&{v[1]}')
                    else:
                        match_parts.append(str(v))  # 处理只有一个元素的情况
                match = ' '.join(match_parts)
                command = f'echo "table_add {table}  {action_name} {match} => {action_params} {priority}"| {cli_command}'
            if 't_popFirstStack' in table:
                match = ' '.join([f'{v[0]}&&&{v[1]}' for k, v in entry['match'].items()])
                command = f'echo "table_add {table}  {action_name} {match} => {action_params} {priority} "| {cli_command}'
        else:
            #f biao shi  zheng chang mingli  geshi  bingqian  keyi  jia bianliang
            #command = f'echo "table_add {table} {action_name} => {action_params} {priority}" | {cli_command} '
            command = f'echo "table_set_default {table}  {action_name} {action_params}" | {cli_command} '
        print (command)
        output, error = run_shell_command(command)

        if error:
            print(f'error{error.decode("utf-8")}')
