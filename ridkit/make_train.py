import os, json, glob, shutil
from ridkit.lib.utils import make_iter_name, make_walker_name
from ridkit.lib.utils import create_path
from ridkit.lib.utils import log_task

res_name="01.resMD"
train_name="02.train"


def collect_data(iter_index, base_dir):
    iter_name = make_iter_name (iter_index)
    train_path = base_dir + iter_name + "/" + train_name + "/"  
    data_path = train_path + "data/"
    data_file = train_path + "data/data.raw"
    data_old_file = train_path + "data/data.old.raw"
    data_new_file = train_path + "data/data.new.raw"
    cwd = os.getcwd() + "/"
    # collect data
    log_task ("collect data upto %d" % (iter_index))
    if iter_index == 0 :
        ii = 0
        this_raw = base_dir + make_iter_name (ii) + "/" + res_name + "/data.raw"
        os.chdir(data_path)
        os.symlink (os.path.relpath(this_raw), os.path.basename(data_new_file))
        os.symlink (os.path.basename(data_new_file), os.path.basename(data_file))
        os.chdir (cwd)
        open (data_old_file, "w").close()
    else :
        prev_iter_index = iter_index - 1
        prev_data_file = base_dir + make_iter_name(prev_iter_index) + "/" + train_name + "/data/data.raw"
        this_raw = base_dir + make_iter_name (iter_index) + "/" + res_name + "/data.raw"
        os.chdir(data_path)
        os.symlink (os.path.relpath(prev_data_file), os.path.basename(data_old_file))
        os.symlink (os.path.relpath(this_raw), os.path.basename(data_new_file))
        os.chdir(cwd)
        with open(data_file, "wb") as fo :
            with open(data_old_file, "rb") as f0, open(data_new_file, "rb") as f1 :
                shutil.copyfileobj(f0, fo)
                shutil.copyfileobj(f1, fo)


def make_train (iter_index, 
                json_file,
                base_dir="./") :
    json_file = os.path.abspath(json_file)
    fp = open (json_file, 'r')
    jdata = json.load (fp)
    fp.close()
    # template_dir = jdata["template_dir"]    
    numb_model = jdata["numb_model"]
    res_iter = jdata["res_iter"]
    
    # abs path
    base_dir = os.path.abspath(base_dir) + "/"
    iter_name = make_iter_name (iter_index)
    train_path = base_dir + iter_name + "/" + train_name + "/"  
    data_path = train_path + "data/"
    cwd = os.getcwd() + "/"
    create_path (train_path) 
    os.makedirs(data_path)
    collect_data(iter_index, base_dir)
    
    # create train dirs
    log_task ("create train dirs")
    for ii in range(numb_model) :
        work_path = train_path + ("%03d/" % ii) 
        old_model_path = work_path + "old_model/"
        create_path (work_path)
        os.chdir (work_path)
        os.symlink ("../data", "./data")
        os.chdir (cwd)
        if iter_index >= 1 :
            prev_iter_index = iter_index - 1
            prev_iter_name = make_iter_name (prev_iter_index)
            prev_train_path = base_dir + prev_iter_name + "/" + train_name + "/"  
            prev_work_path = prev_train_path + ("%03d/" % ii)
            prev_model_files = glob.glob (prev_work_path + "model.ckpt.*")
            prev_model_files = prev_model_files + [prev_work_path + "checkpoint"]
            create_path (old_model_path)
            os.chdir(old_model_path)
            # why to copy twice.
            for ii in prev_model_files :
                os.symlink(os.path.relpath(ii), os.path.basename(ii))
            os.chdir(cwd)
            for jj in prev_model_files :
                shutil.copy (jj, work_path) 
    print("Training files have prepared.")
