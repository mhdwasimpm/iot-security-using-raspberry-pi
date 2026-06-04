import os
import time
import requests
from datetime import datetime

# --- Configuration ---
log_file = "alert.txt"
chat_id = "Chat_id"
token = "Token"
max_icmp_alerts = 4
max_telegram_msg_len = 4000  # Keep buffer under 4096

# --- Alert type matching ---
def get_alert_type(line):
    if "Nmap SYN Scan Detected" in line:
        return "Nmap SYN Scan"
    elif "ICMP flood" in line:
        return "ICMP Flood Attack"
    elif "SSH Brute Force" in line:
        return "SSH Brute Force Attempt"
    elif "SQL Injection" in line or "sqlmap" in line:
        return "SQL Injection Attempt"
    elif "Hydra" in line or "login.php" in line:
        return "HTTP Brute Force Attempt"
    elif "XSS attempt" in line:
        return "Cross-Site Scripting (XSS)"
    elif "Shellshock" in line:
        return "Shellshock Exploit Attempt"
    elif "Web Shell Upload" in line:
        return "Web Shell Upload Attempt"
    elif "Remote File Inclusion" in line:
        return "Remote File Inclusion (RFI) Attack"
    elif "Local File Inclusion" in line:
        return "Local File Inclusion (LFI) Attack"
    elif "SYN Flood" in line:
        return "Nmap SYN Attack"
    elif "XMAS Scan" in line:
        return "XMAS Port Scan"
    elif "FIN Scan" in line:
        return "FIN Port Scan"
    elif "DNS Query Flood" in line:
        return "DNS Query Flood"
    elif "DNS Amplification" in line:
        return "DNS Amplification Attack"
    elif "SMB Brute Force" in line:
        return "SMB Brute Force Attempt"
    elif "Brutefroce Attempt" in line:
        return "HTTP Brute Force Attempt"
    return None

# --- Telegram alert sender (with batching + rate limit handling) ---
def send_telegram_message(msg):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": msg, "parse_mode": "HTML"}

    while True:
        res = requests.post(url, data=payload)
            print        if res.status_code == 200:
("✅ Alert sent")
            break
        elif res.status_code == 429:
            retry = res.json().get("parameters", {}).get("retry_after", 5)
            print(f"⏳ Rate limited. Retrying in {retry}s")
            time.sleep(retry)
        else:
            pass
            break

def chunk_and_send(message):
    while message:
        part = message[:max_telegram_msg_len]
        send_telegram_message(part)
        message = message[max_telegram_msg_len:]
        time.sleep(1)  # Delay between chunks

# --- Main monitor ---
print("🔍 Monitoring alert.txt...")
file_position = 0
icmp_counter = 0

while True:
    if os.path.exists(log_file):
        with open(log_file, "r+") as f:
            f.seek(file_position)
            new_lines = f.readlines()
            file_position = f.tell()

            all_alerts = []
            sent_lines = []

            for line in new_lines:
                if "[**]" not in line:
                    continue

                alert_type = get_alert_type(line)
                if not alert_type:
                    continue

                if alert_type in ["ICMP Flood Attack", "SYN Flood Attack", "DNS Amplification Attack", "DNS Query Flood"]:
                    if icmp_counter >= max_icmp_alerts:
                        continue
                    icmp_counter += 1

                timestamp = line.split("]")[0].replace("[", "")
                src_ip = "Unknown"
                if "->" in line:
                    src_ip = line.split("->")[0].split("}")[-1].strip()

                alert_msg = (
                    f"\n🚨 <b>IoT Device Alert</b>\n"
                    f"🛡 <b>Type:</b> {alert_type}\n"
                    f"🕒 <b>Time:</b> {timestamp}\n"
                    f"🌐 <b>Attacker IP:</b> {src_ip}\n"
                    f"{'-'*30}"
                )
                all_alerts.append(alert_msg)
                sent_lines.append(line)

            # Send batched message
            if all_alerts:
                final_message = "\n".join(all_alerts)
                chunk_and_send(final_message)

                # Backup and cleanup
                os.makedirs("alert_backups", exist_ok=True)
                bkp_name = datetime.now().strftime("alert_backups/alerts_%Y%m%d_%H%M%S.txt")
                with open(bkp_name, "w") as bkp:
                    bkp.writelines(sent_lines)

    else:
        print("❌ alert.txt not found.")

    time.sleep(5)

