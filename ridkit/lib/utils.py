import re, os, shutil, logging, json, datetime
from dpdispatcher.lazy_local_context import LazyLocalContext
from dpdispatcher.submission import Task, Resources
from dpdispatcher.pbs import PBS
from dpdispatcher.slurm import Slurm

iter_format = "%06d"
walker_format = "%03d"
task_format = "%02d"
log_iter_head = "iter " + iter_format + " task " + task_format + ": "

def replace (file_name, pattern, subst) :
    file_handel = open (file_name, 'r')
    file_string = file_handel.read ()
    file_handel.close()
    file_string = ( re.sub (pattern, subst, file_string) )
    file_handel = open (file_name, 'w')
    file_handel.write (file_string)
    file_handel.close()

def create_path (path) :
    if os.path.isdir(path) : 
        dirname = os.path.abspath(path)
        counter = 0
        while True :
            bk_dirname = dirname + ".bk%03d" % counter
            if not os.path.isdir(bk_dirname) : 
                # shutil.move (dirname, bk_dirname)
                os.system("mv {} {}".format(dirname, bk_dirname)) 
                print("{} has exists, a back-off {} generated!".format(path, bk_dirname))
                break
            counter += 1
    os.makedirs (path)


def copy_file_list(file_list, from_path, to_path) :
    for jj in file_list : 
        if os.path.isfile(from_path + jj) :
            shutil.copy (from_path + jj, to_path)
        elif os.path.isdir(from_path + jj) :
            cwd=os.getcwd()
            os.chdir(from_path+jj)
            files = glob.glob("*")
            os.chdir(cwd)
            os.makedirs(to_path+jj)
            for ff in files :
                shutil.copy(from_path+jj+'/'+ff, to_path+jj+'/'+ff)


def make_iter_name(iter_index):
    return "iter." + (iter_format % iter_index)

def make_walker_name(walker_index):
    return (walker_format % walker_index)

def checkfile(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)

def log_task (message) :
    header = repeat_to_length (" ", len(log_iter_head % (0, 0)))
    logging.info (header + message)
    # print(header + message)

def repeat_to_length(string_to_expand, length):
    ret = ""
    for ii in range (length) : 
        ret += string_to_expand
    return ret

def cmd_append_log (cmd,
                    log_file) :
    ret = cmd
    ret = ret + " 1> " + log_file
    ret = ret + " 2> " + log_file
    return ret

def set_resource(json_file, target='enhc'):
    fp = open (json_file, 'r')
    jdata = json.load (fp)
    fp.close()
    return Resources(
        number_node=jdata['{}_number_node'.format(target)], 
        cpu_per_node=jdata['{}_cpu_per_node'.format(target)], 
        gpu_per_node=jdata['{}_gpu_per_node'.format(target)], 
        queue_name=jdata['queue_name'], 
        group_size=jdata['{}_group_size'.format(target)], 
        if_cuda_multi_devices=jdata['if_cuda_multi_devices']) 

def set_machine(json_file):
    fp = open (json_file, 'r')
    jdata = json.load (fp)
    fp.close()
    lazy_local_context = LazyLocalContext(local_root='./', work_profile=None)
    if jdata["machine_type"] == "Slurm" or jdata["machine_type"] == "slurm":
        return Slurm(context=lazy_local_context)
    if jdata["machine_type"] == "PBS" or jdata["machine_type"] == "pbs":
        return PBS(context=lazy_local_context)


def print_list (tmp, 
                suffix = "") :
    mylist = ""
    for kk in tmp:
        if len(mylist) == 0 :
            mylist = str(kk) + suffix
        else :
            mylist += "," + str(kk) + suffix
    return mylist


def print_repeat_list (numb, item) :
    mylist=""
    for ii in range(numb) :
        if ii == 0: 
            mylist = str(item)
        else :
            mylist += "," + str(item)
    return mylist


def record_task(record_file, iter_idx, task_idx):
    if os.path.basename(record_file) == '':
        print("please assign a valid record file path.")
        raise RuntimeError

    if os.path.exists(record_file):
        with open(record_file, 'a') as record:
            record.write("iteration: {} task: {}    task finished at {}\n".format(iter_idx, task_idx, datetime.datetime.now().strftime("%H:%M:%S %D")))
    else:
        with open(record_file, 'w') as record:
            record.write("iteration: {} task: {}    task finished at {}\n".format(iter_idx, task_idx, datetime.datetime.now().strftime("%H:%M:%S %D")))
    pass

def get_checkpoint(record_file):
    checkpoint = [-1, -1]
    if not os.path.exists(record_file):
        return [-1, -1]
    else:
        with open(record_file, 'r') as record:
            for line in record.readlines():
                content = line.split()
                if len(content) == 0:
                    continue
                else:
                    checkpoint = [int(content[1]), int(content[3])]
        return checkpoint

if __name__ == '__main__':
    record_task("./new_record.txt", 1, 16)
    print(get_checkpoint("./no_record.txt"))
    print(get_checkpoint("./new_record.txt"))

