#migrates the info on one grant to another

old_grant_id = 128
new_grant_id = 200

from grants.models import Grant

old_grant = Grant.objects.get(pk=old_grant_id)
new_grant = Grant.objects.get(pk=new_grant_id)

for sub in old_grant.subscriptions.all():
    sub.grant = new_grant
    sub.save()

for obj in old_grant.phantom_funding.all():
    obj.grant = new_grant
    obj.save()

for obj in old_grant.milestones.all():
    obj.grant = new_grant
    obj.save()

for obj in old_grant.activities.all():
    obj.grant = new_grant
    obj.save()

for obj in old_grant.updates.all():
    obj.grant = new_grant
    obj.save()

for obj in old_grant.clr_matches.all():
    obj.grant = new_grant
    obj.save()

old_grant.hidden = True
old_grant.link_to_new_grant = new_grant

old_grant.save()
new_grant.save()
