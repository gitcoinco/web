CURRENT_ROUNDS=$(bash scripts/run_management_command.bash get_active_clrs mainnet all)
CALC_TYPES="slim
full"

# optional param - override calc types
if [ "$1" != "" ]; then
    CALC_TYPES="$1"
fi

for j in $(echo "$CALC_TYPES"); do
for i in $(echo "$CURRENT_ROUNDS"); do
    SCREEN_NAME="estimate_clr_for_${i}_mode_${j}"
    echo $i $j $SCREEN_NAME
    sleep 3
    screen -S $SCREEN_NAME -dm bash scripts/run_management_command_if_not_already_running.bash estimate_clr mainnet $i $j 2>&1 | tee -a /var/log/gitcoin/estimate_clr_$i_$j.log
done
sleep 60
done


