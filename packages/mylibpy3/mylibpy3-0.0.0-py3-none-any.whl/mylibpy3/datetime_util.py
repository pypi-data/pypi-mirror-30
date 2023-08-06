
def epoch_millis_to_seconds(epoch_millis):
    return int(epoch_millis / 1000)

def epoch_seconds_to_millis(epoch_seconds):
    return epoch_seconds * 1000

def local_millis_to_seconds(local_millis):
    return local_millis[:-4]

def local_seconds_to_millis(local_seconds):
    return local_seconds + '.000'

def compact_millis_to_seconds(compact_millis):
    return compact_millis[:-4]

def compact_seconds_to_millis(compact_seconds):
    return compact_seconds + '.000'

def iso_millis_to_seconds(iso_millis):
    return iso_millis[:19] + iso_millis[23:]

def iso_seconds_to_millis(iso_seconds):
    return iso_seconds[:19] + '.000' + iso_seconds[19:]

if __name__ == '__main__':
    pass
