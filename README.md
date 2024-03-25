
install pip requirements
```bash
pip install -r requirements.txt
```

install google chrome:
```bash
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
```


```bash
python main.py -h
usage: main.py [-h] [-b BOOK] [-s SUPERVISE] [-i INPUT]

options:
  -h, --help            show this help message and exit
  -b BOOK, --book BOOK  book or test
  -s SUPERVISE, --supervise SUPERVISE
                        supervise interval seconds
  -i INPUT, --input INPUT
                        input a want list filename
```

if no display error

```bash
$ export DISPLAY=:0.0
$ export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0
```

wantlist file sample:

```json
[
    {
      "id": 123123123,
      "callan": [],
      "name": "ABCABC",
      "time": [
        {"Mon": ["12:00", "22:30", "23:00", "23:30"]},
        {"Tue": ["12:00", "22:30", "23:00", "23:30"]},
        {"Wed": ["12:00", "22:30", "23:00", "23:30"]},
        {"Thu": ["19:30"]},
        {"Fri": ["12:00", "22:30", "23:00", "23:30"]},
        {"Sat": ["12:00", "22:30", "23:00", "23:30"]},
        {"Sun": ["12:00", "22:30", "23:00", "23:30"]},
      ]
    }
  ]
```

```yaml
---
- id: 123123123
  name: ABCABC
  callan: ['21:00', '22:30']
  callan_new: ['21:00', '22:30']
  time:
  - Mon: ['21:00', '22:30', '23:00']
  - Tue: ['21:00', '22:30', '23:00']
  - Wed: ['21:00', '22:30', '23:00']
  - Fri: ['21:00', '22:30', '23:00']
  - Sat: ['21:00', '22:30', '23:00']
  - Sun: ['21:00', '22:30', '23:00']

```