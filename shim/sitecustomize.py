# scikit-rf 2.x moved connect() out of the top-level namespace.
# Palace's combine_extend_snp.py (line 230) still expects the 1.x API.
import skrf
if not hasattr(skrf, "connect"):
 from skrf.network import connect, innerconnect
 skrf.connect = connect
 skrf.innerconnect = innerconnect
