#!/bin/bash

# Directory on OSC Pitzer containing SPEEDY data
src_dir=ens_data



# date
# echo EXTRACT DATA FOR EVERY OTHER DAY
# echo ""


# # Extract surface pressure data for every other day
# day_num=0
# nday_interval=2

# # Loop over all ensembles
# for ensname in reference_ens perturbed_ens; do

#     for fname in `ls --color=none ens_data/$ensname/data_raw/2011*.nc`; do

#         # Extract data
#         if (( day_num % nday_interval == 0 )); then
#             outfname=SPEEDY_ensemble_data/$ensname/data_raw/`basename $fname`
#             ncks -v ps $fname -4 -O -L 1 $outfname
#             echo Extracted   $fname   into   $outfname
#         fi

#         # Increment time counter
#         (( day_num++ ))

#     done
# done


# echo "" 



date
echo EXTRACT DATA FOR EVERY DAY IN FEB
echo ""

# Loop over all ensembles
for ensname in reference_ens perturbed_ens; do

    for fname in `ls --color=none ens_data/$ensname/data_raw/201102*.nc`; do

        # Extract data
        outfname=SPEEDY_ensemble_data/$ensname/data_raw/`basename $fname`

        # Skip if extraction already done
        if [[ ! -e $outfname ]]; then
            ncks -v ps $fname -4 -O -L 1 $outfname
            echo Extracted   $fname   into   $outfname
        fi

    done
done

echo ""
date 
echo FINISHED EXTRACTING ALL DATA