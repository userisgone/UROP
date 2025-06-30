#this version compares SINES using similar start/stop 

from collections import defaultdict

def read_sine_file(file_path):
    """Read SINE text file into list of dictionaries"""
    with open(file_path, 'r') as f:
        # Skip non-header lines
        while True:
            pos = f.tell()
            line = f.readline()
            if any(x in line for x in ['SeqID', 'Start', 'Stop', 'End', 'Orientation']):
                f.seek(pos)
                break

        header = [col.strip().replace(' ', '').lower() for col in f.readline().strip().split('\t')]
        return [dict(zip(header, line.strip().split('\t'))) for line in f if line.strip()]


def group_by_seqid(entries):
    grouped = defaultdict(list)
    for e in entries:
        seqid = e.get('seqid', '').split('.')[0]
        grouped[seqid].append(e)
    return grouped

def is_match(e1, e2, tolerance=100):
    try:
        start1, stop1 = int(e1['start']), int(e1['stop'])
        start2, stop2 = int(e2['start']), int(e2['stop'])
        return abs(start1 - start2) <= tolerance or abs(stop1 - stop2) <= tolerance
    except:
        return False

def compare_sines():
    file1 = read_sine_file("/Users/emmabarton/UROP/sine1_features.txt")
    file2 = read_sine_file("/Users/emmabarton/UROP/EhSINE1_Full_List.txt")

    grouped1 = group_by_seqid(file1)
    grouped2 = group_by_seqid(file2)

    matched = []
    only_file1 = []
    only_file2 = []

    seen1 = set()
    seen2 = set()

    for seqid in set(grouped1) | set(grouped2):
        entries1 = grouped1.get(seqid, [])
        entries2 = grouped2.get(seqid, [])

        for e1 in entries1:
            matched_flag = False
            for e2 in entries2:
                if is_match(e1, e2):
                    matched.append((e1, e2))
                    seen1.add(id(e1))
                    seen2.add(id(e2))
                    matched_flag = True
                    break
            if not matched_flag:
                only_file1.append(e1)

        for e2 in entries2:
            if id(e2) not in seen2:
                only_file2.append(e2)

    with open("comparison_results_(start_stop).txt", 'w') as out:
        out.write("=== COMMON SINEs ver.1")
        out.write("SeqID\tSINE_ID_1\tStart_1\tStop_1\tOrientation_1\tLength_1\tSINE_ID_2\tStart_2\tStop_2\tOrientation_2\tLength_2\n")
        for e1, e2 in matched:
            out.write(f"{e1.get('seqid','')}\t{e1.get('sineid','')}\t{e1.get('start','')}\t{e1.get('stop','')}\t{e1.get('orientation','')}\t{e1.get('length','')}\t"
                      f"{e2.get('sineid','')}\t{e2.get('start','')}\t{e2.get('stop','')}\t{e2.get('orientation','')}\t{e2.get('length','')}\n")

        out.write("\n=== ONLY IN FILE 1 ===\n")
        out.write("SeqID\tSINE_ID\tStart\tStop\tOrientation\tLength\n")
        for e in only_file1:
            out.write(f"{e.get('seqid','')}\t{e.get('sineid','')}\t{e.get('start','')}\t{e.get('stop','')}\t{e.get('orientation','')}\t{e.get('length','')}\n")

        out.write("\n=== ONLY IN FILE 2 ===\n")
        out.write("SeqID\tSINE_ID\tStart\tStop\tOrientation\tLength\n")
        for e in only_file2:
            out.write(f"{e.get('seqid','')}\t{e.get('sineid','')}\t{e.get('start','')}\t{e.get('stop','')}\t{e.get('orientation','')}\t{e.get('length','')}\n")

    print("\nComparison complete.")
    print(f"Matched: {len(matched)} entries")
    print(f"Unique to File 1: {len(only_file1)}")
    print(f"Unique to File 2: {len(only_file2)}")


# Run the comparison
compare_sines()
