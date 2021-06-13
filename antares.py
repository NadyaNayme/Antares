# -*- coding: utf-8 -*-

# This code is a terrible example of both Python and Programming.
# It isn't meant to be pretty, it isn't meant to be maintainable.
# It is only meant to get the job done. Some of the code exists as
# dead code from a failed experiment to get the program to run
# as an .exe instead of .py
# The program still works with the superfluous code so it
# was never changed back

# Beware all ye who ignored this warning and chose to read on

import re
import os

script_dir = os.path.dirname(__file__)
input_file = os.path.join(script_dir, '__INPUT.txt')
output_file = os.path.join(script_dir, '__OUTPUT.txt')

parsed_sql = []

select_columns = []
top_value = 1  # Default to 1
db = {'from': '', 'alias': ''}
join = []
apply = []
where = []
orderby = ""


def match_dict(val):
    return {
        '=': 'EQUALS',
        '<>': '{NE}',
        '​STARTSWITH': '​STARTSWITH',
        '​ENDSWITH': '​ENDSWITH',
        '​LIKE': '​LIKE',
        '​NOTEQUAL': '​NOTEQUAL',
        '​NOTSTARTSWITH': '​NOTSTARTSWITH',
        'NOTENDSWITH': 'NOTENDSWITH',
        'NOTLIKE​': 'NOTLIKE​',
        '​GREATER': '​GREATER',
        '​LESSER': '​LESSER',
        '​GREATEROREQUAL': '​GREATEROREQUAL',
        '​LESSEROREQUAL': '​LESSEROREQUAL',
        '​BETWEEN': '​BETWEEN',
        '​IN': '​IN',
        '​NOTIN': '​NOTIN',
        '​LISTHAS': '​LISTHAS',
        '​CASESENSITIVE': '​CASESENSITIVE',
        '​FULLTEXT': '​FULLTEXT',
        '​CONTAINS': '​CONTAINS',
        '​DURINGDAYOF': '​DURINGDAYOF',
        '​DURINGMONTHOF': '​DURINGMONTHOF',
        '​DURINGYEAROF': '​DURINGYEAROF',
        '​ISNULL': '​ISNULL',
        '​NOTNULL': '​NOTNULL',
        '​LIKEPHONE': '​LIKEPHONE',
        '​LIKEEACH': '​LIKEEACH',
        '​LIKEANY': '​LIKEANY'
    }.get(val, 'EQUALS')


with open(input_file, 'r') as in_file:
    all_lines = in_file.readlines()
    for line in all_lines:
        line = line.rstrip()
        line = line.split()
        parsed_sql.append(line)

# All of these _indices and _clauses could probably be refactored enumerating a dict to check for the clauses and appending to the proper list
join_clauses = []
apply_clauses = []
where_clauses = []
orderby_clauses = []
for index in parsed_sql:
    join_indices = [n for n, clause in enumerate(index) if clause == 'JOIN']
    join_clauses.append(join_indices)
    apply_indices = [n for n, clause in enumerate(index) if clause == 'APPLY']
    apply_clauses.append(apply_indices)
    where_indices = [n for n, clause in enumerate(
        index) if clause == 'WHERE' or clause == 'AND']
    where_clauses.append(where_indices)
    orderby_indices = [n for n, clause in enumerate(
        index) if clause == 'ORDER']
    orderby_clauses.append(orderby_indices)

# Parse the SELECT statement skipping to the fourth index if TOP exists. The third index is always the top_value
# And all values past top_value are columns
if parsed_sql[0].__len__() > 3:
    select_columns.append(' '.join(map(str, parsed_sql[0][3:])))
    top_value = parsed_sql[0][2]
else:
    select_columns.append(' '.join(map(str, parsed_sql[0][1:])))

# Parse the FROM statement where the grammar is FROM db AS alias
if parsed_sql[1].__len__() > 1:
    new_db = {'from': parsed_sql[1][1], 'alias': parsed_sql[1][-1]}
    db.update(new_db)
else:
    new_db = {'from': parsed_sql[1][1], 'alias': None}
    db.update(new_db)

# Parse JOIN where the first index is the type, the third index is the database, the fifth index is an alias if it exists
# Otherwise the fifth index is ID1 and the seventh index is ID2
check_join_clauses = [i for i, val in enumerate(
    join_clauses) if val != [] and val == [0] or val == [1] or val == [2]]
for indice in check_join_clauses:
    if parsed_sql[indice].__len__() == 10:
        new_join = {'type': ' '.join(map(str, parsed_sql[indice][0:2])), 'db': parsed_sql[indice][3],
                    'alias': parsed_sql[indice][5], 'id1': parsed_sql[indice][7], 'id2': parsed_sql[indice][9]}
        join.append(new_join)
    elif parsed_sql[indice].__len__() == 9:
        new_join = {'type': parsed_sql[indice][0], 'db': parsed_sql[indice][2],
                    'alias': parsed_sql[indice][4], 'id1': parsed_sql[indice][6], 'id2': parsed_sql[indice][8]}
        join.append(new_join)
    else:
        new_join = {'type': parsed_sql[indice][0], 'db': parsed_sql[indice][2],
                    'alias': None, 'id1': parsed_sql[indice][4], 'id2': parsed_sql[indice][6]}
        join.append(new_join)

# Parse APPLY where the first index is the type, the third index is the database, the fifth index is an alias if it exists and the sixth index is the sql
# Otherwise the fifth index is sql
check_apply_clauses = [i for i, val in enumerate(
    apply_clauses) if val != [] and val == [0] or val == [1]]
for indice in check_apply_clauses:
    if parsed_sql[indice].__len__() > 7:
        new_apply = {'type': parsed_sql[indice][0], 'db': parsed_sql[indice][-1:-2],
                     'alias': parsed_sql[indice][-1], 'sql': ' '.join(map(str, parsed_sql[indice][2:-2]))}
        apply.append(new_apply)
    else:
        new_apply = {'type': parsed_sql[indice][0], 'db': parsed_sql[indice][2],
                     'alias': None, 'sql': ' '.join(map(str, parsed_sql[indice][4:-1]))}
        apply.append(new_apply)

# Parse simple WHERE and AND clauses. Name is second index, match_type is third, and the value to match is fourth.
check_where_clauses = [i for i, val in enumerate(
    where_clauses) if val != [] and val == [0]]
for indice in check_where_clauses:
    if parsed_sql[indice][2] != "IS" and parsed_sql[indice][2] != "IN":
        new_where = {'name': parsed_sql[indice][1], 'match_type': match_dict(
            parsed_sql[indice][2]), 'value': parsed_sql[indice][3]}
        where.append(new_where)
    elif parsed_sql[indice][2] == "IS" and parsed_sql[indice][3] == "NOT" and parsed_sql[indice][4] == "NULL":
        new_where = {'name': parsed_sql[indice][1],
                     'match_type': "IS NOT", 'value': "NULL"}
        where.append(new_where)
    elif parsed_sql[indice][2] == "IS" and parsed_sql[indice][3] == "NULL":
        new_where = {'name': parsed_sql[indice]
                     [1], 'match_type': "IS", 'value': "NULL"}
        where.append(new_where)
    elif parsed_sql[indice][2] == "IN":
        new_where = {'name': parsed_sql[indice][1], 'match_type': "IN", 'value': ' '.join(
            map(str, parsed_sql[indice][3:]))}
        where.append(new_where)
    else:
        print("Failure to parse WHERE clause correctly")

# Parse ORDER BY clause. Grab all indices after the second ("BY")
check_orderby_clauses = [
    i for i, val in enumerate(orderby_clauses) if val != []]
for indice in check_orderby_clauses:
    if parsed_sql[indice].__len__() > 0:
        orderby = parsed_sql[indice][2:]

# The if statements are to be sure the variable has been set - otherwise an error would prevent the program from working. Better to skip than crash.
if select_columns:
    select_line = 'select: \'{fields}\','.format(
        fields=' '.join(map(str, select_columns)))
if top_value:
    top_line = 'top: {tvalue}'.format(tvalue=top_value)
if db['from'] and db['alias']:
    from_line = 'from: \'{database}\',\n\talias: \'{alias}\','.format(
        database=db['from'], alias=db['alias'])
elif db['from']:
    from_line = 'from: \'{database}\','.format(database=db['from'])

# Hacky way of joining all the clauses together. Python's string interpolation sucks compared to Javascript
# All of the _lines lists should be refactored to be generated by a function but for now we'll just loop over each item seperately
join_lines = []
if join.__len__() > 0:
    for item in join:
        join_type = item['type']
        join_from = item['db']
        join_alias = item['alias']
        join_id1 = item['id1']
        join_id2 = item['id2']
        join_on = '[{{ id1: \'{jid1}\', id2: \'{jid2}\' }}]'.format(
            jid1=join_id1, jid2=join_id2)
        join_lines.append('  {{\n\t\ttype: \'{jtype}\',\n\t\tto: \'{jfrom}\',\n\t\talias: \'{jalias}\',\n\t\ton: {jon}\n\t  }}'.format(
            jtype=join_type, jfrom=join_from, jalias=join_alias, jon=join_on))

apply_lines = []
if apply.__len__() > 0:
    for item in apply:
        apply_type = item['type']
        apply_to = item['sql']
        apply_alias = item['alias']
        apply_lines.append('  {{\n\t\ttype: \'{atype}\',\n\t\tto: \'\n\t\t  {ato}\n\t\t\',\n\t\talias: \'{aalias}\',\n\t  }}'.format(
            atype=apply_type, ato=apply_to, aalias=apply_alias))

where_lines = []
if where.__len__() > 0:
    for item in where:
        where_name = item['name']
        where_type = item['match_type']
        where_value = item['value']
        where_lines.append('  {{ name: \'{wname}\', match: \'{wtype}\', value: \'{wvalue}\' }}'.format(
            wname=where_name, wtype=where_type, wvalue=where_value.replace('\'', '')))

coral_sql = 'datasource: {{\n\t{sline}\n\t{tline}\n\t{fline}\n\tjoin: [\n\t{jlines}\n\t],\n\tapply: [\n\t{alines}\n\t],\n\twhere: [\n\t{wlines}\n\t],\n\torderby: \'{oby}\'\n}}'.format(
    sline=select_line, tline=top_line, fline=from_line, jlines=',\n\t'.join(map(str, join_lines)), alines=',\n\t'.join(map(str, apply_lines)), wlines=',\n\t'.join(map(str, where_lines)), oby=' '.join(map(str, orderby)))

# Fuck Python ternary string interpolation. Condense the above lines so I can do a quick sanity check for their existence in the ternary_coral_sql format()
ternary_sline = "\n\t{sline}".format(sline=select_line)
ternary_tline = "\n\t{tline}".format(tline=top_line)
ternary_fline = "\n\t{fline}".format(fline=from_line)
ternary_jlines = "\n\tjoin: [\n\t{jlines}\n\t],".format(
    jlines=',\n\t'.join(map(str, join_lines)))
ternary_alines = "\n\tapply: [\n\t{alines}\n\t],".format(
    alines=',\n\t'.join(map(str, apply_lines)))
ternary_wlines = "\n\twhere: [\n\t{wlines}\n\t],".format(
    wlines=',\n\t'.join(map(str, where_lines)))
ternary_oby = "\n\torderby: \'{oby}\'".format(oby=' '.join(map(str, orderby)))

ternary_coral_sql = 'datasource: {{{tsline}{ttline}{tfline}{tjlines}{talines}{twlines}{toby}\n}}'.format(
    tsline=ternary_sline if ternary_sline else "", ttline=ternary_tline if ternary_tline else "", tfline=ternary_fline if ternary_fline else "", tjlines=ternary_jlines if join_lines else "", talines=ternary_alines if apply_lines else "", twlines=ternary_wlines if where_lines else "", toby=ternary_oby if orderby_indices else "")

# Write that monstrosity that is the coral sql into an output file for people to copy from
with open(output_file, 'w') as out_file:
    out_file.write(ternary_coral_sql)
