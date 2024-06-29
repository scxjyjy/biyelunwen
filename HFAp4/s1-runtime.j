{
  "target": "bmv2",
  "p4info": "build/calc.p4.p4info.txt",
  "bmv2_json": "build/calc.json",
  "table_entries": [
    {
      "table": "MyIngress.t_NFA_match_0",
      "match": {
        "meta.state": 0,
        "hdr.patrns[0].pattern": 97
      },
      "action_name": "MyIngress.push_Stack_1_member",
      "action_params": {
        "push_value1": 1
      }
    },
    {
      "table": "MyIngress.t_NFA_match_0",
      "match": {
        "meta.state": 1,
        "hdr.patrns[0].pattern": 98
      },
      "action_name": "MyIngress.a_mark_as_to_send_backend",
      "action_params": {}
    }
  ]
}
