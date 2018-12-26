{% for host in groups['appformix_mongo_replica_master'] %}
  sh.addShard("{{ appformix_mongo_replica_set_name }}/{{ host }}:{{ appformix_mongo_replica_exposed_port }}")
  sleep(5000)
{% endfor %}
printjson(sh.status())
