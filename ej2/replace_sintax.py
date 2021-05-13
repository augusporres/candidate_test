# el script va a generar un archivo my_expected.v
# en donde se tiene la sintaxis correcta


import re

with open('testcase.v', 'r') as f, open('my_expected.v', 'w') as d:
    file_content = f.read()
    new_content = re.sub(r'  reg \[(.*)\] (\S*) \[(.*)\];\n  initial begin\n((    \S*\[\S*\] = \S*;\n)*)  end\n', '  reg [7:0] mem [15:0];\n  $readmemh("memdump0.mem", mem);\n', file_content, flags=0)
    d.write(new_content)



