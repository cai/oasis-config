#!/usr/bin/python

"""
Program to test SSD performace for a multiple conditions

Loop over RAID stripe size
   Loop over number of drives in RAID
      * Create RAID device w/ given stripe size and drive count
      Loop over filesystem options (on/off)
        * Optionally create file system
        * Set target for xdd
        Loop over read ahead options (on/off)
           Loop over IO scheduler options
              * Fill the file
              Loop over sequential thread counts
                 * Perform sequential read test
                 * Perform sequential write test
              Loop over random thread counts
                 * Perform random read test
                 * Perform random write test
        * Remove file system if one had been created
      * Remove RAID device
"""

import sys
import string
import subprocess
import os

id = 0 # Counter to keep track of XDD run number

def mk_iorcmd(precmd, client_wsize_gb, testdir1, hostfile, icorel, corelimit, iterations,numhosts):
    """Create IOR command from base command and parameters"""
    icphost = int(icorel)/int(numhosts)
    igig = int(client_wsize_gb)/int(icphost)
    filen = "htemp"+str(icphost)
    for iloop in range(1,icphost+1):
     if iloop == 1:
      cmd1 = "cat " + hostfile + " > " + filen
     else:
      cmd1 = "cat " + hostfile + " >> " + filen
     output = subprocess.Popen(cmd1,stdout=subprocess.PIPE,shell=True).communicate()[0]
    cmd1 = "sort " + filen + " > ftemp"
    output = subprocess.Popen(cmd1,stdout=subprocess.PIPE,shell=True).communicate()[0]
    cmd1 = "mv ftemp " + filen
    output = subprocess.Popen(cmd1,stdout=subprocess.PIPE,shell=True).communicate()[0]
    iorcmd  = precmd + " -hostfile " + filen 
    iorcmd += " -np " + str(icorel)
    iorcmd += " ../IOR-exe -a POSIX -b " + str(igig) + "g -F -t 1m -i " + str(iterations)
    iorcmd += " -o " + testdir1 + "/file >> IOR_test.out"
    return iorcmd

def cross(*args):
    """Create tuples from outer product of arbitrary number of lists"""
    ans = [[]]
    for arg in args:
        ans = [x+[y] for x in ans for y in arg]
    return ans

def runcmd(cmd1):
    # --- Remember to enable actual running of command
    print(cmd1)
    output = subprocess.Popen(cmd1, stdout=subprocess.PIPE,shell=True).communicate()[0]
#    print(output.strip())

# ------ end function definitions ------
    
# Define keywords - list_keys are for options that have multiple
# values (e.g. things that we want to iterate over), scalar_keys are
# for things that take a single value

list_keys =   ["ost_stripe_list","core_list"]
scalar_keys = ["client_core_limit","client_hostlist_file", 
               "testdir", "runmpi", "iterations","numhosts","client_wsize_gb"]

# Assign default values to the xdd dict (xddd)
xddd = {"client_core_limit":"1", 
        "iterations":"2","client_ost_limit":"1"}

# Parse the input file
f = open(sys.argv[1], "r")
lines = f.readlines()
f.close()
for line in lines:
    sline = line.strip().lower()
    if sline:
        p = string.split(sline)
        if(p[0] in list_keys):
            xddd[p[0]] = p[1:]
        elif(p[0] in scalar_keys):
            xddd[p[0]] = p[1]
        else:
            print("# Warning - invalid keyword %s" % p[0])

# Make sure that all necessary values are assigned
missing = []
for k in scalar_keys+list_keys:
    if k not in xddd:
        missing.append(k)
if missing:
    print("Input file is incomplete - missing following specifications:\n")
    for k in missing:
        print(k)
    print("\nExiting Lustre IOR testing script")
    sys.exit()

# Print out summary of I/O tests to be done
print("\n# Running IOR with following parameters")
for k in scalar_keys:
    print("#  %s: %s" % (k, xddd[k]))
print("# -----------------")
for k in list_keys:
    params = ' '.join(xddd[k])
    print("#  %s: %s" % (k, params))
print("")

# Create IOR base command containing all of the common options
ior_1st  = xddd["runmpi"] 
ior_last = xddd["iterations"]

# IOR TESTS
# Light
for islist in xddd["ost_stripe_list"]:
 print("Stripe used: ", islist)
 run1 = "/opt/lustre/bin/lfs setstripe -c " + islist
 run1 += " -s 1m " + xddd["testdir"]
 runcmd(run1)
 for icore in xddd["core_list"]:
  run2 = mk_iorcmd(ior_1st,xddd["client_wsize_gb"],xddd["testdir"],xddd["client_hostlist_file"],icore,xddd["client_core_limit"], ior_last, xddd["numhosts"])
  runcmd(run2)
  continue
 continue
# Medium

# Heavy
