import sys, time

BOLD  = "\033[1m"
RESET = "\033[0m"

delay   = 0.0008      # slower/faster typing
indent  = "    "      # left padding
scale_x = 2           # 1 = normal, 2 = wider (more readable)
scale_y = 1           # 1 = normal, 2 = taller

# 7-high block letters using only * and spaces
I = [
"*******",
"   *   ",
"   *   ",
"   *   ",
"   *   ",
"   *   ",
"*******",
]
L = [
"*      ",
"*      ",
"*      ",
"*      ",
"*      ",
"*      ",
"*******",
]
O = [
" ***** ",
"*     *",
"*     *",
"*     *",
"*     *",
"*     *",
" ***** ",
]
V = [
"*     *",
"*     *",
"*     *",
"*     *",
" *   * ",
"  * *  ",
"   *   ",
]
E = [
"*******",
"*      ",
"*      ",
"*****  ",
"*      ",
"*      ",
"*******",
]
Y = [
"*     *",
" *   * ",
"  * *  ",
"   *   ",
"   *   ",
"   *   ",
"   *   ",
]
U = [
"*     *",
"*     *",
"*     *",
"*     *",
"*     *",
"*     *",
" ***** ",
]
D = [
"****** ",
"*     *",
"*     *",
"*     *",
"*     *",
"*     *",
"****** ",
]

letters = [I, L, O, V, E, Y, O, U, D, I, V, V]
gaps =    [3, 3, 3, 3, 7, 3, 3, 7, 3, 3, 3]  # spaces between letters / words

# Build the 7 output rows
rows = [""] * 7
for idx, pat in enumerate(letters):
    for r in range(7):
        rows[r] += pat[r]
        if idx < len(gaps):
            rows[r] += " " * gaps[idx]

def widen(s, k):
    return "".join(ch * k for ch in s)

sys.stdout.write(BOLD)
for r in rows:
    line = indent + widen(r, scale_x)
    for _ in range(scale_y):
        for ch in line:
            sys.stdout.write(ch)
            sys.stdout.flush()
            time.sleep(delay)
        sys.stdout.write("\n")
sys.stdout.write(RESET)
