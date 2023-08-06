import re
import os
import argparse

def format_yaml(table_name, field_list):
    TABLE_NAME_FORMAT = """tableName: {}
columns:"""

    COLUMNS_FORMAT = """  - name: {}
    dataType: 
    length: 
    defaultValue: 
    allowsNull: false
    isUniqueKey: true
    isCriteria: false
    isFuzzy: false
    isResponse: true"""
    
    final_table_name = TABLE_NAME_FORMAT.format(table_name)
    final_table_field_str = ""
    
    for field in field_list:
        tmp_str = COLUMNS_FORMAT.format(field) + os.linesep
        final_table_field_str += tmp_str 
    res = final_table_name + os.linesep + final_table_field_str
    return res


def generate_yaml():
    parser = argparse.ArgumentParser(description='please input sql path.')
    parser.add_argument('--path', dest="path")

    args = parser.parse_args()

    DEFAULT_IGNORE_STR = ("PRIMARY", "UNIQUE",)

    table_sql = ""

    reader = open(args.path)
    with reader:
        table_sql += reader.read().replace("\n", "")

    p_table = re.compile("(?<=CREATE TABLE).*?(?=ENGINE)")
    table_match = p_table.findall(table_sql)

    result = list()

    for table_str in table_match:
        p_table_name = '.*?(?=\()'
        table_name_match = re.findall(p_table_name, table_str.replace(" ", ""))
        table_name = table_name_match[0].replace('`', '')
        field_name_list = list()
        
        p_table_field_name = '(?<=\().*(?=PRIMARY)'
        table_field_name_list_match = re.findall(p_table_field_name, table_str.strip(" "))
        
        for field_name_str in table_field_name_list_match[0].strip(" ").split(","):
            
            field_name = field_name_str.strip(" ").split(" ")[0].replace("`", '')
            
            if field_name.strip() and field_name not in DEFAULT_IGNORE_STR:
                field_name_list.append(field_name)
        
        tmp_yaml = format_yaml(table_name, field_name_list)

        dir_name = "yaml"
        if not os.path.exists(dir_name):
            os.mkdir(dir_name)
        with open('{}{}{}.yaml'.format(dir_name, os.sep, table_name), 'w') as f:
            f.write(tmp_yaml)

if __name__=="__main__":
    generate_yaml()
