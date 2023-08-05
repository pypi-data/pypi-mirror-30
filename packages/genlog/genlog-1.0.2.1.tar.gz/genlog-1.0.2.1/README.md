# GenerateLog

## What it is
genlog is a tool that can randomly generate log info about user mobile app and send these to specified remote host

## How to use
- install
    - `$ pip3 install genlog`
    - `$ git clone git@github.com:ilpan/GenerateLog.git`
- usage
    - genlog (./main.py) --help
    - genlog (./main.py) ( use default conf)
    - genlog (./main.py) -n [client_num] -i [interval (>1000ms)] -u [user_num] -l [remote_host_list] -s [show]
    - note: for remote_host_list, you need write 'ip:port,ip:port...' with quotes if you want to send data to a host list

## Result
![result](./result.png)
