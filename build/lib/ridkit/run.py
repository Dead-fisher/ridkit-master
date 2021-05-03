import os, json, glob
from dpdispatcher.lazy_local_context import LazyLocalContext
from dpdispatcher.submission import Submission, Job, Task, Resources

from ridkit.lib.utils import make_iter_name, make_walker_name, cmd_append_log, set_resource, set_machine
from ridkit.lib.cal_cv_dim import cal_cv_dim
from ridkit.lib.nn.train import train
from ridkit.lib.nn.freeze import freeze_graph

enhc_name="00.enhcMD"

enhc_plm="plumed.dat"
enhc_bf_plm="plumed.bf.dat"

res_plm="plumed.res.dat"
res_name="01.resMD"

train_name="02.train"


def run_enhc (iter_index,
              json_file,
              base_dir='./') :
    json_file = os.path.abspath(json_file)
    base_dir = os.path.abspath(base_dir) + "/"
    iter_name = make_iter_name (iter_index)
    work_path = base_dir + iter_name + "/" + enhc_name + "/"  

    fp = open (json_file, 'r')
    jdata = json.load (fp)
    fp.close()
    gmx_prep = jdata["gmx_prep"] + ' -f grompp_restraint.mdp -r conf_init.gro'
    gmx_run = jdata["gmx_run"]
    enhc_thread = jdata["enhc_thread"]
    gmx_run = gmx_run + (" -nt %d " % enhc_thread)
    gmx_prep_log = "gmx_grompp.log"
    gmx_run_log = "gmx_mdrun.log"
    # assuming at least one walker
    graph_files = glob.glob (work_path + (make_walker_name(0)) + "/*.pb")
    if len (graph_files) != 0 :
        gmx_run = gmx_run + " -plumed " + enhc_plm  
    else :
        gmx_run = gmx_run + " -plumed " + enhc_bf_plm
    gmx_prep_cmd = cmd_append_log (gmx_prep, gmx_prep_log)
    gmx_run_cmd = cmd_append_log (gmx_run, gmx_run_log)
    numb_walkers = jdata["numb_walkers"]

    print('debug', glob.glob(work_path + "/[0-9]*[0-9]"))
    all_task = list(filter(lambda x:os.path.isdir(x),  glob.glob(work_path + "/[0-9]*[0-9]")))
    all_task.sort()

    all_task_basedir = [os.path.relpath(ii, work_path) for ii in all_task]
    print('run_enhc:work_path', work_path)
    print('run_enhc:gmx_prep_cmd:', gmx_prep_cmd)
    print('run_enhc:gmx_run_cmd:', gmx_run_cmd)
    print('run_enhc:all_task:', all_task)
    print('run_enhc:all_task_basedir:', all_task_basedir)
    
    machine = set_machine(json_file)
    resources = set_resource(json_file, target="enhc")

    gmx_prep_task = [ Task(command=gmx_prep_cmd, task_work_path=ii, outlog='gmx_grompp.log', errlog='gmx_grompp.err') for ii in all_task_basedir ]
    gmx_prep_submission = Submission(work_base=work_path, resources=resources, batch=machine, task_list=gmx_prep_task)

    gmx_prep_submission.run_submission()
    
    gmx_run_task =  [ Task(command=gmx_run_cmd, task_work_path=ii, outlog='gmx_mdrun.log', errlog='gmx_mdrun.log') for ii in all_task_basedir ]
    gmx_run_submission = Submission(work_base=work_path, resources=resources, batch=machine, task_list=gmx_run_task)
    gmx_run_submission.run_submission()


def run_res (iter_index,
             json_file,
             base_dir="./") :
    json_file = os.path.abspath(json_file)
    fp = open (json_file, 'r')
    jdata = json.load (fp)
    fp.close()
    gmx_prep = jdata["gmx_prep"]
    gmx_run = jdata["gmx_run"]
    res_thread = jdata["res_thread"]
    gmx_run = gmx_run + (" -nt %d " % res_thread)
    gmx_run = gmx_run + " -plumed " + res_plm
    gmx_cont_run = gmx_run + " -cpi state.cpt "
    gmx_prep_log = "gmx_grompp.log"
    gmx_run_log = "gmx_mdrun.log"
    gmx_prep_cmd = cmd_append_log (gmx_prep, gmx_prep_log)
    gmx_run_cmd = cmd_append_log (gmx_run, gmx_run_log)
    gmx_cont_run_cmd = cmd_append_log (gmx_cont_run, gmx_run_log)
    
    base_dir = os.path.abspath(base_dir) + "/"
    iter_name = make_iter_name (iter_index)
    res_path = base_dir + iter_name + "/" + res_name + "/"  

    if not os.path.isdir (res_path) : 
        raise RuntimeError ("do not see any restrained simulation (%s)." % res_path)
    
    all_task = list(filter(lambda x:os.path.isdir(x),  glob.glob(res_path + "/[0-9]*[0-9]")))
    print('lib.modeling.run_res:all_task_propose:', all_task)
    print('lib.modeling.run_res:gmx_prep_cmd:', gmx_prep_cmd)
    print('lib.modeling.run_res:gmx_run_cmd:', gmx_run_cmd)
    print('lib.modeling.run_res:gmx_cont_run_cmd:', gmx_cont_run_cmd)

    if len(all_task) == 0:
        return None
    all_task.sort()
    all_task_basedir = [os.path.relpath(ii, res_path) for ii in all_task]

    res_resources = set_resource(json_file, target="res")
    machine = set_machine(json_file)

    gmx_prep_task = [ Task(command=gmx_prep_cmd, task_work_path=ii, outlog='gmx_grompp.log', errlog='gmx_grompp.err') for ii in all_task_basedir ]
    gmx_prep_submission = Submission(work_base=res_path, resources=res_resources, batch=machine, task_list=gmx_prep_task)
    gmx_prep_submission.run_submission()

    gmx_run_task =  [ Task(command=gmx_run_cmd, task_work_path=ii, outlog='gmx_mdrun.log', errlog='gmx_mdrun.log') for ii in all_task_basedir ]
    gmx_run_submission = Submission(work_base=res_path, resources=res_resources, batch=machine, task_list=gmx_run_task)
    gmx_run_submission.run_submission()


def check_new_data(iter_index, train_path, base_path):
    # check if new data is empty
    new_data_file = os.path.join(train_path, 'data/data.new.raw')
    if os.stat(new_data_file).st_size == 0 :
        prev_iter_index = iter_index - 1
        prev_train_path = base_path + make_iter_name(prev_iter_index) + "/" + train_name + "/"
        prev_models = glob.glob(prev_train_path + "*.pb")
        for ii in prev_models :
            model_name = os.path.basename(ii)
            os.symlink(ii, os.path.join(train_path, model_name))
        return True
    else:
        return False


def run_train (iter_index, 
               json_file, 
               cv_file,
               base_dir="./") :
    json_file = os.path.abspath(json_file)
    cv_file = os.path.abspath(cv_file)
    fp = open (json_file, 'r')
    jdata = json.load (fp)
    fp.close()
    cv_file = os.path.abspath(cv_file)
    numb_model = jdata["numb_model"]
    train_thread = jdata["train_thread"]
    res_iter = jdata["res_iter"]
    base_dir = os.path.abspath(base_dir) + "/"
    iter_name = make_iter_name (iter_index)
    train_path = base_dir +  iter_name + "/" + train_name + "/"  

    enhc_path = base_dir + iter_name + "/" + enhc_name + "/"  
    _conf_file = enhc_path + "000/conf.gro"
    cwd = os.getcwd()
    
    if check_new_data(iter_index, train_path, base_dir):
        return
    
    neurons = jdata["neurons"]
    batch_size = jdata["batch_size"]
    if iter_index < res_iter :
        numb_epoches = jdata["numb_epoches"]
        starter_lr = jdata["starter_lr"]
        decay_steps = jdata["decay_steps"]
        decay_rate = jdata["decay_rate"]    
        cmdl_args = ""
        use_mix = False
        restart = False
        old_ratio = 7.0
    else :
        numb_epoches = jdata["res_numb_epoches"]
        starter_lr = jdata["res_starter_lr"]
        decay_steps = jdata["res_decay_steps"]
        decay_rate = jdata["res_decay_rate"]            
        old_ratio = jdata["res_olddata_ratio"]
        use_mix = True
        restart = True

    task_dirs = [ ("%03d" % ii) for ii in range(numb_model) ]
    cv_dim_list = cal_cv_dim(_conf_file, cv_file)
    
    os.chdir (train_path)
    for work_path in task_dirs:
        os.chdir(work_path)
        train(
            cv_dim_list,
            neurons=neurons,
            numb_threads=train_thread,
            resnet=True,
            use_mix=use_mix,
            restart=restart,
            batch_size=batch_size,
            epoches=int(numb_epoches),
            lr=float(starter_lr),
            decay_steps=decay_steps,
            decay_rate=decay_rate,
            old_ratio=old_ratio,
            decay_steps_inner=0,
            init_model=None
        )
        freeze_graph("./", output="graph.pb")
        os.chdir(train_path)

    for ii in range(numb_model) :
        os.symlink ("%03d/graph.pb" % ii, "graph.%03d.pb" % ii)
    os.chdir (cwd)