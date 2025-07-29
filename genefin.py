import re

def parse_coord(coord_str):
    """Extract seqname, start, and end from DS572490.1:890-1120"""
    seqname, coords = coord_str.split(':')
    start, end = map(int, coords.split('-'))
    return seqname, start, end

def load_sines_and_matches(filename):
    results = []
    with open(filename) as f:
        current_block = {}
        for line in f:
            line = line.strip()
            if line.startswith("🔹 SINE"):
                # Start of new SINE
                match = re.search(r"(DS\d+\.\d+:\d+-\d+)", line)
                if match:
                    seqname, start, end = parse_coord(match.group(1))
                    current_block = {
                        'type': 'SINE',
                        'seqname': seqname,
                        'start': start,
                        'end': end,
                        'line': line
                    }
                    results.append(current_block)
            elif line.startswith("Match"):
                match = re.search(r"(DS\d+\.\d+:\d+-\d+)", line)
                if match:
                    seqname, start, end = parse_coord(match.group(1))
                    results.append({
                        'type': 'Match',
                        'seqname': seqname,
                        'start': start,
                        'end': end,
                        'line': line
                    })
    return results

def find_nearby_features(features, user_seqname, user_start, user_end, window=1000):
    hits = []
    for feature in features:
        if feature['seqname'] != user_seqname:
            continue
        # Check if start or end is within ±1kb of gene start or end
        if (abs(feature['start'] - user_start) <= window or
            abs(feature['start'] - user_end) <= window or
            abs(feature['end'] - user_start) <= window or
            abs(feature['end'] - user_end) <= window):
            hits.append(feature)
    return hits

def main():
    input_file = "filtered_overlapping_sines_cov_gt10.txt"  # Replace with your filename
    features = load_sines_and_matches(input_file)

    user_seqname = input("Enter seqname (e.g. DS572490.1): ").strip()
    user_start = int(input("Enter gene start: "))
    user_end = int(input("Enter gene end: "))

    nearby = find_nearby_features(features, user_seqname, user_start, user_end)

    print(f"\nFound {len(nearby)} nearby SINEs/Matches within 1kb:")
    for feature in nearby:
        print(f"[{feature['type']}] {feature['line']}")

if __name__ == "__main__":
    main()
