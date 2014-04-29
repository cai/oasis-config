1. Input file details:
## Set the list of stripe counts we want to test.
ost_stripe_list 1 4 16

## Set the list of core counts we want to test.
core_list 16 32 64 128

## Set the maximum core limit
client_core_limit 8

## Set the number of unique hosts in the host file.
numhosts 16

## Size of write from each client node
client_wsize_gb 48

## Number of Iterations
iterations 1

## Host file with the unique list of hosts
client_hostlist_file /1b/diag/test/h1

## Test directory (make sure this exists and the script must be run from there)
testdir /1b/diag/test/test

## mpirun command (could be different on Trestles)
runmpi mpirun

2. Interactively on Triton:

cd /1b/diag/test/test
nohup ../IOR_Test_Load.py ../Input_Test_Load.txt > test.log&
  
3. Run scripts [coming soon for Trestles]
