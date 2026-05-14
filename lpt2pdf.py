import serial
import subprocess
import datetime
import os
import tempfile

# --- CONFIG ---
SERIAL_PORT = 'COM6'       # adjust to the LPT2PDF device
BAUDRATE = 9600  
OUTPUT_DIR = r'C:\Temp\PCLjobs' # ensure it exists
GPCL6_PATH = r'C:\Users\EMC\Downloads\ghostpcl\ghostpcl-10.06.0-win64\gpcl6win64.exe'  # path to GhostPCL on Windows - Make sure gpcl6.exe is on your PC; you can download GhostPDL from Artifex.
BUFFER_SIZE = 1024

# --- CREATE OUTPUT DIR ---
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- OPEN SERIAL PORT ---
ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)


def save_and_convert(pcl_data):
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    pcl_file = os.path.join(OUTPUT_DIR, f'job_{timestamp}.pcl')
    pdf_file = os.path.join(OUTPUT_DIR, f'job_{timestamp}.pdf')

    # Save raw PCL
    with open(pcl_file, 'wb') as f:
        f.write(pcl_data)

    # Call GhostPCL to convert to PDF
    subprocess.run([GPCL6_PATH, '-dNOPAUSE', '-sDEVICE=pdfwrite', f'-sOutputFile={pdf_file}', pcl_file], check=True)
    print(f'Converted {pcl_file} -> {pdf_file}')
    subprocess.Popen([pdf_file], shell=True)

def main():
    buffer = bytearray()
    print(f"Listening on {SERIAL_PORT}...")
    try:
        while True:
            chunk = ser.read(BUFFER_SIZE)
            if chunk:
                buffer.extend(chunk)
                
                if len(chunk) < BUFFER_SIZE:
                    print(f'Received {len(buffer)} bytes...')
                    save_and_convert(buffer)
                    buffer.clear()
                
                # Detect Universal End of Language (UEL) sequence: 0x1B%-12345X
                if b'\x1B%-12345X' in buffer:
                    print(f'Received {len(buffer)} bytes...')
                    save_and_convert(buffer)
                    buffer.clear()
    except KeyboardInterrupt:
        print("Exiting.")
    finally:
        ser.close()

if __name__ == "__main__":
    main()

