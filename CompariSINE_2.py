#this version compares SINES using overlapping regions
from collections import defaultdict

def read_sine_file(file_path):
    """Read SINE text file into list of dictionaries"""
    with open(file_path, 'r') as f:
        # Skip lines until header is found
        while True:
            pos = f.tell()
            line = f.readline()
            if any(x in line.lower() for x in ['seqid', 'start', 'stop', 'end', 'orientation']):
                f.seek(pos)
                break
        header = [col.strip().replace(' ', '').lower() for col in f.readline().strip().split('\t')]
        return [dict(zip(header, line.strip().split('\t'))) for line in f if line.strip()]

def get_interval_data(file):
    """Organise SINEs by seqid with interval info"""
    sine_by_seqid = defaultdict(list)
    for sine in file:
        seqid = sine.get('seqid', sine.get('eha2accession', '')).split('.')[0]
        try:
            start = int(sine['start'])
            stop = int(sine['stop'])
        except (KeyError, ValueError):
            continue
        sine_by_seqid[seqid].append({
            'sineid': sine.get('sineid', ''),
            'start': start,
            'stop': stop,
            'orientation': sine.get('orientation', ''),
            'length': sine.get('length', ''),
            'raw': sine
        })
    return sine_by_seqid

def intervals_overlap(a_start, a_stop, b_start, b_stop):
    return max(a_start, b_start) <= min(a_stop, b_stop)

def compare_by_overlap(file1, file2):
    data1 = get_interval_data(file1)
    data2 = get_interval_data(file2)

    common = []
    only1 = []
    only2 = []

    matched_2 = set()

    for seqid in set(data1.keys()) | set(data2.keys()):
        f1_intervals = data1.get(seqid, [])
        f2_intervals = data2.get(seqid, [])

        for sine1 in f1_intervals:
            match_found = False
            for idx, sine2 in enumerate(f2_intervals):
                if intervals_overlap(sine1['start'], sine1['stop'], sine2['start'], sine2['stop']):
                    common.append((seqid, sine1, sine2))
                    matched_2.add((seqid, idx))
                    match_found = True
                    break
            if not match_found:
                only1.append((seqid, sine1))

        for idx, sine2 in enumerate(f2_intervals):
            if (seqid, idx) not in matched_2:
                only2.append((seqid, sine2))

    return common, only1, only2

def compare_sines():
    file1 = read_sine_file("/Users/emmabarton/UROP/sine1_features.txt")
    file2 = read_sine_file("/Users/emmabarton/UROP/EhSINE1_Full_List.txt")

    common, only1, only2 = compare_by_overlap(file1, file2)

    with open("comparison_results_(overlap).txt", 'w') as out:
        out.write("=== COMMON SINEs ===\n")
        out.write("SeqID\tOrientation1\tStart1\tStop1\tSINEID1\tOrientation2\tStart2\tStop2\tSINEID2\t%Overlap\n")
        for seqid, s1, s2 in common:
            a_start, a_stop = s1['start'], s1['stop']
            b_start, b_stop = s2['start'], s2['stop']
            overlap_len = max(0, min(a_stop, b_stop) - max(a_start, b_start) + 1)
            union_len = max(a_stop, b_stop) - min(a_start, b_start) + 1
            percent_overlap = (overlap_len / union_len) * 100 if union_len > 0 else 0
            out.write(f"{seqid}\t{s1['orientation']}\t{a_start}\t{a_stop}\t{s1['sineid']}\t"
                    f"{s2['orientation']}\t{b_start}\t{b_stop}\t{s2['sineid']}\t"
                    f"{percent_overlap:.2f}%\n")

        out.write("\n=== ONLY IN FILE 1 ===\n")
        out.write("SeqID\tOrientation\tStart\tStop\tLength\tSINEID\n")
        for seqid, s in only1:
            out.write(f"{seqid}\t{s['orientation']}\t{s['start']}\t{s['stop']}\t{s['length']}\t{s['sineid']}\n")

        out.write("\n=== ONLY IN FILE 2 ===\n")
        out.write("SeqID\tOrientation\tStart\tStop\tLength\tSINEID\n")
        for seqid, s in only2:
            out.write(f"{seqid}\t{s['orientation']}\t{s['start']}\t{s['stop']}\t{s['length']}\t{s['sineid']}\n")

    print("Comparison completed successfully!")
    print(f"Common SINEs: {len(common)}")
    print(f"Unique to File 1: {len(only1)}")
    print(f"Unique to File 2: {len(only2)}")
    print("Results written to 'comparison_results.txt'")

if __name__ == "__main__":
    compare_sines()

