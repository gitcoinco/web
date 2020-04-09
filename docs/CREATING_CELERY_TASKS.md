# Celery 

First make sure you have read and understand the celery docs. [Celery Docs](https://celery.readthedocs.io/en/latest/getting-started/introduction.html)


`app/taskapp/celery.py` has been setup to automatically discover tasks added to different django applications, all you have to do is include shared_tasks inside `tasks.py` (if this file doesn't exist yet inside the app create it) 

##### Creating a new Shared Task
`app/DJANGO_APP/tasks.py`

setup your libraries that you'll need to successfully complete the work you're outlining in the task, below is the bounty_email task from 

`app/dashboard/tasks.py`



The last variable must be retry as a boolean
```
@app.shared_task(bind=True, max_retries=3)
def bounty_emails(self, emails, msg, profile_handle, invite_url=None, kudos_invite=False, retry: bool = True) -> None:
    """
    :param self:
    :param emails:
    :param msg:
    :param profile_handle:
    :param invite_url:
    :param kudos_invite:
    :return:
    """
    # locks the redis key so that other workers can't acquire the same invite_url
    with redis.lock("tasks:bounty_email:%s" % invite_url, timeout=LOCK_TIMEOUT):
        # need to look at how to send bulk emails with SG
        profile = Profile.objects.get(handle=profile_handle) 
        try:
            for email in emails:
                to_email = email
                from_email = settings.CONTACT_EMAIL
                subject = "You have been invited to work on a bounty."
                html, text = render_share_bounty(to_email, msg, profile, invite_url, kudos_invite)
                send_mail(
                    from_email,
                    to_email,
                    subject,
                    text,
                    html,
                    from_name=f"@{profile.handle}",
                    categories=['transactional', func_name()],
                )

        except ConnectionError as exc:
            print(exc)
            self.retry(countdown=30)
```


to delay the above task, you simply import the task, `from dashboard.tasks import bounty_emails`

in `app/marketing/mails.py` we invoke it like so:

```def share_bounty(emails, msg, profile, invite_url=None, kudos_invite=False):
    from dashboard.tasks import bounty_emails
    # attempt to delay bounty_emails task to a worker
    # long on failure to queue
    try:
        bounty_emails.delay(emails, msg, profile.handle, invite_url, kudos_invite)
    except Exception as e:
        logger.error(str(e))```
