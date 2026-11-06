from statistics import mean, stdev

MIN_HISTORY = 10
THRESHOLD = 3
def is_anomaly(history, value): #history is the recent values for one sensor and value is the specific value that is being judged
    if len(history) < MIN_HISTORY:
        return False
    m = mean(history) #calculating the mean of the recent values for one sensor
    s = stdev(history) # calculating the standard deviation of the recent values before this one for one sensor
    if s == 0: #if every historical value is equal, we want to avoid dividing by 0
        return False
    z = abs((value - m)/s)
    return z > THRESHOLD

