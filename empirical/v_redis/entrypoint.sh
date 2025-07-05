#! bin/bash 

echo "sysctl command is setting.."
sysctl vm.overcommit_memory=1

echo "sysctl command has set"

echo "Starting redis server"
redis-server --appendonly yes

echo "Redis-server is up"


