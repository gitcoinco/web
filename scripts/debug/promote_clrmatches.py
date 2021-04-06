from grants.models import *
from marketing.mails import grant_match_distribution_final_txn

round_number = 9
read_only = True
send_email = False
save_object = False

clrmatches_ready = CLRMatch.objects.filter(round_number=round_number, ready_for_test_payout=True, ready_for_payout=False)
clrmatches_notready = CLRMatch.objects.filter(round_number=round_number, ready_for_test_payout=False, ready_for_payout=False)
total_ready = sum(sm.amount for sm in clrmatches_ready)
total_notready = sum(sm.amount for sm in clrmatches_notready)

print("================================")
print("READY")
print(f"count: {clrmatches_ready.count()}")
print(f"amount: ${total_ready}")
print("================================")
print("NOTREADY")
print(f"count: {clrmatches_notready.count()}")
print(f"amount: ${total_notready}")

print("================================")
print("TOTAL")
print(f"count: {clrmatches_ready.count() + clrmatches_notready.count()}")
print(f"amount: ${total_notready + total_ready}")

#for clrm in clrmatches_ready:
#	if not read_only:
#		clrm.ready_for_payout = True
#		clrm.save()
#
#		if send_email:
#			grant_match_distribution_final_txn(clrm, True)
