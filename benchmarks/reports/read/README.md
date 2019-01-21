# Cell element reports read benchmark code

This folder contains the benchmarking code for evaluating read performance
of SONATA cell element reports. These benchmarks are based on the C++
implementation of SONATA in (Brion)[https://github.com/BlueBrain/Brion).

## Setting up the environment

For reproducibility, the benchmarks rely on Nix for building the software
and its dependencies. The Nix recipes used are
(these ones)[https://github.com/BlueBrain/bbp-nixpkgs]. Assuming you have Nix
installed in your system, the steps for setting up the environment are the
following:

    git clone https://github.com/BlueBrain/bbp-nixpkgs
    cd bbp-nixpkgs
    git checkout b316d06
    . sourcethis.sh
    nix-build -A brion

## Running the benchmarks and plotting the results

Assuming the steps in the previous sections were successfully completed. You
just need to execute the `read_test.py` under each subdirectory. The scripts
assume that some report files exist and have been given some specific names.
Regretfully, this repository cannot contain the actual data for practical
reasons. Fake reports can be generated running ..., all the different
derived versions of these reports can be produced ...
