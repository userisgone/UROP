from collections import defaultdict

#Parse GTF file for transcript entries
def parse_transcripts(gtf_file):
    transcripts = []
    with open(gtf_file, 'r') as f:
        for line in f:
            if line.strip() == '' or line.startswith('#'):
                continue
            parts = line.strip().split('\t') 
            if parts[2] != 'transcript':
                continue  # Only considers transcript lines to reduce overlap
            contig = parts[0]
            start = int(parts[3])
            end = int(parts[4])
            strand = parts[6]
            info = parts[8]
            transcripts.append((contig, start, end, strand, info))
    return transcripts

#Find overlapping transcripts (grouped)
def find_positional_overlaps_grouped(denovo, sines, tolerance=0.1): #finds overlapping with 10% tolerance based on SINE length
    
    overlaps = defaultdict(list)
    matched_sines = set()

    for s_index, (s_contig, s_start, s_end, s_strand, s_info) in enumerate(sines):
        s_len = s_end - s_start + 1
        tol = int(s_len * tolerance)
        s_start_tol = s_start - tol
        s_end_tol = s_end + tol

        for d_contig, d_start, d_end, d_strand, d_info in denovo:
            if s_contig != d_contig:
                continue  
            if s_strand != d_strand:
                continue  
            if d_end >= s_start_tol and d_start <= s_end_tol:
                overlaps[s_index].append((d_contig, d_start, d_end, d_info))
                matched_sines.add(s_index) #matched 

    unmatched_sines = [s for i, s in enumerate(sines) if i not in matched_sines]
    return overlaps, unmatched_sines #unmatched

#Save to file (matched)
def save_grouped_overlaps(overlaps, sines, output_file='overlapping_transcripts_1.txt'): #CHANGE ME
    """
    Writes all overlapping DeNovo matches grouped by SINE to a text file.
    """
    with open(output_file, 'w') as f:
        f.write(f"Found {len(overlaps)} SINEs with overlapping DeNovo transcripts (±10% tolerance):\n\n")
        for i, (s_index, denovo_matches) in enumerate(overlaps.items(), 1):
            s_contig, s_start, s_end, s_strand, s_info = sines[s_index]
            f.write(f"🔹 SINE {i} → {s_contig}:{s_start}-{s_end} |{s_strand}|{s_info}\n")
            for j, (d_contig, d_start, d_end, d_info) in enumerate(denovo_matches, 1):
                f.write(f"    Match {j}: {d_contig}:{d_start}-{d_end} | {d_info}\n")
            f.write("\n")

#Save to file (unmatched)
def save_unmatched_sines(unmatched, output_file='unmatched_sines_1.txt'): #CHANGE ME
    """
    Writes all unmatched SINE transcripts to a text file.
    """
    with open(output_file, 'w') as f:
        f.write(f"{len(unmatched)} SINE transcripts did not match any DeNovo transcript (±10% tolerance):\n\n")
        for i, (contig, start, end, strand, info) in enumerate(unmatched, 1):
            f.write(f"Unmatched {i} → {contig}:{start}-{end} | {strand} | {info}\n")

# === Main Execution ===
if __name__ == '__main__':
    # Input GTF files
    denovo_file = '/Users/emmabarton/Desktop/UROP/Eh_transcript_denovo.gtf' #CHANGE ME
    sines_file = '/Users/emmabarton/Desktop/UROP/Eh_SINE1_only_1_e.gtf' #CHANGE ME

    # Parse transcript entries
    denovo_transcripts = parse_transcripts(denovo_file)
    sine_transcripts = parse_transcripts(sines_file)

    print(f"Parsed {len(denovo_transcripts)} transcript entries from {denovo_file}")
    print(f"Parsed {len(sine_transcripts)} transcript entries from {sines_file}")

    # Find overlaps and unmatched entries
    overlaps_grouped, unmatched_sines = find_positional_overlaps_grouped(
        denovo_transcripts, sine_transcripts, tolerance=0.1
    )

    # Display results summary
    print(f"\n Found {len(overlaps_grouped)} SINEs with overlapping DeNovo transcripts (±10% tolerance).")
    print(f" {len(unmatched_sines)} SINE transcripts had no overlaps.\n")

    # Save to output files
    save_grouped_overlaps(overlaps_grouped, sine_transcripts)
    save_unmatched_sines(unmatched_sines)

    print("📁 Results saved to:")
    print("   • overlapping_transcripts_1.txt") #CHANGE ME
    print("   • unmatched_sines_1.txt") #CHANGE ME
