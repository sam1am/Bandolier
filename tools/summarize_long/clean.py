import sys
import re
import os

def clean_transcript(input_file):
    # Create output file name by appending '_cleaned' before file extension
    base = os.path.splitext(input_file)[0]
    output_file = base + '_cleaned' + os.path.splitext(input_file)[1]
    
    with open(input_file, 'r') as f, open(output_file, 'w') as out:
        for line in f:
            # If the line matches the pattern for a timestamp, skip it
            if re.match(r'\d\d:\d\d.\d\d\d --> \d\d:\d\d.\d\d\d', line):
                continue
            # If the line is blank (only contains whitespace), skip it
            elif not line.strip():
                continue
            else:
                # If the line is not a timestamp or blank, write it to the output file
                out.write(line)

    print(f"Cleaned transcript has been saved as: {output_file}")

# Example usage:
if __name__ == "__main__":
    clean_transcript(sys.argv[1])
