import random
import time
import json
import sys

env = []


def new_row(row_num):
    # rule 1
    import random

    minder = int(random.random() * row_num)
    row = [0 if x == minder else 1 for x in range(row_num)]
    return row


def new_env():
    env = []
    # firstnoneminer
    env.append([1, *new_row(row_num - 1)])
    for i in range(1, col_num):
        env.append(new_row(row_num))
    return env


def count_cheractor(env, row, col):
    character = '01234'
    k = 0
    # left
    if col > 0 and env[row][col - 1] == 0:
        k += 1
    # down
    if row < len(env) - 1 and env[row + 1][col] == 0:
        k += 1
    # right
    if col < len(env[row]) - 1 and env[row][col + 1] == 0:
        k += 1
    # up
    if row > 0 and env[row - 1][col] == 0:
        k += 1
    # return ' ' + character[k] + ' '
    return character[k]


def raw_show(show_env, name=''):
    for row in range(len(show_env)):
        for col in range(len(show_env[row])):
            print(' ' + show_env[row][col].replace(' ', '') + ' ', end='')
        print()
    # pass


def show_and_count(show_env, name='actual_world', re=False):
    for row in range(len(show_env)):
        for col in range(len(show_env[row])):
            if show_env[row][col] == 1:
                pass
            if show_env[row][col] == 0:
                pass
    actual_env = []
    for row in range(len(show_env)):
        actual_row_arr = []
        for col in range(len(show_env[row])):
            if show_env[row][col] == 1:
                actual_row_arr.append(count_cheractor(show_env, row, col))
            if show_env[row][col] == 0:
                actual_row_arr.append('*')
            if show_env[row][col] == '?':
                actual_row_arr.append('?')
        actual_env.append(actual_row_arr)
    if re:
        return actual_env


def init_player_ob():
    plob = [['?' for x in y] for y in actual_env]
    plob[0][0] = actual_env[0][0]
    return plob


def init_value(plob):
    # select value
    plob_ima = [[y + str(1) if y.startswith('?') else y for y in x] for x in plob]
    return plob_ima


def value2rate(plob_ima, re_sim_dict_flag=False):
    global col_num
    if not re_sim_dict_flag:
        re_sim_dict = {(x, y): plob_ima[x][y] for x in range(len(plob_ima)) for y in range(len(plob_ima[x]))}
    else:
        re_sim_dict = plob_ima
    sum_value = sum([float(x[1:]) for x in re_sim_dict.values() if x.startswith('?')])

    mine_count = col_num - sum([1 for v in re_sim_dict.values() if v == '*'])
    # re_rate_dict = dict(
    #     (k, '#' + str(float(v[1:]) / sum_value * mine_count)) if v.startswith('?') else (k, v) for k, v in
    #     re_sim_dict.items())

    unknow_num = sum([1 for x in re_sim_dict.values() if x.startswith('?')])

    re_rate_dict = dict((k, '#' + str(float(1 / unknow_num * mine_count))) if sum_value * mine_count == 0 else (
        k, '#' + str(float(v[1:]) / sum_value * mine_count)) if v.startswith('?') else (k, v) for k, v in
                        re_sim_dict.items())

    re_rate_select = dict((k, '#' + str(float(1 / unknow_num))) if sum_value == 0 else
                          (k, '#' + str(float(v[1:]) / sum_value)) if v.startswith('?') else (k, v) for k, v in
                          re_sim_dict.items())
    re_rate_select = dict(
        (k, '#10000000000') if v == '#0.0' else (k, '#' + str(1 / float(v[1:]))) if v[0] == '#' else (k, v) for (k, v)
        in re_rate_select.items())

    return re_rate_dict, re_rate_select


def select_rate(re_rate_dict):
    import random
    ra = random.random()
    for k, v in re_rate_dict.items():
        if v.startswith('#'):
            ra -= float(v[1:])
        if ra <= 0:
            return k
    return k


def record2memo(memo_path, actual_env, env_time_stamp, plob, knowledge_no, suspect_no, re_rate_dict, action,
                beneficial):
    content = [{"plob": plob,
                "knowledge": knowledge_no,
                "suspect_current": suspect_no,
                "re_rate_dict": {str(k): v for k, v in re_rate_dict.items()},
                "action": str(action),
                "beneficial": beneficial}]

    all_content = {"actual_env": actual_env,
                   "env_time_stamp": env_time_stamp,

                   "content": content}
    try:
        with open(memo_path) as f:
            d = json.load(f)
            flag = True
            for record in d['record']:
                print(record)
                if record['actual_env'] == actual_env and record['env_time_stamp'] == env_time_stamp:
                    record['content'].extend(content)
                    flag = False
                    break
            if flag:
                d['record'].append(all_content)
            print(d)
    except:
        d = {
            "record": [
            ]
        }
        d['record'].append(all_content)
    with open(memo_path, 'w') as f:
        json.dump(d, f)


def sim_till_end(plob, record_flag=False, conjecture=False):
    # raw_show(plob, name='before_select plob')
    global total_reward
    global env_time_stamp
    global knowledge_no
    global suspect_no
    global memo_path
    global knowledge_time

    # a, b = strategy(plob)

    plob_ima = init_value(plob)

    if conjecture:
        re_sim_dict = value_by_conjecture(plob, knowledge_time)
        re_rate_dict, re_rate_select = value2rate(re_sim_dict, re_sim_dict_flag=True)
        a, b = action = select_rate(re_rate_dict)


    else:
        re_rate_dict, re_rate_select = value2rate(plob_ima)
        a, b = action = select_rate(re_rate_dict)

    # raw_show(actual_env)
    plob[a][b] = actual_env[a][b]
    # raw_show(plob, name='after_select plob')

    beneficial = 0

    continue_flag = True

    if actual_env[a][b] == '*':
        continue_flag = False
        # print('game  over  ...  ')
        # raw_show(actual_env, 'actual_env')
        beneficial = failure_reward
        total_reward += beneficial
        pass
    elif sum([str(x).count('?') for y in plob for x in y]) == len(plob[0]):
        continue_flag = False
        # print('game  successed  ...  ')
        beneficial = success_reward
        total_reward += beneficial

    if record_flag:
        record2memo(memo_path, actual_env, env_time_stamp, plob, knowledge_no, suspect_no, re_rate_dict, action,
                    beneficial)

    if continue_flag:
        sim_till_end(plob, record_flag, conjecture)


# get_newest_knowledge
def get_n_k():
    with open('knowledge.json') as f:
        d = json.load(f)
    try:
        return max([int(x) for x in list(d['knowledge'].keys())])
    except:
        return ''


# get_newest_suspect
def get_n_s():
    with open('suspect.json') as f:
        d = json.load(f)
    try:
        return max([int(x) for x in list(d['suspect'].keys())])
    except:
        return ''


'''
清空记忆
'''


def frush_obj(file_name):
    with open(file_name, 'w', encoding='utf-8') as f:
        f.write('')
        f.close()


import random


def read_theme(memo_path, num):
    focus_plob = []
    with open(memo_path) as f:
        d = json.load(f)
    for record in d['record']:
        for content in record['content']:
            if content['beneficial'] < 0:
                focus_plob.append(content['plob'])
    focus_plob = [focus_plob[int(random.random() * len(focus_plob))] for x in range(num)]
    return focus_plob


def read_theme(memo_path, num):
    focus_plob = []

    with open(memo_path) as f:
        d = json.load(f)

    for record in d['record']:
        for content in record['content']:
            if content['beneficial'] < 0:
                focus_plob.append(content)
    focus_content = [focus_plob[int(random.random() * len(focus_plob))] for x in range(num)]
    return focus_content


def re_shuffle2col(plob):
    re_plob = [[plob[y][x] for y in range(len(plob))] for x in range(len(plob[0]))]
    return re_plob


def re_shuffle2row(re_plob):
    actual_env = [[re_plob[y][x] for y in range(len(re_plob))] for x in range(len(re_plob[0]))]
    return actual_env


'''bayes sim is based on current view , sim one possible current situation randomly with MC methods'''


def fill_mine(re_plob):
    import random, copy

    re_sim_env = []
    for col in re_plob:
        if '*' in col:
            temp_row = copy.deepcopy(col)
            re_sim_env.append(temp_row)
            continue
        ob_dict = {(x, y): col[x][y] for x in range(len(col)) for y in range(len(col[x]))}
        all_select_possible = {k: v for k, v in ob_dict.items() if v == '?'}
        # rs = random.choice(list(all_select_possible))
        a, b = random.choice(list(all_select_possible))
        temp_row = copy.deepcopy(col)
        temp_row[a] = '*'
        re_sim_env.append(temp_row)
    return re_sim_env


def re2dict(re_sim_env):
    ob_dict = {(x, y): re_sim_env[x][y] for x in range(len(re_sim_env)) for y in range(len(re_sim_env[x]))}
    return ob_dict


def check_cop_re(re_sim_env):
    re_sim_env = [[y.replace(' ', '') for y in x] for x in re_sim_env]
    # print(re_sim_env)
    re_sim_dict = re2dict(re_sim_env)
    # print(re_sim_dict)
    all_num_position = {k: v for k, v in re_sim_dict.items() if v in '01234'}
    # print(all_num_position)
    for k, v in all_num_position.items():
        a, b = k
        print(a, b)
        # check if mine in left/down/right/up
        mine_num = 0
        mine_num += 1 if (a, b - 1) in re_sim_dict and re_sim_dict[(a, b - 1)] == '*' else 0
        mine_num += 1 if (a - 1, b) in re_sim_dict and re_sim_dict[(a - 1, b)] == '*' else 0
        mine_num += 1 if (a, b + 1) in re_sim_dict and re_sim_dict[(a, b + 1)] == '*' else 0
        mine_num += 1 if (a + 1, b) in re_sim_dict and re_sim_dict[(a + 1, b)] == '*' else 0
    if int(v) != mine_num:
        return False
    return True


def dict2arr(re_sim_dict):
    arr = []
    row = []
    temp_row_num = 0
    for k, v in re_sim_dict.items():
        a, b = k

        if temp_row_num != a:
            arr.append(row)
            temp_row_num = a
            row = []
        row.append(v)
    arr.append(row)
    return arr


def fill_mum(re_sim_env):
    # print(re_sim_env)
    re_sim_dict = {(x, y): re_sim_env[x][y] for x in range(len(re_sim_env)) for y in range(len(re_sim_env[x]))}
    all_select_possible = {k: v for k, v in re_sim_dict.items() if v == '?'}

    print(re_sim_dict)
    # print(all_select_possible)

    for k, v in all_select_possible.items():
        a, b = k
        # check if mine in left/down/right/up
        mine_num = 0
        mine_num += 1 if (a, b - 1) in re_sim_dict and re_sim_dict[(a, b - 1)] == '*' else 0
        mine_num += 1 if (a - 1, b) in re_sim_dict and re_sim_dict[(a - 1, b)] == '*' else 0
        mine_num += 1 if (a, b + 1) in re_sim_dict and re_sim_dict[(a, b + 1)] == '*' else 0
        mine_num += 1 if (a + 1, b) in re_sim_dict and re_sim_dict[(a + 1, b)] == '*' else 0
        re_sim_dict[a, b] = str(mine_num)
    re_sim_env = dict2arr(re_sim_dict)
    return re_sim_env


def bayes_sim(re_plob):
    '''
    rules_check
    1. only one mine on each line
    2. corporate with the showing num
    then count another num
    '''
    re_sim_env = fill_mine(re_plob)
    while not check_cop_re(re_sim_env):
        re_sim_env = fill_mine(re_plob)
    print(re_sim_env)
    re_sim_env = fill_mum(re_sim_env)
    return re_sim_env


def bayes_mine_value(plob, epoch):
    re_plob = re_shuffle2col(plob)
    re_bayes_ima = [['$' if y.startswith('?') else y for y in x] for x in re_plob]
    for i in range(epoch):
        re_sim_env = bayes_sim(re_plob)
        print(re_sim_env)
        # re_sim_env = [[' 2 ', '*'], ['*', '2']]
        # bayes_ima = [[1 if plob[x][y] == '?' else 0 for y in range(len(plob[x]))] for x in range(len(plob))]
        re_bayes_ima = [
            [re_bayes_ima[x][y] + re_sim_env[x][y] if re_bayes_ima[x][y][0] == '$' else re_bayes_ima[x][y] for y in
             range(len(re_bayes_ima[x]))] for x in range(len(re_bayes_ima))]
    return re_bayes_ima


def bayes_mine_rate(bayes_ima):
    bayes_rate = [
        ['@' + str(sum([1 if x.isnumeric() else 0 for x in y[1:]]) / int(len(y[1:]))) if y.startswith('$') else y for y
         in x] for x in bayes_ima]
    return bayes_rate


def bayes_rate2re_rate(bayes_rate):
    bayes_rate_dict = {(x, y): bayes_rate[x][y] for x in range(len(bayes_rate)) for y in range(len(bayes_rate[x]))}
    return bayes_rate_dict


def re_bayes_rate2re_rate(re_bayes_rate):
    bayes_rate_dict = {(y, x): re_bayes_rate[x][y] for x in range(len(re_bayes_rate)) for y in
                       range(len(re_bayes_rate[x]))}
    return bayes_rate_dict


def bffo(fo, action):
    return [['?' if (x, y) == eval(action) else fo[x][y] for y in range(len(fo[0]))] for x in range(len(fo))]


def diff2value(bayes_rate_dict, re_rate_dict):
    diff_minus_dict = dict(
        (k, abs(float(v[1:]) - float(re_rate_dict[str(k)][1:]))) if v.startswith('@') else (k, v) for k, v in
        bayes_rate_dict.items())
    diff_value = sum([x if type(x) == float else 0 for x in diff_minus_dict.values()]) / len(diff_minus_dict)
    diff_tuple = (bayes_rate_dict, re_rate_dict)
    return diff_tuple, diff_minus_dict, diff_value


####################################18########################################
def init_suspect(path):
    d = {
        "suspect": {}
    }
    with open(path, 'w') as f:
        json.dump(d, f)


def init_knowledge(path):
    d = {
        "knowledge": {}
    }
    with open(path, 'w') as f:
        json.dump(d, f)


def init_memo(path):
    d = {
        "record": [
        ]
    }
    with open(path, 'w') as f:
        json.dump(d, f)


def init_edr(path):
    d = {
        "edr": {}
    }
    with open(path, 'w') as f:
        json.dump(d, f)


def init_edr_value(path):
    d = {
        "edr_value": {}
    }
    with open(path, 'w') as f:
        json.dump(d, f)


#####################15_2#####################

def compare_direct(a, b):
    # priori knowledge
    y_axis = int(a[0]) - int(b[0])
    x_axis = a[1] - a[1]
    relation = ''
    direction = 'd' if y_axis < 0 else 'u'
    relation += ''.join([direction for x in range(y_axis)])
    direction = 'r' if x_axis < 0 else 'l'
    relation += ''.join([direction for x in range(x_axis)])
    return relation


#####################15_3#####################
def compare_direct(a, b, bayes_rate_dict):
    # priori knowledge
    priori_dict = {'r': 1, 'd': 1, 'l': -1, 'u': -1}
    axis_dict = {'y_axis': 'du', 'x_axis': 'rl'}
    op_priori = {('r', 'op'): {'l'}, ('l', 'op'): {'r'}, ('d', 'op'): {'u'}, ('u', 'op'): {'d'}}

    y_axis = int(a[0]) - int(b[0])
    x_axis = int(a[1]) - int(b[1])

    relation = ''
    direction = 'd' if y_axis < 0 else 'u'
    relation += ''.join([direction for x in range(abs(y_axis))])
    direction = 'r' if x_axis < 0 else 'l'
    relation += ''.join([direction for x in range(abs(x_axis))])

    a_n = bayes_rate_dict[a]
    b_n = bayes_rate_dict[b]
    return a_n, relation, b_n


######################19#######################
def write_edr(EDR):
    global edr_path
    with open(edr_path) as f:
        d = json.load(f)
        f.close()

    edr_no = int(time.time()*1_000_000)
    e_r = {str(edr_no): str(EDR)}
    d['edr'].update(e_r)

    with open(edr_path, 'w') as f:
        json.dump(d, f)
        f.close()
    return edr_no


############################17###############################
def po_plus_dire(position, direction):
    global col_num
    global row_num

    for d in direction:
        if d == 'd':
            position = (position[0] + 1, position[1])
        if d == 'u':
            position = (position[0] - 1, position[1])
        if d == 'r':
            position = (position[0], position[1] + 1)
        if d == 'l':
            position = (position[0], position[1] - 1)

    print(position)
    if position[0] in range(row_num) and position[1] in range(col_num):
        return position
    else:
        return


def edr_value(re_sim_dict, position, mine_rate):
    re_sim_dict[position] = '?' + str(1 - float(mine_rate))
    return re_sim_dict


def read_edr():
    global edr_path
    with open(edr_path) as f:
        d_edr = json.load(f)['edr']
    return d_edr


def read_knowledge():
    global knowledge_path
    with open(knowledge_path) as f:
        d_knowledge = json.load(f)['knowledge']
    return d_knowledge


def get_all_last_plob():
    global memo_path
    with open(memo_path) as f:
        d = json.load(f)
    all_last_plob = [x['content'][-1]['plob'] for x in d['record']]
    return all_last_plob


def evaluate_edr_by_memo(edr_no, all_last_plob):
    d_edr = read_edr()
    print(d_edr)

    d_knowledge = read_knowledge()
    print(d_knowledge)

    edr = eval(d_edr[str(edr_no)])

    key_num = list(list(edr.values())[0].keys())[0][0]
    direction = list(list(edr.values())[0].keys())[0][1]
    mine_rate = list(list(edr.values())[0].values())[0][1]

    loaded = 0
    observed = 0
    correct = 0

    for plob in all_last_plob:

        plob_ima = [[y + str(1) if y.startswith('?') else y for y in x] for x in plob]
        re_sim_dict = {(x, y): plob_ima[x][y] for x in range(len(plob_ima)) for y in range(len(plob_ima[x]))}

        arr = [k for k, v in re_sim_dict.items() if v == key_num]

        loaded += 1
        for position in arr:
            position = po_plus_dire(position, direction)
            if position and re_sim_dict[position][0] != '?':
                observed += 1
                if re_sim_dict[position] == '*':
                    correct += 1
                if re_sim_dict[position][0] in '012345678':
                    correct += 0

                re_sim_dict = edr_value(re_sim_dict, position, mine_rate)
                print(re_sim_dict)
    return {'edr_no': edr_no, 'loaded': loaded, 'observed': observed, 'correct': correct}


def update_edr_value(edr_ob):
    global edr_value_path

    with open(edr_value_path) as f:
        d = json.load(f)
        f.close()

    for ob_e in edr_ob:
        # print(ob_e)
        # {'edr_no': 1651999879035613400, 'loaded': 10, 'observed': 10, 'correct': 10}
        # {'edr_no': 1651999879035613400, 'loaded': 10, 'observed': 10, 'correct': 10}
        if str(ob_e['edr_no']) not in d['edr_value'].keys():
            new_edr_ob = {'edr_no': ob_e['edr_no'], 'loaded': ob_e['loaded'], 'observed': ob_e['observed'],
                          'correct': ob_e['correct'], 'correct_rate': 0}
        else:
            new_edr_ob = d['edr_value'][str(ob_e['edr_no'])]
            new_edr_ob = eval(new_edr_ob)
            new_edr_ob['loaded'] += ob_e['loaded']
            new_edr_ob['observed'] += ob_e['observed']
            new_edr_ob['correct'] += ob_e['correct']
        try:
            new_edr_ob['correct_rate'] = new_edr_ob['correct'] / new_edr_ob['observed']
        except:
            new_edr_ob['correct_rate'] = 0.0
        d['edr_value'][str(ob_e['edr_no'])] = str(new_edr_ob)

    with open(edr_value_path, 'w') as f:
        json.dump(d, f)
        f.close()
    return


###########################24############################
def read_edr_value():
    global edr_value_path
    with open(edr_value_path) as f:
        d_edr_value = json.load(f)['edr_value']
    return d_edr_value


def write_knowledge(edr_no_ls):
    global knowledge_path
    global knowledge_time

    with open(knowledge_path) as f:
        d = json.load(f)

    k_r = {str(knowledge_time): edr_no_ls}
    print(k_r)
    d['knowledge'].update(k_r)
    with open(knowledge_path, 'w') as f:
        json.dump(d, f)
    return


def get_last_knowledge():
    global knowledge_path

    with open(knowledge_path) as f:
        d = json.load(f)
    return list(d['knowledge'].keys())[-1]


def value_by_conjecture(plob, knowledge_time):
    global knowledge_path
    global edr_path
    # select value

    d_edr = read_edr()
    print(d_edr)

    d_knowledge = read_knowledge()
    print(d_knowledge)

    plob_ima = [[y + str(1) if y.startswith('?') else y for y in x] for x in plob]
    print(plob_ima)
    re_sim_dict = {(x, y): plob_ima[x][y] for x in range(len(plob_ima)) for y in range(len(plob_ima[x]))}
    print(re_sim_dict)

    for edr_no in d_knowledge[str(knowledge_time)]:
        print(edr_no)
        print(type(d_edr))
        print(type(edr_no))
        edr = eval(d_edr[str(edr_no)])
        print(edr)
        print(type(edr))
        # {(('2', ''), '2'): {('2', 'l'): ('*', 1.0)}}
        key_num = list(list(edr.values())[0].keys())[0][0]
        direction = list(list(edr.values())[0].keys())[0][1]
        mine_rate = list(list(edr.values())[0].values())[0][1]

        arr = [k for k, v in re_sim_dict.items() if v == key_num]
        print(arr)
        for position in arr:
            position = po_plus_dire(position, direction)
            if position:
                re_sim_dict = edr_value(re_sim_dict, position, mine_rate)
                print(re_sim_dict)
    return re_sim_dict





if __name__ == '__main__':
    sys.setrecursionlimit(10000)

    col_num = 2
    row_num = 3
    total_reward = 0
    success_reward = 0
    failure_reward = -1
    memo_path = 'memo.json'
    suspect_path = 'suspect.json'
    knowledge_path = 'knowledge.json'
    edr_path = 'edr.json'
    edr_value_path = 'edr_value.json'

    read_theme_num = 50

    # is rerun flag
    is_escape_memo = False
    is_escape_memo = True

    is_escape_knowledge = False
    is_escape_knowledge = True

    if is_escape_memo:
        episode = 0
    else:
        episode = 1000
        init_memo(memo_path)
        init_knowledge(knowledge_path)
        init_suspect(suspect_path)
        init_edr(edr_path)
        init_edr_value(edr_value_path)

        frush_obj(memo_path)

    knowledge_no = get_n_k()
    suspect_no = get_n_s()

    for i in range(episode):
        # print('=-----------------'+str(i)+'  episode=-----------------')
        env = new_env()
        raw_env = list(map(list, zip(*env)))
        actual_env = show_and_count(raw_env, re=True, name='raw_env')
        env_time_stamp = int(time.time()*1_000_000)

        plob = init_player_ob()
        #  print(plob)
        #  print(actual_env)
        #  show(plob,  name='plob'
        #  print(actual_env)
        #  raw_show(plob, name='plob')

        sim_till_end(plob, record_flag=True)
    print(total_reward)
    try:
        rate_reward = total_reward / episode
        print(rate_reward)
    except:
        pass

    '''give suspect based on memory, focus on the failure benefit'''

    if is_escape_knowledge:
        knowledge_time = get_last_knowledge()
    else:
        knowledge_time = int(time.time()*1_000_000)

        init_knowledge(knowledge_path)
        init_suspect(suspect_path)
        init_edr(edr_path)
        init_edr_value(edr_value_path)

        all_last_plob = get_all_last_plob()

        focus_content = read_theme(memo_path, read_theme_num)

        print(focus_content)
        print(type(focus_content))
        print(focus_content[1])
        print(type(focus_content[1]))
        diff_content_ls = []
        for fc in focus_content:
            print(fc)
            fo = fc['plob']
            print(fo)
            print(fc['action'])
            # [[' 1 ', '?'], [' 1 ', '?'], ['*', '?']]
            # (2, 0)
            bf_fo = bffo(fo, fc['action'])
            print(bf_fo)
            # [[' 1 ', '?'], [' 1 ', '?'], ['?', '?']]
            plob_ima = init_value(bf_fo)
            print(plob_ima)
            # [[' 1 ', '?0.1'], [' 1 ', '?0.1'], ['?0.1', '?0.1']]
            re_bayes_ima = bayes_mine_value(fo, 1000)
            print(re_bayes_ima)
            # [[' 1 ', ' 1 ', '*'], ['$*****','$1111111','$1111']]
            re_bayes_rate = bayes_mine_rate(re_bayes_ima)
            print(re_bayes_rate)
            # [[' 1 ', ' 1 ', '*'], ['@0.0', '@1.0', '@1.0']]
            bayes_rate_dict = re_bayes_rate2re_rate(re_bayes_rate)
            print(bayes_rate_dict)
            # {(0, 0): ' 1 ', (0, 1): ' 1 ', (0, 2): '*', (1, 0): '@0.0', (1, 1): '@1.0', (1, 2): '@1.0'}
            re_rate_dict = fc['re_rate_dict']
            print(re_rate_dict)
            # {'(0, 0)': ' 1 ', '(0, 1)': '#0.25', '(1, 0)': ' 1 ', '(1, 1)': '#0.25', '(2, 0)': '#0.25', '(2, 1)': '#0.25'}

            diff_tuple, diff_minus_dict, diff_value = diff2value(bayes_rate_dict, re_rate_dict)
            print(diff_tuple)
            print(diff_value)
            # ({(0, 0): ' 1 ', (1, 0): '*', (2, 0): '@1.0', (0, 1): ' 0 ', (1, 1): '@1.0', (2, 1): '@0.0'},
            #  {'(0, 0)': ' 1 ', '(0, 1)': ' 0 ', '(1, 0)': '#0.25', '(1, 1)': '#0.25', '(2, 0)': '#0.25', '(2, 1)': '#0.25'})
            # 0.2916666666666667
            diff_content = {str(diff_tuple): diff_value}
            print(diff_content)
            diff_content_ls.append(diff_content)
            fc['bayes_rate_dict'] = bayes_rate_dict
            fc['diff_value'] = diff_value
            fc['diff_minus_dict'] = diff_minus_dict
            print(fc)
        print(focus_content)
        sorted_fo_content = sorted(focus_content, key=lambda d: -d['diff_value'])
        print(sorted_fo_content)

        for con in sorted_fo_content:
            print(con)
            diff_minus_dict = con['diff_minus_dict']
            bayes_rate_dict = con['bayes_rate_dict']
            re_rate_dict = con['re_rate_dict']
            # print(diff_minus_dict)
            # print(bayes_rate_dict)
            # print(re_rate_dict)
            # {(0, 0): '2', (1, 0): '*', (2, 0): 0.6, (0, 1): 0.4, (1, 1): 0.6, (2, 1): 0.6}
            # {(0, 0): '2', (1, 0): '*', (2, 0): '@1.0', (0, 1): '@0.0', (1, 1): '@1.0', (2, 1): '@1.0'}
            # {'(0, 0)': ' 2 ', '(0, 1)': '#0.4', '(1, 0)': '#0.4', '(1, 1)': '#0.4', '(2, 0)': '#0.4', '(2, 1)': '#0.4'}
            avg = sum([x if type(x) != str else 0 for x in diff_minus_dict.values()]) / len(
                [v for v in diff_minus_dict.values() if type(v) != str])
            print(avg)
            # 0.55

            mine_forcast_grid = [k for k, v in diff_minus_dict.items() if
                                 type(v) != str and diff_minus_dict[k] != 0 and bayes_rate_dict[k][1:] == '0.0']
            print(mine_forcast_grid)
            # [(0, 1)]

            num_grid = [k for k, v in diff_minus_dict.items() if type(v) == str and v.isnumeric()]
            print(num_grid)
            # [(0, 0), (1, 0)]

            # 计算1跳的关系
            # count relation in one direct
            for a in num_grid:
                for b in mine_forcast_grid:
                    a_n, relation, b_n = compare_direct(a, b, bayes_rate_dict)
                    EDR = {(((a_n, '*'), a_n)): {(a_n, relation): ('*', 1.0)}}
                    print(EDR)
                    edr_no = write_edr(EDR)
                    ob_e = evaluate_edr_by_memo(edr_no, all_last_plob)
                    update_edr_value([ob_e])


        '''add correct conjecture to knowledge'''
        d_edr_value = read_edr_value()

        print(d_edr_value.values())
        print(list(d_edr_value.values()))
        edr_no_ls = [k for k, v in d_edr_value.items() if int(eval(v)['correct_rate']) == 1]
        print(edr_no_ls)
        write_knowledge(edr_no_ls)

    '''load knowledge change action'''

    episode = 1000
    total_reward = 0
    # knowledge_time = '11111'

    for i in range(episode):
        # print('=-----------------'+str(i)+'  episode=-----------------')
        env = new_env()
        raw_env = list(map(list, zip(*env)))
        actual_env = show_and_count(raw_env, re=True, name='raw_env')
        env_time_stamp = int(time.time()*1_000_000)

        plob = init_player_ob()
        #  print(plob)
        #  print(actual_env)
        #  show(plob,  name='plob'
        #  print(actual_env)
        #  raw_show(plob, name='plob')

        sim_till_end(plob, conjecture=True)
    print(total_reward)
    try:
        rate_reward = total_reward / episode
        print(rate_reward)
    except:
        pass




