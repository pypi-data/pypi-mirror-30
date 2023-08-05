import terminaltables as tt

def table(data,table_type='ascii'):
    ''' 返回Ascii Table'''
    type_list = ['ascii','single','double','github']
    if table_type not in type_list:
        table_type = 'ascii'
    if table_type == 'ascii':
        t = tt.AsciiTable(data)
    elif table_type == 'single':
        t = tt.SingleTable(data)
    elif table_type == 'double':
        t = tt.DoubleTable(data)
    elif table_type == 'github':
        t = tt.GithubFlavoredMarkdownTable(data)
    return t.table


def main():
    data = []
    data.append([1,2,3])
    data.append([4,5,6])
    print(table(data))

if __name__ == '__main__':
    main()
