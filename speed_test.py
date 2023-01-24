import time
start = time.time()

hand_range = {i:1 for i in range(52*51//2)}
for hand_num in range(1000):
    for betting_round in range(5):
        for hand in hand_range:
            x = 2+5
            y = 7*8
            hand_range[hand] = hand_range[hand]*2/3






end = time.time()
print(f'total time for 1000 hands updates:{end-start}')
