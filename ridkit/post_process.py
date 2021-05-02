
import os, json, glob, shutil
import numpy as np
from ridkit.lib.utils import make_iter_name, make_walker_name, cmd_append_log, set_resource, set_machine, log_task

from ridkit.lib.cal_cv_dim import cal_cv_dim
from ridkit.lib.cmpf import cmpf

from dpdispatcher.submission import Submission, Job, Task, Resources

enhc_out_conf="confs/"
enhc_out_angle="angle.rad.out"
enhc_out_plm="plm.out"
enhc_name="00.enhcMD"

res_name="01.resMD"
res_plm="plumed.res.dat"

def post_enhc (iter_index, 
               json_file,
               base_dir="./") :
    base_dir = os.path.abspath(base_dir) + "/"
    iter_name = make_iter_name (iter_index)
    work_path = base_dir + iter_name + "/" + enhc_name + "/"  
    
    fp = open (json_file, 'r')
    jdata = json.load (fp)
    fp.close()
    gmx_split = jdata["gmx_split_traj"]
    gmx_split_log = "gmx_split.log"
    gmx_split_cmd = cmd_append_log (gmx_split, gmx_split_log)
    
    all_task = list(filter(lambda x:os.path.isdir(x),  glob.glob(work_path + "/[0-9]*[0-9]")))
    all_task.sort()

    cwd = os.getcwd()
    numb_walkers = jdata["numb_walkers"]
    for ii in range(numb_walkers) :
        walker_path = work_path + make_walker_name(ii) + "/"
        os.chdir(walker_path)        
        if os.path.isdir ("confs") : 
            shutil.rmtree ("confs")
        os.makedirs ("confs")
        os.chdir(cwd)

    machine = set_machine(json_file)
    resources = set_resource(json_file, target="post")
    gmx_split_task = [ Task(command=gmx_split_cmd, task_work_path=ii, outlog='gmx_split.log', errlog='gmx_split.err') for ii in all_task ]
    gmx_split_submission = Submission(work_base=work_path, resources=resources, batch=machine, task_list=gmx_split_task)
    gmx_split_submission.run_submission()
    print('rid.py:post_enhc:gmx_split_cmd', gmx_split_cmd)
    
    for ii in range(numb_walkers) :
        walker_path = work_path + make_walker_name(ii) + "/"
        angles = np.loadtxt (walker_path + enhc_out_plm)
        print(angles.shape)
        np.savetxt (walker_path + enhc_out_angle, angles[:,1:], fmt="%.6f")



def post_res (iter_index,
              json_file,
              cv_file,
              base_dir="./") :
    fp = open (json_file, 'r')
    jdata = json.load (fp)
    fp.close()

    base_dir = os.path.abspath(base_dir) + "/"
    iter_name = make_iter_name (iter_index)
    res_path = base_dir + iter_name + "/" + res_name + "/"  
    cwd = os.getcwd()
    
    os.chdir(res_path)
    all_task = glob.glob("/[0-9]*[0-9]")
    all_task = list(filter(lambda x:os.path.isdir(x),  glob.glob("[0-9]*[0-9]")))
    if len(all_task) == 0 :
        np.savetxt (res_path + 'data.raw', [], fmt = "%.6e")        
        return
    all_task.sort()
    centers = []
    force = []
    ndim = 0
    _conf_file = os.path.abspath(all_task[0] + "/conf.gro")
    cv_dim_list = cal_cv_dim (_conf_file, cv_file)
    cv_dih_dim = cv_dim_list[0]

    for work_path in all_task:
        os.chdir(work_path)
        cmpf(cv_dih_dim, plm_out="plm.res.out", kappa_file='kappa.out', center_file='centers.out', tail=0.90, out_put='force.out')
        this_centers = np.loadtxt ('centers.out')
        centers = np.append (centers, this_centers)
        this_force = np.loadtxt ('force.out')
        force = np.append (force, this_force)        
        ndim = this_force.size
        assert (ndim == this_centers.size), "center size is diff to force size in " + work_path
        os.chdir(res_path)
    print('cmpf done')

    os.chdir(cwd)
    centers = np.reshape (centers, [-1, ndim])
    force = np.reshape (force, [-1, ndim])
    data = np.concatenate ((centers, force), axis = 1)
    np.savetxt (res_path + 'data.raw', data, fmt = "%.6e")

    norm_force = np.linalg.norm (force, axis = 1)
    log_task ("min|f| = %e  max|f| = %e  avg|f| = %e" % 
              (np.min(norm_force), np.max(norm_force), np.average(norm_force)))
    print('save cmpf done!')