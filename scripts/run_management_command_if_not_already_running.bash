IS_ALREADY_RUNNING=$(pgrep -fl $1 | grep python | wc -l)
if [ "$IS_ALREADY_RUNNING" -eq "0" ]; then
    bash scripts/run_management_command.bash $1 $2 $3 $4 $5 $6 $7 $8 $9
fi
