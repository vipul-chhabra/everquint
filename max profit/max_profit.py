"""
Theatre: 5 units to build, earns 1500/unit
Pub: 4 units, earns 1000/unit
Commercial Park: 10 units, earns 2000/unit

"""

# name, build time, rate, position in the (T, P, C) count tuple
BUILDINGS = [
    ("Theatre", 5, 1500, 0),
    ("Pub", 4, 1000, 1),
    ("Commercial Park", 10, 2000, 2),
]


def solve(n):
    best = [0] * (n + 1)
    mixes = [{(0, 0, 0)} for k in range(n + 1)]
    for t in range(1, n + 1):
        for name, duration, rate, idx in BUILDINGS:
            if duration >= t:
                continue
            total = rate * (t - duration) + best[t - duration]
            if total < best[t]:
                continue
            if total > best[t]:
                best[t] = total
                mixes[t] = set()
            for mix in mixes[t - duration]:
                counts = list(mix)
                counts[idx] += 1
                mixes[t].add(tuple(counts))
    return best[n], mixes[n]


def report(n):
    earnings, mixes = solve(n)
    lines = [f"Time Unit: {n}", f"Earnings: ${earnings}", "Solutions"]
    for i, (theatres, pubs, parks) in enumerate(sorted(mixes, reverse=True), start=1):
        lines.append(f"{i}. T: {theatres} P: {pubs} C: {parks}")
    return "\n".join(lines)


if __name__ == "__main__":
    while True:
        try:
            answer = input("Time unit (blank to quit): ").strip()
        except EOFError:
            break
        if not answer:
            break
        try:
            n = int(answer)
        except ValueError:
            print("Enter a whole number.")
            continue
        if n < 0:
            print("Time unit can't be negative.")
            continue
        print(report(n))
        print()