import json
from ridkit.lib.make_ndx import make_ndx
from ridkit.lib.make_def import make_general_angle_def, make_general_dist_def

def cal_cv_dim (conf_file, cv_file) :    
    cfile = conf_file
    jfile = cv_file
    residues, residue_atoms = make_ndx (cfile)
    fp = open (jfile, 'r')
    jdata = json.load (fp)
    fp.close()
    dih_angles = jdata["dih_angles"]
    fmt_alpha = jdata["alpha_idx_fmt"]
    fmt_angle = jdata["angle_idx_fmt"]
    hp_residues = []
    dist_atom = []
    dist_excl = 10000
    if "hp_residues" in jdata :
        hp_residues = jdata["hp_residues"]
    if "dist_atom" in jdata:
        dist_atom = jdata["dist_atom"]
    if "dist_excl" in jdata:
        dist_excl = jdata["dist_excl"]

    angle_names, angle_atom_idxes = make_general_angle_def(residue_atoms, dih_angles, fmt_alpha, fmt_angle)
    dist_names, dist_atom_idxes = make_general_dist_def(residues, residue_atoms, hp_residues, dist_atom, fmt_alpha, dist_excl)
    return [len(angle_names), len(dist_names)]