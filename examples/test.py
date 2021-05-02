import os, json
from ridkit import make_task, make_enhc, make_res, run, post_process, make_train

def main():
    out_dir = './test_rid'
    mol_dir = './mol'
    rid_json = './rid.json'
    graph_files = []
    cv_file = "./phipsi_selected.json"
    fp = open(rid_json, 'r')
    jdata = json.load(fp)
    fp.close()

    iter_numb = int(jdata['numb_iter'])
    for iter_idx in range(iter_numb):
        print("prepare gen_rid")
        make_task.gen_rid (out_dir, mol_dir, rid_json)
        print("prepare gen_enhc")
        make_enhc.make_enhc(iter_idx, rid_json, graph_files, mol_dir, cv_file ,base_dir=out_dir)
        print("prepare run enhc")
        run.run_enhc(iter_idx, rid_json, base_dir=out_dir)
        print("prepare post enhc")
        post_process.post_enhc(iter_idx, rid_json, base_dir=out_dir)
        print("prepare gen_res")
        make_res.make_res(iter_index=iter_idx, json_file=rid_json, cv_file=cv_file, mol_path=mol_dir, base_dir=out_dir)
        print("prepare run res")
        md_run.run_res (iter_index=iter_idx, json_file=rid_json, base_dir=out_dir)
        print("prepare post res")
        post_process.post_res(iter_index=iter_idx, json_file=rid_json, cv_file=cv_file, base_dir=out_dir)
        print("prepare gen train")
        make_train.make_train(iter_index=iter_idx, json_file=rid_json, base_dir=out_dir)
        print("prepare run train")
        run.run_train(iter_index=iter_idx, json_file=rid_json, cv_file=cv_file, base_dir=out_dir)


if __name__ == "__main__":
    main()