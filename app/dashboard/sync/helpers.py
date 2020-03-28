from dashboard.models import BountyFulfillment


def txn_already_used(txn, token_name):
    return BountyFulfillment.objects.filter(
        payout_tx_id = txn,
        token_name=token_name
    ).exists()
