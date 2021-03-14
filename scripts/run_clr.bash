CURRENT_ROUNDS=$(bash scripts/run_management_command.bash get_active_clrs mainnet all)
for i in $(echo "$CURRENT_ROUNDS"); do
    echo $i
    LOGPATH="/var/log/gitcoin/estimate_clr_$i.log"
    bash scripts/run_management_command_if_not_already_running.bash estimate_clr mainnet $i >> LOGPATH &
done
