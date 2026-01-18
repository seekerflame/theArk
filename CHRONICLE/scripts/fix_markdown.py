import os
import re

def fix_markdown_formatting(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.readlines()

    new_content = []
    in_list = False
    
    for i, line in enumerate(content):
        original_line = line
        stripped = line.strip()
        
        # Heading Logic (MD022)
        if stripped.startswith('#'):
            # Ensure blank line before (unless first line)
            if new_content and new_content[-1].strip() != '':
                new_content.append('\n')
            
            new_content.append(line)
            
            # Ensure blank line after will be handled by next iteration check
            # (but we can preemptively check next line in original)
            if i + 1 < len(content) and content[i+1].strip() != '':
                 # We rely on the "blank line before" logic of the NEXT line? 
                 # No, that logic is "insert before ME".
                 # So if we have Header\nText, next loop processes Text. It sees last line was Header.
                 pass
            continue

        # List Logic (MD032)
        is_list_item = re.match(r'^\s*[-*d]\s+', line) or re.match(r'^\s*\d+\.\s+', line)
        
        if is_list_item:
            if not in_list:
                # Start of list - ensure blank line before
                if new_content and new_content[-1].strip() != '':
                     new_content.append('\n')
                in_list = True
        else:
             if in_list and stripped != '':
                 # End of list - ensure blank line before this non-list text
                 # effectively putting blank line after list
                 if new_content and new_content[-1].strip() != '':
                      new_content.append('\n')
                 in_list = False
             elif stripped == '':
                 in_list = False

        # Ensure blank line AFTER heading
        if new_content and new_content[-1].strip().startswith('#') and stripped != '':
            new_content.append('\n')

        new_content.append(line)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_content)
    print(f"Fixed: {file_path}")

# Scan Directory
root_dir = '/Volumes/Extreme SSD/Antigrav/OSE/CHRONICLE'
for dirpath, dirnames, filenames in os.walk(root_dir):
    for filename in filenames:
        if filename.endswith('.md'):
            fix_markdown_formatting(os.path.join(dirpath, filename))
