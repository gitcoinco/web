BRANCH=$1
#deploy script
#assumes that gitcoin repo lives at $HOME/gitcoin
# and that gitcoinenv is the virtualenv under which it lives

#setup
cd 
cd gitcoin/coin
source ../gitcoinenv/bin/activate

#pull from git
git add .
git stash
git checkout $BRANCH
git pull origin $BRANCH

#deploy hooks
pip install -r requirements.txt
crontab scripts/crontab
cd app
./manage.py collectstatic --noinput -i other
rm -Rf ~/gitcoin/coin/app/static/other
./manage.py migrate
./manage.py createcachetable

#finally, let gunicorn know its ok to restart
sudo systemctl restart gunicorn
