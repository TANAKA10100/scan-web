import os

print("=== RUN WEB SCANNER ===")

target = input("TARGET: ").strip()
if not target:
    print("Target tidak boleh kosong!")
    exit()

# jalankan scan.py dengan target
os.system(f"python scan.py {target}")
