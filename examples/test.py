import os, json
from ridkit import make_task, make_enhc, make_res, run, post_process, make_train, record_task, get_checkpoint

def main():
    out_dir = './test_rid'
    mol_dir = './mol'
    rid_json = './rid.json'
    graph_files = []
    cv_file = "./phipsi_selected.json"
    fp = open(rid_json, 'r')
    jdata = json.load(fp)
    fp.close()
    record_file = out_dir + "/record.txt"
    checkpoint = get_checkpoint(record_file)
    max_tasks = 10
    number_tasks = 8
    iter_numb = int(jdata['numb_iter'])

    if sum(checkpoint) < 0:
        print("prepare gen_rid")
        make_task.gen_rid (out_dir, mol_dir, rid_json)

    for iter_idx in range(iter_numb):
        for tag in range(number_tasks):
            if iter_idx * max_tasks + number_tasks <= checkpoint[0] * max_tasks + checkpoint[0]:
                continue
            elif tag == 0:
                print("prepare gen_enhc")
                make_enhc.make_enhc(iter_idx, rid_json, graph_files, mol_dir, cv_file ,base_dir=out_dir)
                record_task(record_file, iter_idx, tag)
            elif tag == 1:
                print("prepare run enhc")
                run.run_enhc(iter_idx, rid_json, base_dir=out_dir)
                record_task(record_file, iter_idx, tag)
            elif tag == 2:
                print("prepare post enhc")
                post_process.post_enhc(iter_idx, rid_json, base_dir=out_dir)
                record_task(record_file, iter_idx, tag)
            elif tag == 3:
                print("prepare gen_res")
                make_res.make_res(iter_index=iter_idx, json_file=rid_json, cv_file=cv_file, mol_path=mol_dir, base_dir=out_dir)
                record_task(record_file, iter_idx, tag)
            elif tag == 4:
                print("prepare run res")
                run.run_res (iter_index=iter_idx, json_file=rid_json, base_dir=out_dir)
                record_task(record_file, iter_idx, tag)
            elif tag == 5:
                print("prepare post res")
                post_process.post_res(iter_index=iter_idx, json_file=rid_json, cv_file=cv_file, base_dir=out_dir)
                record_task(record_file, iter_idx, tag)
            elif tag == 6:
                print("prepare gen train")
                make_train.make_train(iter_index=iter_idx, json_file=rid_json, base_dir=out_dir)
                record_task(record_file, iter_idx, tag)
            elif tag == 7:
                print("prepare run train")
                run.run_train(iter_index=iter_idx, json_file=rid_json, cv_file=cv_file, base_dir=out_dir)
                record_task(record_file, iter_idx, tag)


if __name__ == "__main__":
    main()
