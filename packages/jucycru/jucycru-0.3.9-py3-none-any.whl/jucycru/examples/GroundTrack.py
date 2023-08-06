#!/usr/bin/env python

"""
This example produces the ground track of JUICE for a given planet during the time
window specified by start_time and end_time.

For this script to run you should ensure you have the following packages installed:

    math | numpy | spiceypy | matplotlib | jucycru

To install jucycru use the following command:

    pip install jucycru

And all dependencies will be installed.

You must set kpath to the absolute path to the kernel folder for the relevant mission
(in this case JUICE).

This example uses the latest mk file (juice_crema_3_2_v160.tm). This can be changed
to older version by setting crema to the crema version i.e. 3_0 and the
crema_version to the version of the mk spice file i.e. v152.

The start_time and end_time can be any date in the form of the string as long as
there is sufficient ephemeris data for the spacecraft and bodies loaded within the
metakernel.

The main_body can be changed to other solar system bodies and will be used as the
central object for any plots the be produced [A background image must also be
available in the directory jucycru/surfaces/ as a .png or .jpg].

The resolution is the step size in the time array; for smaller time windows it
is best to use a smaller resolution (for large time windows and small resolution
the computation time will be longer).

"""

import jucycru as jc
import spiceypy as spice

# REQUIRED INPUTS
start_time = '2026 Nov 25 13:00:00'
end_time = '2026 Nov 26 13:00:00'
crema = '3_2'
crema_version = 'v160'
main_body = 'Earth'

# CHANGE THIS TO PATH/TO/KERNELS FOLDER
kpath = '/Applications/cosmographia/Missions/spicekernels/JUICE/'

# RECOMMENDED INPUT
res = 300

# DEFAULT INPUTS
spacecraft = 'JUICE'

# CONFIGURE KERNEL POOL
mkpath = 'mk/juice_crema_'
kfurnsh = kpath + mkpath + crema + '_' + crema_version + '.tm'
spice.furnsh(kfurnsh)

# COMPUTE GROUND TRACK
[longitude, latitude, distance] = jc.groundTrack(main_body,
                                                 spacecraft,
                                                 start_time,
                                                 end_time,
                                                 res)

# PLOT GROUND TRACK
jc.plotGT(longitude, latitude, distance, main_body)
