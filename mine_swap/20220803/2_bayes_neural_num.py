


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


def re_shuffle2col(plob):
    re_plob = [[plob[y][x] for y in range(len(plob))] for x in range(len(plob[0]))]
    return re_plob


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
        # print(a, b)
        # check if mine in left/down/right/up
        mine_num = 0
        mine_num += 1 if (a, b - 1) in re_sim_dict and re_sim_dict[(a, b - 1)] == '*' else 0
        mine_num += 1 if (a - 1, b) in re_sim_dict and re_sim_dict[(a - 1, b)] == '*' else 0
        mine_num += 1 if (a, b + 1) in re_sim_dict and re_sim_dict[(a, b + 1)] == '*' else 0
        mine_num += 1 if (a + 1, b) in re_sim_dict and re_sim_dict[(a + 1, b)] == '*' else 0
    if int(v) != mine_num:
        return False
    return True


if __name__ == '__main__':

    plob = [["0", "?"], ["?", "?"], ["?", "?"]]
    plob = [["1", "?"], ["?", "?"], ["?", "?"]]
    plob = [["2", "?"], ["?", "?"], ["?", "?"]]

    re_plob = re_shuffle2col(plob)

    re_sim_env = fill_mine(re_plob)
    print(re_sim_env)

    re_sim_env = fill_mum(re_sim_env)
    print(re_sim_env)


    binary_result = check_cop_re(re_sim_env)

    print(binary_result)


























