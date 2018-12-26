{% for host in groups['appformix_mongo_replica_slaves'] %}
  rs.add("{{ host }}:{{ appformix_mongo_replica_exposed_port }}")
  sleep(5000)
{% endfor %}
printjson(rs.status())
