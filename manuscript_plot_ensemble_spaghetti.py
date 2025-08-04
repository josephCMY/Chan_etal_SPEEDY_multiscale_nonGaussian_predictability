
'''
    Load packages
'''
from datetime import datetime, timedelta
import numpy as np
from netCDF4 import Dataset as ncopen
from matplotlib import use as mpl_use
mpl_use('agg')
import matplotlib.pyplot as plt
from copy import deepcopy
from matplotlib import ticker
from gc import collect as gc_collect
import pickle



'''
    User settings
'''
# Start and end dates
date_st = datetime(year=2011, month=1, day=1)
date_ed = datetime(year=2011, month=7, day=1)

# Time interval between simulation outputs
time_int = timedelta( days=1 )

# Path to SPEEDY reference ensemble and perturbed ensemble
path_reference_ens_dir = '/fs/ess/PAS2856/SPEEDY_ensemble_data/reference_ens/data_raw'
path_perturbed_ens_dir = '/fs/ess/PAS2856/SPEEDY_ensemble_data/perturbed_ens/data_raw'

# Typical date formatting
date_fmt = '%Y%m%d%H%M'

# Latitude to make plots for (50.1 deg N)
lat_list = np.linspace(-87.21645, 87.21645, 48)
targ_lat_ind=37

# Contur level to plot
pres_val = 5 # hPa perturbation from reference state

# Ensembel size
ens_size = 1000

# flag to do big data load
load_data_flag = False


'''
    Generate information about dates to plot
'''
# Generate list of date
date_list = []
date_nw = deepcopy( date_st )
while ( date_nw <= date_ed ):
    date_list.append(date_nw)
    date_nw += time_int
# --- End of loop over dates

# Number of dates
n_dates = len(date_list)





'''
    Loading ensemble mean surface pressure from first time point to act as "reference"
'''
# Generate path to file
fname = date_st.strftime( '%s/%s.nc' % (path_reference_ens_dir, date_fmt) )

# Load file
ncfile = ncopen( fname, 'r' )

# Extract first time point's ensemble mean
ref_ps_state = np.mean( np.squeeze( ncfile.variables['ps'] ), axis=0 )

# Extract lat and lon for completeness
lat1d = np.squeeze( ncfile.variables['lat'] )
lon1d = np.squeeze( ncfile.variables['lon'] )

# Close file for hygiene
ncfile.close()






'''
    Loop over dates and generate one plot per date. Will purge data over time to improve data usage
'''

if load_data_flag:
    # Dictionary to hold data 
    agg_data_dict = {}
    agg_data_dict['ref'] = np.zeros( [n_dates, ens_size, len(lon1d)])
    agg_data_dict['prt'] = np.zeros( [n_dates, ens_size, len(lon1d)])

    # Loop over dates
    for idate, date_nw in enumerate( date_list ):

        # Load surface pressure from reference ensemble
        ref_fname = date_nw.strftime( '%s/%s.nc' % (path_reference_ens_dir, date_fmt) )
        ref_ncfile = ncopen( ref_fname, 'r' )
        ref_ps_ens = (np.squeeze( ref_ncfile.variables['ps'] ) - ref_ps_state) / 100 # Convert from Pa to hPa
        ref_ens_avg = np.mean( ref_ps_ens, axis=0)
        ref_ncfile.close()

        # Load surface pressure from perturbed ensemble
        ptb_fname = date_nw.strftime( '%s/%s.nc' % (path_perturbed_ens_dir, date_fmt) )
        ptb_ncfile = ncopen( ptb_fname, 'r' )
        ptb_ps_ens = (np.squeeze( ptb_ncfile.variables['ps'] ) - ref_ps_state) / 100 # Convert from Pa to hPa
        ptb_ncfile.close()

        # Subset to desired latitude ring
        agg_data_dict['ref'][idate,:,:] = ref_ps_ens[:,targ_lat_ind,:]
        agg_data_dict['prt'][idate,:,:] = ptb_ps_ens[:,targ_lat_ind,:]

        # Purge data if needed
        if idate > 0 and idate % 10 == 0:
            gc_collect()

        print( 'loaded data for ' + date_nw.strftime(date_fmt))
    # --- End of loop over dates

    # Save data
    with open( 'surf_pres_spaghetti.pkl', 'wb') as f:
        pickle.dump( agg_data_dict, f)

else:
    # Load data
    with open( 'surf_pres_spaghetti.pkl', 'rb') as f:
        agg_data_dict = pickle.load( f )




'''
    Spaghetti plot!
'''
# Generate reference state to remove terrain
ref_ps = np.mean( agg_data_dict['ref'], axis = 1)  #np.mean( np.mean( agg_data_dict['ref'], axis=0), axis=0 )
for imem in range( ens_size ):
    agg_data_dict['ref'][:,imem,:] -= ref_ps
    agg_data_dict['prt'][:,imem,:] -= ref_ps


fig, axs = plt.subplots( nrows=1, ncols=2, figsize = (8,8))

for imem in range( 1000 ):
    axs[0].contour( lon1d, date_list, agg_data_dict['ref'][:,imem,:], [10], colors=['k'], alpha=0.02 )
    axs[1].contour( lon1d, date_list, agg_data_dict['prt'][:,imem,:], [10], colors=['k'], alpha=0.02 )

plt.tight_layout()
plt.savefig('test.png', dpi=200)