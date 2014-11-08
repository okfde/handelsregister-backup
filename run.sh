set -x
until python scrape.py -v -s 127.0.0.1 -p 9050 --proxypid $1
do
  sleep 0.1
done

