#!/usr/bin/env python

import os,sys
import collections
sys.path.append("/tigress/ejdennis/BrainPipe")
from torch import sigmoid
import tools.conv_net.dataprovider3.dataprovider3 as dp
	
import forward
import utils

def main(noeval, **args):

    #args should be the info you need to specify the params
    # for a given experiment, but only params should be used below
    params = fill_params(**args)

    utils.set_gpus(params["gpus"])

    net = utils.create_network(**params)
    if not noeval:
        net.eval()

    utils.log_tagged_modules(params["modules_used"], params["log_dir"],
                             params["log_tag"], params["chkpt_num"])

    for dset in params["dsets"]:
        print(dset)

        fs = make_forward_scanner(dset, **params)

        output = forward.forward(net, fs, params["scan_spec"],
                                 activation=params["activation"])

        save_output(output, dset, **params)


def fill_params(expt_name, expt_dir,chkpt_num, gpus,
                nobn, model_fname, tag):

    params = {}

    #Model params
    params["in_spec"]     = dict(input=(1,20,192,192))
    params["output_spec"] = collections.OrderedDict(soma=(1,20,192,192))
    params["width"]       = [32, 40, 80]
    params["activation"]  = sigmoid
    params["chkpt_num"]   = chkpt_num

    #GPUS
    params["gpus"] = gpus

    #IO/Record params
    params["expt_name"]   = expt_name
    params["expt_dir"]    = expt_dir
    params["model_dir"]   = os.path.join(params["expt_dir"], "models")
    params["log_dir"]     = os.path.join(params["expt_dir"], "logs")
    params["fwd_dir"]     = os.path.join(params["expt_dir"], "forward")
    params["log_tag"]     = "fwd_" + tag if len(tag) > 0 else "fwd"
    params["output_tag"]  = tag

    #Dataset params
    test_dir = os.path.join(expt_dir,"training_data","test")
    params["data_dir"] = test_dir
    assert os.path.isdir(test_dir),"nonexistent data directory"

    test_sets = [x.split('_lbl.tif')[0] for x in os.listdir(test_dir) if 'lbl' in x] 
    assert len(test_sets) > 0
    params["dsets"]       = test_sets
    params["input_spec"]  = collections.OrderedDict(input=(20,192,192)) #dp dataset spec
    params["scan_spec"]   = collections.OrderedDict(soma=(1,20,192,192))
    params["scan_params"] = dict(stride=(0.75,0.75,0.75), blend="bump")

    #Use-specific Module imports
    params["model_class"] = utils.load_source(model_fname).Model

    #"Schema" for turning the parameters above into arguments
    # for the model class
    params["model_args"]   = [params["in_spec"], params["output_spec"],
                              params["width"]]
    params["model_kwargs"] = {}

    #Modules used for record-keeping
    params["modules_used"] = [__file__, model_fname, "layers.py"]

    return params


def make_forward_scanner(dset_name, data_dir, input_spec,
                         scan_spec, scan_params, **params):
    """ Creates a DataProvider ForwardScanner from a dset name """

    # Reading lightsheet image
    if os.path.isfile(os.path.join(data_dir, dset_name + "_img.h5")):
        img = utils.read_img(os.path.join(data_dir, dset_name + "_img.h5"))
    elif os.path.isfile(os.path.join(data_dir, dset_name + "_img.tif")):
        img = utils.read_img(os.path.join(data_dir, dset_name + "_img.tif"))
        
    img = (img / 255.).astype("float32")

    # Creating DataProvider Dataset
    vd = dp.Dataset(spec=input_spec)

    vd.add_data(key="input", data=img)

    # Returning DataProvider ForwardScanner
    return dp.ForwardScanner(vd, scan_spec, **scan_params)


def save_output(output, dset_name, chkpt_num, fwd_dir, output_tag, **params):
    """ Saves the volumes within a DataProvider ForwardScanner """

    for k in output.outputs.data:

        output_data = output.outputs.get_data(k)

        if len(output_tag) == 0:
            basename = "{}_{}_{}.tif".format(dset_name, k, chkpt_num)
        else:
            basename = "{}_{}_{}_{}.tif".format(dset_name, k, 
                                               chkpt_num, output_tag)

        full_fname = os.path.join(fwd_dir, basename)

        utils.write_img(output_data, full_fname)


#============================================================



if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument("expt_name",
                        help="Experiment Name")
    parser.add_argument("expt_dir",
                        help="Experiment Directory")
    parser.add_argument("model_fname",
                        help="Model Template Name")
    parser.add_argument("chkpt_num", type=int,
                        help="Checkpoint Number")
    parser.add_argument("--nobn", action="store_true",
                        help="Whether net uses batch normalization")
    parser.add_argument("--gpus", default=["0"], nargs="+")
    parser.add_argument("--noeval", action="store_true",
                        help="Whether to use eval version of network")
    parser.add_argument("--tag", default="",
                        help="Output (and Log) Filename Tag")


    args = parser.parse_args()

    main(**vars(args))
