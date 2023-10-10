/*********************  I N G R E S S   D E P A R S E R  ************************/
control IngressDeparser(packet_out pkt,
    /* User */
    inout my_ingress_headers_t                       hdr,
    in    my_ingress_metadata_t                      meta,
    /* Intrinsic */
    in    ingress_intrinsic_metadata_for_deparser_t  ig_dprsr_md)
{
    Digest<flow_digest_t>() new_flow_digest; 
    Digest<flow_digest_t>() new_long_flow_digest; 
    Digest<RTT_digest_t>()  rtt_sample_digest; 
    Digest<test_SEQ_t>()  test_SEQ; 
    Digest<queue_delay_sample_digest_t>()  queue_delay_sample_digest; 
    Digest<before_after_t>()  before_after; 
    Digest<flow_IP_t>()  IP_digest; 

    apply {
         /*
        if(ig_dprsr_md.digest_type == 2) {
            rtt_sample_digest.pack({hdr.ipv4.dst_addr, meta.rtt});  
        }
        */
        if(ig_dprsr_md.digest_type == 0) {
            new_flow_digest.pack({meta.flow_id, meta.rev_flow_id});
        } else if(ig_dprsr_md.digest_type == 1) {
            new_long_flow_digest.pack({meta.flow_id, meta.rev_flow_id});
        } else if(ig_dprsr_md.digest_type == 2) {
            rtt_sample_digest.pack({meta.flow_id, meta.rtt, hdr.ipv4.dst_addr});
            //rtt_sample_digest.pack({hdr.ipv4.dst_addr, meta.rtt});
        } else if(ig_dprsr_md.digest_type == 3) {
            test_SEQ.pack({hdr.tcp.seq_no, meta.lost});
        } else if(ig_dprsr_md.digest_type == 4) {
            before_after.pack({meta.total_before, meta.total_after});
        }
        pkt.emit(hdr);
    }
}

