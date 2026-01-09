import requests
import csv
import json
import statistics
import io
import sys

# Standard Beopjeong-dong code file URL (This is a mirror or you can download from code.go.kr)
# Since direct raw links change, this script handles the standard '법정동코드 전체자료.txt' format.
# You can download the latest version from: https://www.code.go.kr/stdcode/regCodeL.do 

def parse_beopjeongdong(file_path=None, encoding='cp949'):
    """
    Parses the Beopjeong-dong code list (txt/csv) into a hierarchical JSON structure.
    Sido -> Sigugun -> Dong
    """
    data = {}

    # Mock data if file is not provided (for demonstration)
    lines = []
    if not file_path:
        print("No file path provided. Using a standard structure example.")
        print("Please download '법정동코드 전체자료.txt' from https://www.code.go.kr/stdcode/regCodeL.do")
        # Sample lines
        lines = [
            "1100000000\t서울특별시\t존재",
            "1111000000\t서울특별시 종로구\t존재",
            "1111010100\t서울특별시 종로구 청운동\t존재",
            "1111010200\t서울특별시 종로구 신교동\t존재",
            "4100000000\t경기도\t존재",
            "4111000000\t경기도 수원시\t존재",
            "4111100000\t경기도 수원시 장안구\t존재",
            "4111110100\t경기도 수원시 장안구 파장동\t존재",
        ]
    else:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                lines = f.readlines()
        except Exception as e:
            print(f"Error reading file: {e}")
            return

    for line in lines:
        parts = line.strip().split('\t')
        if len(parts) < 3:
            continue
        
        code = parts[0]
        full_name = parts[1]
        status = parts[2]

        if status != "존재":
            continue

        names = full_name.split(" ")
        
        sido = names[0]
        sigugun = ""
        dong = ""

        if len(names) > 1:
            sigugun = names[1]
            # Handle cases like "수원시 장안구" which are sometimes split or combined
            # In standard file: "경기도 수원시 장안구" -> names[1]="수원시", names[2]="장안구"
            if len(names) > 2:
                 # Check if the second part ends with '시' or '군' and third with '구' (Gu inside Si)
                 if (names[1].endswith("시") or names[1].endswith("군")) and names[2].endswith("구"):
                     sigugun = f"{names[1]} {names[2]}"
                     if len(names) > 3:
                         dong = names[3]
                 else:
                     dong = names[2]
        
        # Build Hierarchy
        if sido not in data:
            data[sido] = {}
        
        if sigugun:
            if sigugun not in data[sido]:
                data[sido][sigugun] = []
            
            if dong:
                if dong not in data[sido][sigugun]:
                    data[sido][sigugun].append(dong)

    return data

if __name__ == "__main__":
    if len(sys.argv) > 1:
        result = parse_beopjeongdong(sys.argv[1])
    else:
        result = parse_beopjeongdong()
    
    with open("korea_administrative_divisions.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print("Successfully generated korea_administrative_divisions.json")
