cd ../src


# change virtualenv
# workon myviertualenv

nohup python main.py &
echo $! > ../tmp/server.pid