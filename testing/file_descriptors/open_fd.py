
import time

j = 0
while False:
    j += 1
    print(f'{j}')
    time.sleep(0.1)

with open('file.txt', 'w+') as file:
    i = 0
    while i < 10:
        file.write(f'{i}\n')
        file.flush()
        time.sleep(1)
        i += 1
        print('penis')
