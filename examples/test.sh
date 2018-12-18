set -e

# A script to quickly check the standard examples, to make sure they run &
# produce expected output files


#######################################################################
assert_recently_edited_file ()               
{              
  file_name=$1

  echo "Checking whether this file recently changed: $file_name"

    if [ -f "$file_name" ]
    then
        echo "File $file_name has been found!"

        MAX_DIFF=3
        CURTIME=$(date +%s)
        LASTTIME=$(expr $CURTIME - $MAX_DIFF)

        FILETIME=$(stat $file_name -c %Y)

        # Check if file older
        if [ $LASTTIME -gt $FILETIME ]
        then
            echo "File $file_name has not been modified in past $MAX_DIFF seconds!"
            exit
        else
            echo "File $file_name recently modified..."
        fi

    else
        echo "$file_name not found in `pwd`!!"
        exit
    fi  

}    
#######################################################################


cd sim_tests/intfire/one_cell_iclamp/bmtk_build/
echo
echo "+++++++++++++++++++++++++++++++++++++++++++"
pwd
echo "+++++++++++++++++++++++++++++++++++++++++++"

python build_network.py
cd ../bmtk_test/
python ../../../shared_components/scripts/run_bionet.py NEST ../input/config.json
assert_recently_edited_file "output/spikes.h5"


cd ../../ten_cells_iclamp/bmtk_build/
echo
echo "+++++++++++++++++++++++++++++++++++++++++++"
pwd
echo "+++++++++++++++++++++++++++++++++++++++++++"

python build_network.py
cd ../bmtk_test/
python ../../../shared_components/scripts/run_bionet.py NEST ../input/config.json
assert_recently_edited_file "output/spikes.h5"


cd ../../../../9_cells/

echo
echo "+++++++++++++++++++++++++++++++++++++++++++"
pwd
echo "+++++++++++++++++++++++++++++++++++++++++++"

python build_network.py
python run_bionet.py
assert_recently_edited_file "output/spikes.h5"


cd ../5_cells_iclamp/
echo
echo "+++++++++++++++++++++++++++++++++++++++++++"
pwd
echo "+++++++++++++++++++++++++++++++++++++++++++"

python build_network.py
python run_bionet.py 
assert_recently_edited_file "output/spikes.h5"


cd ../300_intfire
echo
echo "+++++++++++++++++++++++++++++++++++++++++++"
pwd
echo "+++++++++++++++++++++++++++++++++++++++++++"

python build_network.py
python run_bionet.py 
assert_recently_edited_file "output/spikes.h5"


if [ "$1" = "-all" ]
then

cd ../300_cells
echo
echo "+++++++++++++++++++++++++++++++++++++++++++"
pwd
echo "+++++++++++++++++++++++++++++++++++++++++++"

python build_network.py
python run_bionet.py  

cd ..

else
    echo
    echo "   Skipping long simulations with a long generation/run time! Run this script with -all to include these!"
    echo
fi

echo "Done!!"