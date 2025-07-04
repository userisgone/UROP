def process_feature_table(input_file, output_file):
    """
    
    Args:
        input_file (str): Path to input feature table file
        output_file (str): Path to output file for results
    """
    
    sine_counter = 1  # SINE ID
    current_seqid = None #SeqID
    current_feature = None #Location
    sine1_features = [] #All the features to be printed
    
    # Open input file and process line by line
    with open(input_file, 'r') as in_f:
        for line in in_f:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
                
            # Check for >Feature to find SeqID
            if line.startswith('>Feature'):
                # Extract SeqID
                current_seqid = line.split('|')[-2]
                continue
                
            # Check if this is a feature line 
            if line[0].isdigit() or line.startswith('<') or line.startswith('>'):
                #Split the line by tabs to extract all the features within
                parts = line.split('\t')
                if len(parts) >= 2:
                    try:
                        start = int(parts[0])
                        end = int(parts[1])
                        current_feature = (start, end)
                    except ValueError:
                        current_feature = None
                continue
                
            # Check if this is a qualifier line (indented)
            if current_feature and "rpt_family" in line.lower() and "sine1" in line.lower():
                parts = line.strip().split('\t')
                if len(parts) >= 2:
                    key = parts[0].lower()
                    value = parts[1].lower()
                    if "rpt_family" in key and "sine1" in value:
                        start, end = current_feature
                        
                        # Correct and adjust for orientation
                        if start < end:
                            orientation = '+'
                            final_start = start
                            final_end = end
                        else:
                            orientation = '-'
                            final_start = end
                            final_end = start
                        
                        # Calculate length
                        length = abs(end - start) + 1
                        
                        #Append to table
                        sine1_features.append(
                            (sine_counter, current_seqid, orientation, final_start, final_end, length))
                        sine_counter += 1
    
    # Write all collected features to output file
    with open(output_file, 'w') as out_f:
        # Header row 
        out_f.write("SINE ID\tSeqID\tOrientation\tStart\tStop\tLength\n")
        
        # Write all features
        for feature in sine1_features:
            out_line = '\t'.join(map(str, feature)) + '\n'
            out_f.write(out_line)

if __name__ == "__main__":
    #Rename as necessary for input and output files
    input_file = "histolytica_feature_tables.txt"  # CHANGE AS APPROPRIATE: Your input file
    output_file = "sine1_features.txt"  # CHANGE AS APPROPRIATE: Output file
    
    process_feature_table(input_file, output_file)
    print(f"Processing complete. Results saved to {output_file}")
