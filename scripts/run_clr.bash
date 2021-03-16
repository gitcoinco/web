CURRENT_ROUNDS=$(bash scripts/run_management_command.bash get_active_clrs mainnet all)
for i in $(echo "$CURRENT_ROUNDS"); do
    echo $i
    sleep 3
    screen -S estimate_clr_$i -dm bash scripts/run_management_command_if_not_already_running.bash estimate_clr mainnet $i 2>&1 | tee -a /var/log/gitcoin/estimate_clr_$i.log
    
done

