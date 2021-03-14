CURRENT_ROUNDS=$(bash scripts/run_management_command.bash get_active_clrs mainnet all)
for i in $(echo "$CURRENT_ROUNDS"); do
    echo $i
    LOGPATH="/var/log/gitcoin/estimate_clr_$i.log"
    bash scripts/run_management_command_if_not_already_running.bash estimate_clr mainnet $i >> $LOGPATH 2>&1 &

    # TODO: move to a screen perheps, per https://superuser.com/questions/454907/how-to-execute-a-command-in-screen-and-detach
    # a la
    # screen -S sleepy -dm sleep 60

done

