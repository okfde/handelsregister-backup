set -x
until python scrape.py -v --proxypid $1
do
  sleep 0.1
done

