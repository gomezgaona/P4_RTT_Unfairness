/***************** I N G R E S S *********************/
control Ingress(
    /* User */
    inout my_ingress_headers_t                       hdr,
    inout my_ingress_metadata_t                      meta,
    /* Intrinsic */
    in    ingress_intrinsic_metadata_t               ig_intr_md,
    in    ingress_intrinsic_metadata_from_parser_t   ig_prsr_md,
    inout ingress_intrinsic_metadata_for_deparser_t  ig_dprsr_md,
    inout ingress_intrinsic_metadata_for_tm_t        ig_tm_md)
{

    Counter<bit<64>, bit<1>>(1, CounterType_t.BYTES) link_stats;

    DirectMeter(MeterType_t.BYTES)      bytes_meter;
    bit<2> color;
    bit<1> stored;

    Register<bit<1>, bit<16>>(65535) informed_long_flows;
    RegisterAction<bit<1>, bit<16>, bit<1>>(informed_long_flows) read_store_long_flow = {
        void apply(inout bit<1> register_data, out bit<1> result) {
             result = register_data;
             //register_data = 1;
        }
    };

    action apply_read_store_long_flow() {
        stored = read_store_long_flow.execute(meta.flow_id);
    }

    RegisterAction<bit<1>, bit<16>, bit<1>>(informed_long_flows) read_long_flow = {
        void apply(inout bit<1> register_data, out bit<1> result) {
             result = register_data;
             register_data = 0;
        }
    };

    action apply_read_long_flow() {
        stored = read_long_flow.execute(meta.flow_id);
    }
    
    // ***********************************************************************************************
    // *************************        H  A S H I N G       *****************************************
    // ***********************************************************************************************
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
	
	SKETCH_REGISTER(0);
    SKETCH_REGISTER(1);
    SKETCH_REGISTER(2);
    SKETCH_REGISTER(3);

    CRCPolynomial<bit<13>>( 0x04C11DB7, true, false, false, 13w0xFFFF, 13w0xFFFF) crc10d_1; 
    CRCPolynomial<bit<13>>( 0xEDB88320, true, false, false, 13w0xFFFF, 13w0xFFFF) crc10d_2; 
    CRCPolynomial<bit<13>>( 0x1A83398B, true, false, false, 13w0xFFFF, 13w0xFFFF) crc10d_3; 
    CRCPolynomial<bit<13>>( 0xabc14281, true, false, false, 13w0xFFFF, 13w0xFFFF) crc10d_4; 

    SKETCH_COUNT(0, HashAlgorithm_t.CUSTOM, crc10d_1)
    SKETCH_COUNT(1, HashAlgorithm_t.CUSTOM, crc10d_2)
    SKETCH_COUNT(2, HashAlgorithm_t.CUSTOM, crc10d_3)
    SKETCH_COUNT(3, HashAlgorithm_t.CUSTOM, crc10d_4)
	
	action meter(){
    }
	table counted_flow {
        key = {
            meta.flow_id: exact;
        }
        actions = {
            meter;
            NoAction;
        }
        size = 65535;
	    const default_action = NoAction;
        idle_timeout = true;
    }
	
	Hash<bit<16>>(HashAlgorithm_t.CRC16) rev_hash;
    action apply_rev_hash() {
        meta.rev_flow_id = rev_hash.get({
            hdr.ipv4.dst_addr,
            hdr.ipv4.src_addr,
            hdr.ipv4.protocol,
            hdr.tcp.dst_port,
            hdr.tcp.src_port
        });
    }
    table calc_rev_flow_id {
        actions = {
            apply_rev_hash;
        }
        const default_action = apply_rev_hash();
    }
    // ***********************************************************************************************
    // *************************     E N D   H  A S H I N G       ************************************
    // ***********************************************************************************************

    // ***********************************************************************************************
    // *************************     R T T       *****************************************************
    // ***********************************************************************************************
        action drop() {
            ig_dprsr_md.drop_ctl = 0x1; // Drop packet.
        }

        action nop() {
        }
       
        action route_to_64(){
            //route to CPU NIC. on tofino model, it is veth250
            ig_tm_md.ucast_egress_port=64;
        }
        
        action mark_SEQ(){
            meta.pkt_type=PKT_TYPE_SEQ;
        }

        action mark_ACK(){
            meta.pkt_type=PKT_TYPE_ACK;
        }

        action drop_and_exit(){
            drop();exit;
        }
        
        // Decide packet is a data packet or an ACK
        
        table tb_decide_packet_type {
            key = {
                hdr.tcp.flags: ternary;
                hdr.ipv4.total_len: range;
                //hdr.ipv4.dst_addr: lpm; //use IP address to decide inside/outside
            }
            actions = {
                mark_SEQ;
                mark_ACK;
                drop_and_exit;
            }
            default_action = mark_SEQ();
            size = 512;
            const entries = {
                (TCP_FLAGS_S,_): mark_SEQ();
                (TCP_FLAGS_S+TCP_FLAGS_A,_): mark_ACK();
                (TCP_FLAGS_A, 0..80 ): mark_ACK();
                (TCP_FLAGS_A+TCP_FLAGS_P, 0..80 ): mark_ACK();
                (_,100..1600): mark_SEQ();
                (TCP_FLAGS_R,_): drop_and_exit();
                (TCP_FLAGS_F,_): drop_and_exit();
            }
        }
        
        // Calculate the expected ACK number for a data packet.
        // Formula: expected ACK=SEQ+(ipv4.total_len - 4*ipv4.ihl - 4*tcp.data_offset)
        // For SYN/SYNACK packets, add 1 to e_ack
        
        Hash<bit<32>>(HashAlgorithm_t.IDENTITY) copy32_1;
        Hash<bit<32>>(HashAlgorithm_t.IDENTITY) copy32_2;
        action compute_eack_1_(){
            meta.tmp_1=copy32_1.get({26w0 ++ hdr.ipv4.ihl ++ 2w0});
        }

        action compute_eack_2_(){
            meta.tmp_2=copy32_2.get({26w0 ++ hdr.tcp.data_offset ++ 2w0});
        }

        action compute_eack_3_(){
            meta.tmp_3=16w0 ++ hdr.ipv4.total_len;
        }

        action compute_eack_4_(){
            meta.total_hdr_len_bytes=(meta.tmp_1+meta.tmp_2);
        }

        action compute_eack_5_(){
            meta.total_body_len_bytes=meta.tmp_3 - meta.total_hdr_len_bytes;
        }

        action compute_eack_6_(){
            meta.expected_ack=hdr.tcp.seq_no + meta.total_body_len_bytes;
        }
        
        action compute_eack_last_if_syn(){
            meta.expected_ack=meta.expected_ack + 1;
            // could save 1 stage here by folding this into "++ 2w0" as "++ 2w1"
        }
        
        // Calculate 32-bit packet signature, to be stored into hash tables
        
        Hash<bit<32>>(HashAlgorithm_t.CRC32) crc32_1;
        Hash<bit<32>>(HashAlgorithm_t.CRC32) crc32_2;
        action get_pkt_signature_SEQ(){
            meta.pkt_signature=crc32_1.get({
                hdr.ipv4.src_addr, hdr.ipv4.dst_addr,
                hdr.tcp.src_port, hdr.tcp.dst_port,
                meta.expected_ack
            });
        }

        action get_pkt_signature_ACK(){
            meta.pkt_signature=crc32_2.get({
                hdr.ipv4.dst_addr,hdr.ipv4.src_addr, 
                hdr.tcp.dst_port,hdr.tcp.src_port, 
                hdr.tcp.ack_no
            });
        }
        
        // Calculate 16-bit hash table index
        Hash<bit<16>>(HashAlgorithm_t.CRC16) crc16_1;
        Hash<bit<16>>(HashAlgorithm_t.CRC16) crc16_2;
        action get_location_SEQ(){
            meta.hashed_location_1=crc16_1.get({
                //4w0,
                hdr.ipv4.src_addr, hdr.ipv4.dst_addr,
                hdr.tcp.src_port, hdr.tcp.dst_port,
                meta.expected_ack//,
                //4w0
            });
        }

        action get_location_ACK(){
            meta.hashed_location_1=crc16_2.get({
                //4w0,
                hdr.ipv4.dst_addr,hdr.ipv4.src_addr, 
                hdr.tcp.dst_port,hdr.tcp.src_port, 
                hdr.tcp.ack_no//,
                //4w0
            });
        }
        
        // Self-expiry hash table, each entry stores a signature and a timestamp
        
        #define TIMESTAMP ig_intr_md.ingress_mac_tstamp[31:0]
        #define TS_EXPIRE_THRESHOLD (50*1000*1000)
        //50ms
        #define TS_LEGITIMATE_THRESHOLD (2000*1000*1000)
        
        
        Register<paired_32bit,_>(32w65536) reg_table_1;
        //lo:signature, hi:timestamp
        
        RegisterAction<paired_32bit, _, bit<32>>(reg_table_1) table_1_insert= {  
            void apply(inout paired_32bit value, out bit<32> rv) {          
                rv = 0;                                                    
                paired_32bit in_value;                                          
                in_value = value;                 
                
                bool existing_timestamp_is_old = (TIMESTAMP-in_value.hi)>TS_EXPIRE_THRESHOLD;
                bool current_entry_empty = in_value.lo==0;
                
                if(existing_timestamp_is_old || current_entry_empty)
                {
                    value.lo=meta.pkt_signature;
                    value.hi=TIMESTAMP;
                    rv=1;
                }
            }                                                              
        };
        
        action exec_table_1_insert(){
            meta.table_1_read=table_1_insert.execute(meta.hashed_location_1);
        }
        
        RegisterAction<paired_32bit, _, bit<32>>(reg_table_1) table_1_tryRead= {  
            void apply(inout paired_32bit value, out bit<32> rv) {    
                rv=0;
                paired_32bit in_value;                                          
                in_value = value;     
                
                #define current_entry_matched (in_value.lo==meta.pkt_signature)
                #define timestamp_legitimate  ((TIMESTAMP-in_value.hi)<TS_LEGITIMATE_THRESHOLD)
                
                if(current_entry_matched && timestamp_legitimate)
                {
                    value.lo=0;
                    value.hi=0;
                    rv=in_value.hi;
                }
            }                                                              
        };
        
        action exec_table_1_tryRead(){
            meta.table_1_read=table_1_tryRead.execute(meta.hashed_location_1);
        }
    // ***********************************************************************************************
    // *************************     E N D   R T T       *********************************************
    // ***********************************************************************************************



    // ***********************************************************************************************
    // *************************        M E T E R I N G      *****************************************
    // ***********************************************************************************************
    action do_meter() {
        color = (bit<2>) bytes_meter.execute();  // Default color coding: 0 - Green,            1 - Yellow,            3- Red 
    }

    action inform_control_plane() {
        color = (bit<2>) bytes_meter.execute();
        ig_dprsr_md.digest_type=0;
    }
    //@idletime_precision(6)
    table metering {
       key = { meta.flow_id : exact; }
        actions = {
            do_meter;
            inform_control_plane;
        }
		size = 24000;
        meters = bytes_meter;
	    const default_action = inform_control_plane;
        idle_timeout         = true;
    }

    action route_to_CPU() {
	    ig_tm_md.ucast_egress_port=192;
    }

    table store_and_check_if_long_flow_informed {
        actions = {apply_read_store_long_flow;}
        const default_action = apply_read_store_long_flow;
    }

    table check_if_long_flow {
        actions = {apply_read_long_flow;}
        const default_action = apply_read_long_flow;
    }

    // ***********************************************************************************************
    // *************************  E N D   M E T E R I N G      ***************************************
    // ***********************************************************************************************
    Register<bit<32>, bit<16>>(65535) last_seq;
    RegisterAction<bit<32>, bit<16>, bit<32>>(last_seq) read_store_last_seq = {
        void apply(inout bit<32> register_data, out bit<32> result) {
            //if(meta.expected_ack != 0){
			if(hdr.tcp.seq_no + 65535 < register_data) {
				register_data = meta.expected_ack;
			}
			
			if(hdr.tcp.seq_no < register_data ) {
				result = register_data;
			} else
			{
				register_data = meta.expected_ack;
			}
			
        }
    };

    action exec_read_store_last_seq(){
        meta.lost=read_store_last_seq.execute(meta.flow_id);
    }

    Register<bit<32>, bit<1>>(1) total_retr;
    RegisterAction<bit<32>, bit<1>, bit<1>>(total_retr) update_total_retr = {
        void apply(inout bit<32> register_data) {
            if(meta.lost != 0) {
                register_data = register_data + 1;
            }
        }
    };

    action exec_update_total_retr(){
        update_total_retr.execute(0);
	}

    Register<bit<32>, bit<1>>(32) total_sent;
    RegisterAction<bit<32>, bit<1>, bit<32>>(total_sent) update_total_sent = {
        void apply(inout bit<32> register_data) {
            register_data = register_data + 1;
        }
    };

    action exec_update_total_sent(){
        update_total_sent.execute(0);
    }
	

	
	Register<bit<32>, bit<1>>(1) total_sent_before;
    RegisterAction<bit<32>, bit<1>, bit<32>>(total_sent_before) update_total_sent_before = {
        void apply(inout bit<32> register_data, out bit<32> result) {
			register_data = register_data + 1;
			result = register_data;
        }
    };

    action exec_update_total_sent_before(){
        meta.total_before = update_total_sent_before.execute(0);
    }
	
	Register<bit<32>, bit<1>>(1) total_sent_after;
    RegisterAction<bit<32>, bit<1>, bit<32>>(total_sent_after) update_total_sent_after = {
        void apply(inout bit<32> register_data, out bit<32> result) {
            register_data = register_data + 1;
			result = register_data;
        }
    };

    action exec_update_total_sent_after(){
        meta.total_after = update_total_sent_after.execute(0);
    }
	RegisterAction<bit<32>, bit<1>, bit<32>>(total_sent_before) read_total_sent_before = {
        void apply(inout bit<32> register_data, out bit<32> result) {
			result = register_data;
        }
    };

    action exec_read_total_sent_before(){
        meta.total_before = read_total_sent_before.execute(0);
    }
	
	Register<bit<32>, bit<1>>(1) report_reg;
    RegisterAction<bit<32>, bit<1>, bit<32>>(report_reg) update_report_reg = {
        void apply(inout bit<32> register_data, out bit<32> result) {
            if(register_data == 1000) {
				register_data = 0;
			} else {
				register_data = register_data + 1;
			}
			result = register_data;
        }
    };

    action exec_update_report_reg(){
        meta.report_loss = update_report_reg.execute(0);
		
    }
	
	
	Register<bit<32>, bit<1>>(1) last_report_timestamp;
	RegisterAction<bit<32>, bit<1>, bit<9>>(last_report_timestamp) update_last_report_timestamp = {
        void apply(inout bit<32> register_data, out bit<9> result) {
			 //if (ig_intr_md.ingress_mac_tstamp[31:0] - register_data > 1000000000) {
				register_data = ig_intr_md.ingress_mac_tstamp[31:0];
				result = 192;
			 //}
		}
    };

	action apply_update_last_report_timestamp() {
        ig_tm_md.ucast_egress_port = update_last_report_timestamp.execute(0);
    }

    Hash<bit<16>>(HashAlgorithm_t.CRC16) hash_udp;
    action apply_hash_udp() {
        meta.flow_id = hash_udp.get({
            //hdr.ipv4.src_addr,
            //hdr.ipv4.dst_addr,
            //hdr.ipv4.protocol,
            //hdr.udp.src_port
            //hdr.udp.dst_port,
			hdr.rtp.SSRC
			//hdr.rtp.sequence_number
        });
    }

    table calc_flow_id_udp {
        actions = {
            apply_hash_udp;
        }
        default_action = apply_hash_udp();
    }

    bit<32> result_sample;
	
	Register<bit<32>, bit<16>>(65535) last_timestamp;
	
	RegisterAction<bit<32>, bit<16>, bit<32>>(last_timestamp) update_last_timestamp = {
        void apply(inout bit<32> register_data) {
			register_data = ig_intr_md.ingress_mac_tstamp[31:0]; //[41:10];
		}
    };

	action apply_update_last_timestamp() {
        update_last_timestamp.execute(meta.flow_id);
    }

	RegisterAction<bit<32>, bit<16>, bit<32>>(last_timestamp) get_and_reset_timestamp = {
        void apply(inout bit<32> register_data, out bit<32> result) {
			if(register_data != 0){
				result = ig_intr_md.ingress_mac_tstamp[31:0] - register_data;
			} else {
				result = 111;
			}
			register_data = ig_intr_md.ingress_mac_tstamp[31:0];
			/*
			if(register_data == 0)  { 
                    register_data = ig_intr_md.ingress_mac_tstamp[31:0];
                    result = 111;
            } else if(ig_intr_md.ingress_mac_tstamp[31:0] > register_data && register_data != 0) { //[41:10];
				    result = ig_intr_md.ingress_mac_tstamp[31:0] - register_data;
            } 
			*/
				
		}
    };
	action apply_get_and_reset_timestamp() {
        result_sample = get_and_reset_timestamp.execute(meta.flow_id);
    }

    apply {
		
		hdr.tcp.in_port = ig_intr_md.ingress_port;
		
		if(ig_intr_md.ingress_port == 148) {
			exec_update_total_sent_before();
			
		} else if (ig_intr_md.ingress_port == 140) {
			exec_update_total_sent_after();
			exec_read_total_sent_before();
		} 
			
		//apply_update_last_report_timestamp();

		//route_to_CPU();
		if(ig_intr_md.ingress_port == 140) {
			exec_update_report_reg();
            //ig_dprsr_md.digest_type = 5;
			//exec_read_total_sent_after();
			

		}

        if(hdr.ipv4.isValid() && hdr.tcp.isValid() && ig_intr_md.ingress_port != 148){ // && ig_intr_md.ingress_port != 156 ) {
			
			calc_flow_id.apply();
			calc_rev_flow_id.apply();
			
			apply_hash_0();
            apply_hash_1();
            apply_hash_2();
            apply_hash_3();

			exec_read_sketch0();
            exec_read_sketch1();
            exec_read_sketch2();
            exec_read_sketch3();
			
			if(counted_flow.apply().miss){
                if(ig_intr_md.ingress_port != 132 && meta.value_sketch0 == 1 && meta.value_sketch1 == 1 && meta.value_sketch2 == 1  && meta.value_sketch3 == 1) {
                    ig_dprsr_md.digest_type = 1;  
                }
            }
			/*
            if (metering.apply().hit) {                            // Get the color (green, yellow, red), or inform the control plane about a new flow joined
                if (color == 3) {                                    // We have a long flow
                    store_and_check_if_long_flow_informed.apply();     // Store long flow / check if we informed the control plane that this flow is RED (this is important so that we don't flood the control plane) 
                    if (stored == 0) {
                        ig_dprsr_md.digest_type=1;
                    }
                }
            }
			*/

                // RTT calculation
                tb_decide_packet_type.apply();
                    
                // compute e_ack
                if(meta.pkt_type==PKT_TYPE_SEQ){
                    compute_eack_1_();
                    compute_eack_2_();
                    compute_eack_3_();
                    compute_eack_4_();
                    compute_eack_5_();
                    compute_eack_6_();
					//exec_read_store_last_seq();
                    if(hdr.tcp.flags==TCP_FLAGS_S){
                        compute_eack_last_if_syn();
                    } else {
						//if(meta.total_body_len_bytes > 0) {
                        exec_read_store_last_seq();
						//}
						if(meta.lost != 0) {
							ig_dprsr_md.digest_type = 3;
						}	
                    }
                }

                //get signature (after having eack)
        
                if(meta.pkt_type==PKT_TYPE_SEQ){
                    
                    get_pkt_signature_SEQ();
                    get_location_SEQ();
                }else{
                    get_pkt_signature_ACK();
                    get_location_ACK();
                }
                
                // insert into table if syn
                // read from table if ack
                
                // Insert or Read from hash table
                if(meta.pkt_type==PKT_TYPE_SEQ){
                    exec_table_1_insert();
					if(meta.report_loss == 1000) {
						ig_dprsr_md.digest_type = 4;
					}
                }else{
                    exec_table_1_tryRead();
                }
              
                // send out report headers.
                if(meta.pkt_type==PKT_TYPE_SEQ){
                    exec_update_total_retr();
                }else{
                    if(meta.table_1_read==0){
                        meta.rtt=0;                        
                    }else{
                        meta.rtt = (TIMESTAMP-meta.table_1_read);
                        ig_dprsr_md.digest_type = 2;
                    }
                }

				exec_update_total_sent();
				//ig_dprsr_md.digest_type = 3;
            
            link_stats.count(0);
			
        } else if(hdr.ipv4.isValid() && hdr.udp.isValid()) {
			calc_flow_id_udp.apply();
			//meta.flow_id = 0; //hdr.rtp.sequence_number;
			if (ig_intr_md.ingress_port == 140) {
				apply_get_and_reset_timestamp();
				hdr.rtp.timestamp = result_sample;
				ig_tm_md.ucast_egress_port=192;
			}
		}
		
		if(ig_tm_md.ucast_egress_port != 192) {
			ig_tm_md.ucast_egress_port=148; // just to go to egress
            //ig_dprsr_md.digest_type = 5;
		}
		
    }

}
//To do: Identify the event that will trigger sending digest 5
//47 bits or bytes?
//Identify the variable of the IP in the control plane