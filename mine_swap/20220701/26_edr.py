


import json
import time


def write_edr(EDR):
    global edr_path
    with open(edr_path) as f:
        d = json.load(f)
        f.close()

    edr_no = int(time.time() * 1_000_000)
    e_r = {str(edr_no): str(EDR)}

    # update and do not write if exists

    write_flag = False
    if str(EDR) not in d['edr'].values():
        d['edr'].update(e_r)
        write_flag = True

    with open(edr_path, 'w') as f:
        json.dump(d, f)
        f.close()
    return write_flag, edr_no



if __name__ == '__main__':
    edr_path = 'edr.json'
    write_edr('')
















