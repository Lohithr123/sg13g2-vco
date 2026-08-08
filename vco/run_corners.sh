#!/bin/bash
# Run the VCO netlist across process corners.
#
# ngspice resolves .lib at parse time, so one netlist cannot sweep corners in a
# single pass. This rewrites the three .lib lines, runs, and collects results.

cd /foss/designs/vco
M=/foss/pdks/ihp-sg13g2/libs.tech/ngspice/models

run() {   # $1=hbt corner  $2=mos corner  $3=label
  sed -e "s|cornerHBT.lib .*|cornerHBT.lib $1|" \
      -e "s|cornerMOSlv.lib .*|cornerMOSlv.lib $2|" \
      -e "s|cornerMOShv.lib .*|cornerMOShv.lib $2|" \
      vco_corners.spice > _corner_run.spice
  echo "=== $3  ($1 / $2) ==="
  ngspice _corner_run.spice 2>&1 | grep -E "^ta |^tb |^vx |^vn |failed"
  echo ""
}

run hbt_typ mos_tt "TYPICAL"
run hbt_wcs mos_ss "WORST   <- startup dies here first if anywhere"
run hbt_bcs mos_ff "BEST    <- highest frequency, check for clipping"
run hbt_wcs mos_ff "slow devices, fast switches"
run hbt_bcs mos_ss "fast devices, lossy switches"

rm -f _corner_run.spice
