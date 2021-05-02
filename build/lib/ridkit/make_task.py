import os, glob, json
from ridkit.lib.utils import create_path

def gen_rid (out_dir,
              mol_dir,
              rid_json) :
    mol_dir += "/"
    out_dir += "/"
    conf_file = glob.glob(mol_dir + "*.gro")
    fp = open (rid_json, 'r')
    jdata = json.load (fp)    
    numb_walkers = jdata['numb_walkers']
    create_path (out_dir)
    print(conf_file)
    assert (len(conf_file) >= int(numb_walkers)), "number of conformation files must be equal to the number of walkers."

def main_debug():
    create_path("./debug")
    return
   
if __name__ == '__main__':
    # _main()
    main_debug()
