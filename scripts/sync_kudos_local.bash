while true; do
    python manage.py sync_kudos localhost filter -s earliest >> /var/log/kudos_sync.log 2>&1
    sleep 60
done
