
#rtt_separation.p4
compile:
	cd /root/bf-sde-9.4.0/ ; sh . ../tools/./set_sde.bash
	~/tools/p4_build.sh --with-p4c=bf-p4c /root/rtt_separation/p4src/rtt_unfairness.p4

run:
	pkill switchd 2> /dev/null ; cd /root/bf-sde-9.4.0/ ;./run_switchd.sh -p rtt_unfairness

conf_links:
	cd /root/bf-sde-9.4.0/ ; ./run_bfshell.sh --no-status-srv -f /root/rtt_separation/ucli_cmds

start_control_plane_measurements:
	/root/bf-sde-9.4.0/./run_bfshell.sh --no-status-srv -i -b /root/rtt_separation/bfrt_python/control_plane.py

