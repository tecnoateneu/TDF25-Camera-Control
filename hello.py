
import time
time.sleep(0.5)

print('starting')
count = 0
delay = 0.5

while count < 1000000:
    count = count + 10
    print(count)
    time.sleep(delay)
