import csv

from .standardizer import Documentizer

CFILE = '/Users/jfenton/github-whitelabel/concordance/irs-efile-master-concordance-file/efiler_master_concordance.csv'
            
def read_concordance():
    """ returns an array of rows """

    reader = csv.DictReader(open(CFILE))
    xpath_hash = {}
    var_hash = {}
    for row in reader:
        #print(row)
        try:
            xpath_hash[row['xpath']] = xpath_hash[row['xpath']] + [row]
        except KeyError:
            xpath_hash[row['xpath']] = [row]

        try:
            var_hash[row['variable_name']] = var_hash[row['variable_name']] + [row]
        except KeyError:
            var_hash[row['variable_name']] = [row]

    return {'xpath_hash':xpath_hash, 'var_hash':var_hash}


def get_concordance_var_version(var_array, version):
    for var in var_array:
        if version in var['version'].split(';'):
            print ("Got %s %s" % (var['variable_name'], version))
            return var['variable_name']

    return None


if __name__ == '__main__':

    cvars = read_concordance()
    xpath_hash = cvars['xpath_hash']
    var_hash = cvars['var_hash']

    documentizer = Documentizer(versions=True)
    variables = documentizer.get_variables()
    # for var in variables:
    #     #print(var)
    #     thisvar = documentizer.get_var(var)

    #     this_xpath = thisvar['xpath']
        
    #     if this_xpath.startswith("/IRS990"):
    #         this_xpath = "/Return/ReturnData" + this_xpath
    #     else:
    #         this_xpath = "/Return" + this_xpath

    #     this_jfvar = thisvar['db_table'] + '_' + thisvar['db_name']
    #     modern_concordance_var = None   
    #     try:    
    #         modern_concordance_var = get_concordance_var_version(xpath_hash[this_xpath], '2015v3.0')
        
    #     except KeyError:
    #         print("keyerror for %s" % this_xpath)
    #         continue

    #     if modern_concordance_var:
    #         pass
    #         print("Found %s <-> %s : %s" % (modern_concordance_var, this_xpath, thisvar ))
            
    ## run through variables, find them in concordance, then extend them
    print("Now looking to extend post 2013 vars")
    for var in variables:
        thisvar = documentizer.get_var(var)
        this_jfvar = thisvar['db_table'] + '_' + thisvar['db_name']
        print ("Handling var %s, %s" % (var, this_jfvar))


