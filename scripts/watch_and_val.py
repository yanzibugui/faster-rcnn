#coding: utf-8
import argparse
import json
from glob import glob
import os
import subprocess
import time


def glob_all(dir_path):
    ckpt_list = []
    ckpt_list.extend(glob(os.path.join(dir_path, '*.ckpt')))
    inside = os.listdir(dir_path)
    for dir_name in inside:
        if os.path.isdir(os.path.join(dir_path, dir_name)):
            ckpt_list.extend(glob_all(os.path.join(dir_path, dir_name)))
    return ckpt_list


def glob_all_dict(dir_path):
    ckpt_list = glob_all(dir_path)
    ckpt_dict = {}
    for ckpt in ckpt_list:
        ckpt_dict[ckpt] = True
    return ckpt_dict


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--ckpt-dir', default='output/faster_rcnn_end2end/')
    """加入事先执行的，这个是关键词搜索，有这个关键词的就去执行"""
    parser.add_argument('-e', '--eval-old', default=None, help='example: sz_lights_train,sz_cyc_train')
    args = parser.parse_args()
    return args


def add_report(ckpt):
    """
    example:
    ckpt: output/faster_rcnn_end2end/sz_cyc_train/VGGnet_fast_rcnn_iter_5000.ckpt
    """
    iter_number = int(ckpt.split('.')[-2].split('_')[-1])
    model_name = ckpt.split('/')[-2]
    save_file_name = model_name + '.txt'
    save_file_name = os.path.join(args.ckpt_dir, save_file_name)
    if os.path.exists(save_file_name) is False:
        with open(save_file_name, 'w'):
            pass
    """replace"""
    imdb_val = model_name.replace('train', 'val')
    command = './tools/test_net.py --gpu 0  --cfg experiments/cfgs/faster_rcnn_end2end.yml '\
        '--network VGGnet_test --imdb %s --weights %s' % (imdb_val, ckpt)
    print(iter_number, model_name, command)
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    out, err = p.communicate()
    result = out.splitlines()
    AP = float(result[-2].decode('utf-8').split(' ')[-1])
    with open(save_file_name, 'a') as f:
        f.write('%s %s iter: %d AP: %f\n' % (time.strftime('%Y-%m-%d %H:%M'), model_name, iter_number, AP))


def main(args):
    ckpt_dict = glob_all_dict(args.ckpt_dir)
    if args.eval_old:
        eval_list = args.eval_old.split(',')
        for keyword in eval_list:
            keyword = keyword.strip()
            if keyword:
                for ckpt in ckpt_dict:
                    if ckpt.find(keyword) != -1:
                        add_report(ckpt)
    print('Now watching.....')
    while True:
        time.sleep(30)
        new_ckpt_dict = glob_all_dict(args.ckpt_dir)
        for ckpt in new_ckpt_dict:
            if ckpt not in ckpt_dict:
                print('*************************SUNNY:)*******************************')
                add_report(ckpt)
                time.sleep(5)
        ckpt_dict = new_ckpt_dict
    # add_report('output/faster_rcnn_end2end/sz_cyc_train/VGGnet_fast_rcnn_iter_5000.ckpt')

if __name__ == '__main__':
    args = parse_args()
    main(args)