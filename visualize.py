import matplotlib.pyplot as plt

num_hands = 500000
divider = 1
file_name = 'gamelog.txt'

A_plus_minus = [0]
B_plus_minus = [0]
hand_num = [0]
guarenteed_win = [int(1.5*num_hands)+2]
even = [0]

# reading gamelog.txt:
with open(file_name, 'r') as f:
    text = f.read()
    text_rows = text.split('\n')
    for i, row in enumerate(text_rows):
        if "Round" in row:
            num = int(row.split(',')[0].split('#')[1])
            if num % divider == 0:
                A_up = int(row.split('A')[1].split('(')[1].split(')')[0])
                B_up = -A_up
                A_plus_minus.append(A_up)
                B_plus_minus.append(B_up)
                hand_num.append(num)
                guarenteed_win.append(int(1.5*(num_hands-num)+2))
                even.append(0)
            if num == num_hands:
                break

# making graph:
plt.title('Performance(A is red, B is blue)')
plt.plot(hand_num, A_plus_minus, 'r')
plt.plot(hand_num, B_plus_minus, 'b')
plt.plot(hand_num, guarenteed_win, 'g')
plt.plot(hand_num, even, 'k')
plt.show()