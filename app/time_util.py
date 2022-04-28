from datetime import datetime, timedelta

def hour_rounder(t):
    # Rounds to nearest hour by adding a timedelta hour 
    # of 2 hrs if the current minutes is >= 55
    if t.minute >= 55:
        delta = timedelta(hours=2)
    # of 1 hrs if the current minutes is bel
    else:
        delta = timedelta(hours=1)
    return (t.replace(second=0, microsecond=0, minute=0, hour=t.hour)
            +delta)

if __name__ == "__main__":
    now = datetime(2022,4,17,23,55)
    print(hour_rounder(now))
    print(hour_rounder(datetime.now()))