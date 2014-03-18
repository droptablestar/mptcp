__author__ = 'Nadya'
#!/usr/bin/python


"""
Program arguments:
plots_n_rcv.py --help

args: -f <folder_name> -m <multiple>-p <num_plots> -r <num_rcv> -s <num_snd> -nflow <num_f>

optional arguments:
  -h, --help    show this help message and exit

  -f F          Folder name           : Give folder name that contains the csv files
  -m M          Multiple folders      : Compare multiple tests. Folders must match the number of csv files

  -p P          Number of plots       : Optional, same as the number of rcv or less if it's needed it.
  -g G          Graph start           : To adjust plotting legend

  -r R          Number of rcv
  -s S          Number of Senders
  -nflow        Number of subflows



To Run the program:
-------------------
plots_n_rcv.py -f ~/../..test_2 -r 2 -s 5 -nflow 6

"""

import os, argparse
import numpy as np
import collections
import matplotlib.pyplot as plt

def parse_args():
    parser = argparse.ArgumentParser(description=
            "args: -f <folder_name> -m <multiple>-p <num_plots>  -r <num_rcv> -s <num_snd>  -nflow <num_f> ")

    parser.add_argument('-f',
                        action="store",
                        required=True,
                        help="Folder name",
                        default="")
    parser.add_argument('-m',
                        action="store",
                        help="Multiple folders",
                        default=False)
    parser.add_argument('-p',
                        action="store",
                        help="Number of plots",
                        default=1)
    parser.add_argument('-r',
                        action="store",
                        help="Number of rcv",
                        default=1)
    parser.add_argument('-s',
                        action="store",
                        help="Number of Senders",
                        default=1)
    parser.add_argument('-nflow',
                        action="store",
                        help="Number of subflows",
                        default=1)
    parser.add_argument('-g',
                        action="store",
                        help="Graph start",
                        default=0)

    args = parser.parse_args()
    args.f = str(args.f)
    args.p = int(args.p)
    args.r = int(args.r)
    args.s = int(args.s)
    args.nflow = int(args.nflow)
    args.g = int(args.g)
    return args

def get_test_folder(args):

    #To read multiple (m) Folders
    if args.m:
        folder_path = [os.path.abspath(args.f)+'/'+test for test in os.listdir(args.f)]

    # Single Folder
    else:
        folder_path = [os.path.abspath(args.f) if os.path.exists(args.f) else ""]

     # Folder Paths:
    if folder_path == "":
        raise AssertionError("\n\n** Folder doesn't exist **\n")

    else:
        folder_names = [ os.path.basename(t_name) for t_name in folder_path]
        print "\nFolder name: ", folder_names
        #print "[folder_path]", folder_path
        return folder_path

def get_file_names(nfolder):

    # Folder Names
    file_names= [files for root, dirs, files in os.walk(nfolder)]

    # [1:] To remove .DS_Store temp files
    file_names= file_names[0][1:] if ".DS_Store" == file_names[0][0] else file_names[0]

    return nfolder, file_names

def dict_values(snd, rcv, nflw, folder="", file_name=[]):

    st=0
    dict_ns_nr={}

    for ns in range(snd):
        for nr in range(rcv):
            dict_ns_nr[(ns+1,nr+1)]=[]
            for fl in range(nflw):

                #Open each file
                csvF= open(folder+"/"+file_name[st+fl], 'rb')

                # Read Lines axis[0]=time_snd and axis[1]=time_rcv
                axis =csvF.readlines()
                # print axis[0]

                axis_nr= [ float(val) for val in axis[1].split(',')]

                # print axis_nr
                dict_ns_nr[(ns+1,nr+1)].append(np.mean(axis_nr))

            st+=nflw

    # Order Keys:
    sort_dict = collections.OrderedDict(sorted(dict_ns_nr.items()))
    #print  "sorted_keys: ", sort_dict.keys()
    # print  "sorted_keys: ", sort_dict[(1,1)]

    return  sort_dict

def get_multiple_tests(args, n_tests, dict_tests):
        dict_ns_nr={}

        for test in range(n_tests):
            for nr in range(args.r):
                for ns in range(args.s):
                        if (ns+1,nr+1) not in dict_ns_nr.keys():
                            dict_ns_nr[(ns+1,nr+1)]= [dict_tests[test][(ns+1,nr+1)]]
                        else:
                            dict_ns_nr[(ns+1,nr+1)].append(dict_tests[test][(ns+1,nr+1)])

        for key in dict_ns_nr:

            dict_ns_nr[key] = list(np.mean(dict_ns_nr[key], axis=0))

        return dict_ns_nr

def get_dict_of_vals(args, test_name):

    dict_vals={}
    dict_tests={}
    n_tests=len(test_name)

    # Folder Names
    for num_test in range(n_tests):
        folder, file_names= get_file_names(test_name[num_test])
        print "\nNum of files: %i \ttest=%i" % (len(file_names), num_test+1)

        if (args.s * args.nflow * args.r) == len(file_names):

            # Dict Values:
            dict_vals = dict_values(args.s,args.r, args.nflow, folder, file_names)

            # Dict Diffent Test Cases:
            dict_tests[num_test] = collections.OrderedDict(sorted(dict_vals.items()))

        else:
            raise AssertionError("\num_snd (%i) * num_rcv(%i) * num_senders(%i) "
                                 "\n--> != num_files_names(%i)" %(args.s , args.nflow , args.r, len(file_names) ))

    if n_tests > 1:
        return get_multiple_tests(args, n_tests, dict_tests)
    
    else:
        return dict_vals

def plot_rcv(num_snd, num_rcv, dict_vals, args):

    if dict_vals == {}:
        raise AssertionError("\n--> Empty Dictionary")

    else:
        #Make Folder to save graphs:
        graphs=os.getcwd()+"/plots/"
        graphs_fol= graphs if os.path.exists(graphs) else os.mkdir(graphs)
        graphs_fol= graphs if not graphs_fol else graphs_fol

        # X-axis
        x_axis = list(range(1,args.nflow+1))
        xaxis_name = map(lambda x: str(x), x_axis)
        xaxis_name[0] = " TCP "
        labels = []


        for r in range(1,num_rcv+1):
            sum=0
            for s in range(1, num_snd + 1):
                plt.plot(x_axis, dict_vals[(s,r)])
                labels.append(r'$snd: %i$' % (s))
                #for flow in range(1,7):
                if s == args.s:
                    #print "VALUES-DICT (s,r)" , (s,r), "vals: ", str(map(lambda x: int(x), dict_vals[(s,r)]))
                    sum += np.sum(dict_vals[(s,r)])

            #print "sum rcv=" ,str(r), "sum=", str(sum)

            #Adjust plot legends
            if args.r == 2:
                XY= [0.47, 0.82] if r==2 else [0.45, 0.9]
                col = 3
            else: #default p=4
                XY= [0.95, 0.85] if r==1 else [0.28, 0.9]
                col = 1 if r==1 else 4


            plt.legend(labels, ncol=col, loc='center left',
                       bbox_to_anchor=[XY[0], XY[1]],
                       columnspacing=1.0, labelspacing=0.0,
                       handletextpad=0.0, handlelength=1.5,
                       fancybox=False, shadow=False)

            plt.xlabel('Number of Subflows')
            plt.ylabel('Time (sec)')
            plt.title('File Transfer Time with TCP & MPTCP' )
            plt.suptitle('Receiver: '+str(r+args.g), fontsize=12, fontweight='bold')
            plt.grid(True)
            plt.xticks(x_axis, xaxis_name)
            plt.savefig(graphs_fol+'rcv_'+str(r+args.g))
            plt.clf()
            #plt.show()

        return "\n** Plotting-Finished ** "

def main():

    try:

        # Parse args
        args = parse_args()
        print "\nNum of snd:  %i \nNum of rcv:  %i\nNum of flow: %i" %(args.s, args.r, args.nflow)

        # Get Test Name
        folder_path = get_test_folder(args)

        # Get Values from Dict
        dict_vals = get_dict_of_vals(args, folder_path)

        ## Plotting:
        plots= plot_rcv(args.s, args.r, dict_vals, args)

        print plots

    except ValueError:
        print "Error:" + str(ValueError)

if __name__ == '__main__':
    main()
