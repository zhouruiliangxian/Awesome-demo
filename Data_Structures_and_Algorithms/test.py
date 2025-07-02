import sys
from collections import defaultdict

def main():
    data = [
        [800, 2, 0],  # 主件
        [400, 5, 1],  # 附件，属于主件1
        [300, 5, 1],  # 附件，属于主件1
        [400, 3, 0],  # 主件
        [500, 2, 0]   # 主件
    ]
    
    # 假设预算是1000，物品数量是5
    n = 1000
    m = 5
    
    n //= 10
    items = []
    for item in data:
        v, w, q = item
        v //= 10
        items.append((v, w, q))
        
    main_items = []
    attachments = defaultdict(list)
    
    for i in range(m):
        v, w, q = items[i]
        if q == 0:
            main_items.append((v, w, i+1))
        else:
            attachments[q].append((v, w))
            
    groups = []
    for item in main_items:
        v0, w0, idx = item
        att_list = attachments.get(idx, [])
        options = []
        options.append((v0, v0 * w0))
        if len(att_list) >= 1:
            v1, w1 = att_list[0]
            options.append((v0 + v1, v0*w0 + v1*w1))
        if len(att_list) >= 2:
            v2, w2 = att_list[1]
            options.append((v0 + v2, v0*w0 + v2*w2))
            options.append((v0 + v1 + v2, v0*w0 + v1*w1 + v2*w2))
        groups.append(options)
        
    dp = [0] * (n + 1)
    for group in groups:
        for j in range(n, -1, -1):
            for c, s in group:
                if j >= c:
                    if dp[j] < dp[j - c] + s:
                        dp[j] = dp[j - c] + s
    ans = max(dp) * 10
    print(ans)




if __name__ == '__main__':
    # main()
    import re

    def move_robot(s):
        x, y = 0, 0
        # 改进后的正则表达式，确保指令前是开头或分号 (0[1-9]|[1-9]\d?);
        pattern = re.compile(r"(?:^|;)([ADWS])(0[1-9]|[1-9]\d?);")
        print( pattern.finditer(s))
        for match in pattern.finditer(s):
            direction = match.group(1)
            steps = int(match.group(2))
            if 1 <= steps <= 99:
                if direction == "A":
                    x -= steps
                elif direction == "D":
                    x += steps
                elif direction == "W":
                    y += steps
                elif direction == "S":
                    y -= steps
        return f"{x},{y}"


    # 读取输入
    s = "A10;S20;W10;D30;X;A1A;B10A11;;A10;"
    # 处理并输出结果
    print(move_robot(s))
