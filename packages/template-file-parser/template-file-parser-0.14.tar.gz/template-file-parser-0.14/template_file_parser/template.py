from string import Template

def parse_file(in_file, out_file, variables, safe=False):
    '''
    This function was inspired by: https://stackoverflow.com/a/6385940/2343743
    '''
    with open(in_file) as in_fh, open(out_file,'w') as out_fh:
        src = Template(in_fh.read())
        if safe:
            res = src.safe_substitute(variables)
        else:
            res = src.substitute(variables)
        out_fh.write(res)
        

