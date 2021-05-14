# el script va a generar un archivo my_expected.v
# en donde se tiene la sintaxis correcta.
# También se vuelca el contenido de la memoria en my_memdump0.mem
import re

with open('testcase.v', 'r') as f, open('my_expected.v', 'w') as d, open('my_memdump0.mem', 'w') as memdump:
    # Corrijo sintaxis
    file_content = f.read()
    new_content = re.sub(r'  reg \[(.*)\] (\S*) \[(.*)\];\n  initial begin\n((    \S*\[\S*\] = \S*;\n)*)  end\n', '  reg [7:0] mem [15:0];\n  $readmemh("memdump0.mem", mem);\n', file_content, flags=0)
    d.write(new_content)

    # Extraigo valores de inicializacion
    f.seek(0,0)
    for line in f:
        reg = re.compile(r'    mem\[(\d)*\] = 8\'h(\d|\w)(\d|\w);\n')
        mo = reg.search(line)
        if (mo):
            memdump.write((mo.group(2)+mo.group(3))+'\n')



