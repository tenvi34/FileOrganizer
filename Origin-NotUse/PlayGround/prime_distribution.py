import math
import matplotlib.pyplot as plt


# 소수 판별 함수
def is_prime(n):
    if n <= 1:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True


# π(x) 함수 생성
def prime_pi(x):
    count = 0
    for i in range(2, x + 1):
        if is_prime(i):
            count += 1
    return count


# 데이터 생성
X = list(range(2, 1001, 10))
pi_x = [prime_pi(x) for x in X]
approx = [x / math.log(x) for x in X]

# 그래프 그리기
plt.figure(figsize=(10, 6))
plt.plot(X, pi_x, label="π(x) (실제 소수 개수)", marker="o", markersize=4)
plt.plot(X, approx, label="x / ln(x) (근사치)", linestyle="--")
plt.xlabel("x")
plt.ylabel("소수 개수")
plt.title("π(x) vs 소수정리 근사치")
plt.legend()
plt.grid(True)
plt.show()
