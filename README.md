# we_broke
project to fetch our current balance from our google drive document

# requirements
 * pydrive
 * bottle
 * python 2.7
 * dateutils

# usage

firstly, you need to get your credentials authorized to run fetch the balance

```python
>>> import balance
balance.fetch()
# Click on the provided URL, authorize your credentials, 
# copy the code and paste it on the command line
```

# response

```python
{
  lastUpdate: UTC standard formatted,
  lastUpdateHuman: BRT %d-%m-%y %H:%M %Z formatted,
  balance: real,
  daysRemaining: int
}
```
then you may simply run the server

```$ python server.py```
