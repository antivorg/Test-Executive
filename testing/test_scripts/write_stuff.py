import time

i = 0

with open('output.txt', 'w+') as file:
    while i < 20:
        print(f'{i}, hey, this is stdout!')
        file.write(f'{i}, hey, this is written to a file!')
        time.sleep(0.5)
        i += 1


