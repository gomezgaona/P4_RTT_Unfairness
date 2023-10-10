/***************** E G R E S S *********************/
control Egress(
    /* User */
    inout my_egress_headers_t                          hdr,
    inout my_egress_metadata_t                         meta,
    /* Intrinsic */
    in    egress_intrinsic_metadata_t                  eg_intr_md,
    in    egress_intrinsic_metadata_from_parser_t      eg_prsr_md,
    inout egress_intrinsic_metadata_for_deparser_t     eg_dprsr_md,
    inout egress_intrinsic_metadata_for_output_port_t  eg_oport_md)
{
	Hash<bit<16>>(HashAlgorithm_t.CRC16) hash;
    action apply_hash() {
        meta.flow_id = hash.get({
            hdr.ipv4.src_addr,
            hdr.ipv4.dst_addr,
            hdr.ipv4.protocol,
            hdr.tcp.src_port,
            hdr.tcp.dst_port
        });
    }
    table calc_flow_id {
        actions = {
            apply_hash;
        }
        const default_action = apply_hash();
    }
	
// ------------------------- QUEUE DELAY--------------------------------------
// ---------------------------------------------------------------------------
	Hash<bit<32>>(HashAlgorithm_t.CRC32) packet_hash;

    action apply_packet_hash() {
        meta.packet_hash = packet_hash.get({
            meta.flow_id,
			hdr.tcp.seq_no
        });
    }

    table calc_packet_hash {
        actions = {
            apply_packet_hash;
        }
        const default_action = apply_packet_hash();
    }

	Register<bit<32>, bit<17>>(100000) packets_timestamp;
    RegisterAction<bit<32>, bit<17>, bit<32>>(packets_timestamp) update_packets_timestamp = {
        void apply(inout bit<32> register_data) {
			//if(register_data == 0) {
				register_data = eg_prsr_md.global_tstamp[31:0];
			//}
		}
    };

    action exec_update_packets_timestamp(){
        update_packets_timestamp.execute(meta.packet_hash[16:0]);
    }

	RegisterAction<bit<32>, bit<17>, bit<32>>(packets_timestamp) calc_queue_delay_packet = {
        void apply(inout bit<32> register_data, out bit<32> result) {
            //result = eg_prsr_md.global_tstamp[30:15] - register_data;
			if(eg_prsr_md.global_tstamp[31:0] > register_data && eg_prsr_md.global_tstamp[31:0] - register_data < 200000000) {
				result = eg_prsr_md.global_tstamp[31:0] - register_data;
			} else {
				result = 0;
			}
        }
    };

    action exec_calc_queue_delay_packet(){
        meta.packet_queue_delay = calc_queue_delay_packet.execute(meta.packet_hash[16:0]);
    }
	
	// Averaging
	Lpf<value_t, bit<1>>(size=1) lpf_queue_delay_1;
	Lpf<value_t, bit<1>>(size=1) lpf_queue_delay_2;
	value_t lpf_queue_delay_input;
	value_t lpf_queue_delay_output_1;
	value_t lpf_queue_delay_output_2;
	
	Register<bit<32>, bit<1>>(1) queue_delays;
    RegisterAction<bit<32>, bit<1>, bit<32>>(queue_delays) update_queue_delays = {
        void apply(inout bit<32> register_data) {
            register_data = meta.packet_queue_delay;
        }
    };

    action exec_update_queue_delays(){
        update_queue_delays.execute(0);
    }

    apply {
		calc_flow_id.apply();
		calc_packet_hash.apply();
		if (hdr.tcp.in_port == 148) {
			exec_update_packets_timestamp();
		}
		else if(hdr.tcp.in_port == 140) {
			exec_calc_queue_delay_packet();
			if(meta.packet_queue_delay != 0) {
				lpf_queue_delay_input = (value_t)meta.packet_queue_delay;
				lpf_queue_delay_output_1 = lpf_queue_delay_1.execute(lpf_queue_delay_input, 0);
				lpf_queue_delay_output_2 = lpf_queue_delay_2.execute(lpf_queue_delay_output_1, 0);
				meta.packet_queue_delay = lpf_queue_delay_output_2;
				exec_update_queue_delays();
			}
		}
		eg_dprsr_md.drop_ctl = 0;
	
    }
}
