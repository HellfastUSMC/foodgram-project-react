import csv


def csv_gen(name, data):
    key_list = [key for key in data[0] if key != 'recipes']
    filename = f'{name}.csv'
    file = csv.writer(open(filename, 'w'))
    file.writerow(key_list)
    for record in data:
        cur_rec = []
        for key in key_list:
            if key == 'recipes':
                pass
            else:
                cur_rec.append(record[key])
        file.writerow(cur_rec)
    return file
