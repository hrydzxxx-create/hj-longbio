from flask import Flask, request, jsonify, make_response, render_template_string
import requests
import binascii
import jwt
import urllib3
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

try:
    import my_pb2
    import output_pb2
except ImportError:
    pass

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

FREEFIRE_VERSION = "OB53"

KEY = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
IV = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])

BIO_HEADERS = {
    "Expect": "100-continue",
    "X-Unity-Version": "2018.4.11f1",
    "X-GA": "v1 1",
    "ReleaseVersion": FREEFIRE_VERSION,
    "Content-Type": "application/x-www-form-urlencoded",
    "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 11; SM-A305F Build/RP1A.200720.012)",
    "Connection": "Keep-Alive",
    "Accept-Encoding": "gzip",
}

LOGIN_HEADERS = {
    "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; ASUS_Z01QD Build/PI)",
    "Connection": "Keep-Alive",
    "Accept-Encoding": "gzip",
    "Content-Type": "application/octet-stream",
    "Expect": "100-continue",
    "X-Unity-Version": "2018.4.11f1",
    "X-GA": "v1 1",
    "ReleaseVersion": FREEFIRE_VERSION
}

# Region configuration
REGION_CONFIG = {
    "IND": {  # India
        "login": "https://loginbp.ggpolarbear.com",
        "server": "https://client.ind.freefiremobile.com"
    },
    "ME": {  # Middle East
        "login": "https://loginbp.ggpolarbear.com",
        "server": "https://clientbp.ggblueshark.com"
    },
    "VN": {  # Vietnam
        "login": "https://loginbp.ggpolarbear.com",
        "server": "https://clientbp.ggpolarbear.com"
    },
    "BD": {  # Bangladesh
        "login": "https://loginbp.ggpolarbear.com",
        "server": "https://clientbp.ggpolarbear.com"
    },
    "PK": {  # Pakistan
        "login": "https://loginbp.ggpolarbear.com",
        "server": "https://clientbp.ggblueshark.com"
    },
    "SG": {  # Singapore
        "login": "https://loginbp.ggpolarbear.com",
        "server": "https://clientbp.ggpolarbear.com"
    },
    "BR": {  # Brazil
        "login": "https://loginbp.ggpolarbear.com",
        "server": "https://client.us.freefiremobile.com"
    },
    "NA": {  # North America
        "login": "https://loginbp.ggpolarbear.com",
        "server": "https://client.us.freefiremobile.com"
    },
    "ID": {  # Indonesia
        "login": "https://loginbp.ggpolarbear.com",
        "server": "https://clientbp.ggpolarbear.com"
    },
    "RU": {  # Russia
        "login": "https://loginbp.ggpolarbear.com",
        "server": "https://clientbp.ggpolarbear.com"
    },
    "TH": {  # Thailand
        "login": "https://loginbp.ggpolarbear.com",
        "server": "https://clientbp.ggpolarbear.com"
    }
}

DEFAULT_REGION = "ME"

_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\ndata.proto\"\xbb\x01\n\x04\x44\x61ta\x12\x0f\n\x07\x66ield_2\x18\x02 \x01(\x05\x12\x1e\n\x07\x66ield_5\x18\x05 \x01(\x0b\x32\r.EmptyMessage\x12\x1e\n\x07\x66ield_6\x18\x06 \x01(\x0b\x32\r.EmptyMessage\x12\x0f\n\x07\x66ield_8\x18\x08 \x01(\t\x12\x0f\n\x07\x66ield_9\x18\t \x01(\x05\x12\x1f\n\x08\x66ield_11\x18\x0b \x01(\x0b\x32\r.EmptyMessage\x12\x1f\n\x08\x66ield_12\x18\x0c \x01(\x0b\x32\r.EmptyMessage\"\x0e\n\x0c\x45mptyMessageb\x06proto3'
)
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'data1_pb2', _globals)
BioData = _sym_db.GetSymbol('Data')
EmptyMessage = _sym_db.GetSymbol('EmptyMessage')

def encrypt_data(data_bytes):
    cipher = AES.new(KEY, AES.MODE_CBC, IV)
    padded = pad(data_bytes, AES.block_size)
    return cipher.encrypt(padded)

def get_name_region_from_reward(access_token):
    try:
        uid_url = "https://prod-api.reward.ff.garena.com/redemption/api/auth/inspect_token/"
        uid_headers ={
            "authority": "prod-api.reward.ff.garena.com",
            "method": "GET",
            "path": "/redemption/api/auth/inspect_token/",
            "scheme": "https",
            "accept": "application/json, text/plain, */*",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "access-token": access_token,
            "cookie": "_gid=GA1.2.444482899.1724033242; _ga_XB5PSHEQB4=GS1.1.1724040177.1.1.1724040732.0.0.0; token_session=cb73a97aaef2f1c7fd138757dc28a08f92904b1062e66c; _ga_KE3SY7MRSD=GS1.1.1724041788.0.0.1724041788.0; _ga_RF9R6YT614=GS1.1.1724041788.0.0.1724041788.0; _ga=GA1.1.1843180339.1724033241; apple_state_key=817771465df611ef8ab00ac8aa985783; _ga_G8QGMJPWWV=GS1.1.1724049483.1.1.1724049880.0.0; datadome=HBTqAUPVsbBJaOLirZCUkN3rXjf4gRnrZcNlw2WXTg7bn083SPey8X~ffVwr7qhtg8154634Ee9qq4bCkizBuiMZ3Qtqyf3Isxmsz6GTH_b6LMCKWF4Uea_HSPk;",
            "origin": "https://reward.ff.garena.com",
            "referer": "https://reward.ff.garena.com/",
            "sec-ch-ua": '"Not.A/Brand";v="99", "Chromium";v="124"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Android"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        }
        uid_res = requests.get(uid_url, headers=uid_headers, verify=False)
        uid_data = uid_res.json()
        return uid_data.get("uid"), uid_data.get("name"), uid_data.get("region")
    except Exception as e:
        return None, None, None

def get_openid_from_shop2game(uid):
    if not uid: return None
    try:
        openid_url = "https://topup.pk/api/auth/player_id_login"
        openid_headers = {
            "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-MM,en-US;q=0.9,en;q=0.8",
        "Content-Type": "application/json",
        "Origin": "https://topup.pk",
        "Referer": "https://topup.pk/",
        "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Android WebView";v="138"',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"Android"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Linux; Android 15; RMX5070 Build/UKQ1.231108.001) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.7204.157 Mobile Safari/537.36",
        "X-Requested-With": "mark.via.gp",
        "Cookie": "source=mb; region=PK; mspid2=13c49fb51ece78886ebf7108a4907756; _fbp=fb.1.1753985808817.794945392376454660; language=en; datadome=WQaG3HalUB3PsGoSXY3TdcrSQextsSFwkOp1cqZtJ7Ax4YkiERHUgkgHlEAIccQO~w8dzTGM70D9SzaH7vymmEqOrVeX5pIsPVE22Uf3TDu6W3WG7j36ulnTg2DltRO7; session_key=hq02g63z3zjcumm76mafcooitj7nc79y",
        }
        payload = {"app_id": 100067, "login_id": str(uid)}
        res = requests.post(openid_url, headers=openid_headers, json=payload, verify=False)
        data = res.json()
        return data.get("open_id")
    except Exception as e:
        return None

def decode_jwt_info(token):
    try:
        decoded = jwt.decode(token, options={"verify_signature": False})
        name = decoded.get("nickname")
        region = decoded.get("lock_region")
        uid = decoded.get("account_id")
        return str(uid), name, region
    except:
        return None, None, None

def perform_major_login(access_token, open_id, login_url):
    platforms = [8, 3, 4, 6]
    for platform_type in platforms:
        try:
            game_data = my_pb2.GameData()
            game_data.timestamp = "2024-12-05 18:15:32"
            game_data.game_name = "free fire"
            game_data.game_version = 1
            game_data.version_code = "1.123.4"
            game_data.os_info = "Android OS 9 / API-28 (PI/rel.cjw.20220518.114133)"
            game_data.device_type = "Handheld"
            game_data.network_provider = "Verizon Wireless"
            game_data.connection_type = "WIFI"
            game_data.screen_width = 1280
            game_data.screen_height = 960
            game_data.dpi = "240"
            game_data.cpu_info = "ARMv7 VFPv3 NEON VMH | 2400 | 4"
            game_data.total_ram = 5951
            game_data.gpu_name = "Adreno (TM) 640"
            game_data.gpu_version = "OpenGL ES 3.0"
            game_data.user_id = "Google|74b585a9-0268-4ad3-8f36-ef41d2e53610"
            game_data.ip_address = "172.190.111.97"
            game_data.language = "en"
            game_data.open_id = open_id
            game_data.access_token = access_token
            game_data.platform_type = platform_type
            game_data.field_99 = str(platform_type)
            game_data.field_100 = str(platform_type)

            serialized_data = game_data.SerializeToString()
            encrypted = encrypt_data(serialized_data)
            hex_encrypted = binascii.hexlify(encrypted).decode('utf-8')

            edata = bytes.fromhex(hex_encrypted)
            major_login_url = f"{login_url}/MajorLogin"
            response = requests.post(major_login_url, data=edata, headers=LOGIN_HEADERS, verify=False, timeout=10)

            if response.status_code == 200:
                data_dict = None
                try:
                    example_msg = output_pb2.Garena_420()
                    example_msg.ParseFromString(response.content)
                    data_dict = {field.name: getattr(example_msg, field.name)
                                 for field in example_msg.DESCRIPTOR.fields
                                 if field.name == "token"}
                except Exception:
                    pass
                if data_dict and "token" in data_dict:
                    return data_dict["token"]
        except Exception:
            continue
    return None

def perform_guest_login(uid, password):
    payload = {
        'uid': uid,
        'password': password,
        'response_type': "token",
        'client_type': "2",
        'client_secret': "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3",
        'client_id': "100067"
    }
    headers = {
        'User-Agent': "GarenaMSDK/4.0.19P9(SM-M526B ;Android 13;pt;BR;)",
        'Connection': "Keep-Alive"
    }
    oauth_url = "https://100067.connect.garena.com/oauth/guest/token/grant"
    try:
        resp = requests.post(oauth_url, data=payload, headers=headers, timeout=10, verify=False)
        data = resp.json()
        if 'access_token' in data:
            return data['access_token'], data.get('open_id')
    except Exception as e:
        pass
    return None, None

def upload_bio_request(jwt_token, bio_text, server_url):
    try:
        data = BioData()
        data.field_2 = 17
        data.field_5.CopyFrom(EmptyMessage())
        data.field_6.CopyFrom(EmptyMessage())
        data.field_8 = bio_text
        data.field_9 = 1
        data.field_11.CopyFrom(EmptyMessage())
        data.field_12.CopyFrom(EmptyMessage())

        data_bytes = data.SerializeToString()
        encrypted = encrypt_data(data_bytes)

        headers = BIO_HEADERS.copy()
        headers["Authorization"] = f"Bearer {jwt_token}"

        update_url = f"{server_url}/UpdateSocialBasicInfo"
        resp = requests.post(update_url, headers=headers, data=encrypted, timeout=20, verify=False)

        status_text = "Unknown"
        if resp.status_code == 200: status_text = "Success"
        elif resp.status_code == 401: status_text = "Unauthorized (Invalid JWT)"
        else: status_text = f"Status {resp.status_code}"

        raw_hex = binascii.hexlify(resp.content).decode('utf-8')

        return {
            "status": status_text,
            "code": resp.status_code,
            "bio": bio_text,
            "server_response": raw_hex
        }
    except Exception as e:
        return {"status": f"Error: {str(e)}", "code": 500, "bio": bio_text, "server_response": "N/A"}

# ─────────────────────────────────────────────
# WEB INTERFACE TEMPLATE
# ─────────────────────────────────────────────
WEB_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>FF Bio Uploader</title>
<link href="https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&family=Share+Tech+Mono&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
<style>
:root{
  --bg:#0a0a0f;--bg2:#12121c;--card:rgba(22,22,37,.5);--border:#2a2a3a;
  --fg:#e8e6f0;--muted:#7a7890;--accent:#ff6b2b;--accent2:#ff3d00;
  --glow:rgba(255,107,43,.25);--ok:#00e676;--err:#ff1744;--warn:#ffc400;
}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Rajdhani',sans-serif;background:var(--bg);color:var(--fg);min-height:100vh;overflow-x:hidden}
#bgc{position:fixed;inset:0;z-index:0;pointer-events:none}
.bgg{position:fixed;inset:0;z-index:0;pointer-events:none;
  background:radial-gradient(ellipse 60% 40% at 20% 10%,rgba(255,61,0,.08) 0%,transparent 70%),
  radial-gradient(ellipse 50% 50% at 80% 80%,rgba(255,107,43,.06) 0%,transparent 70%)}
.wrap{position:relative;z-index:1;min-height:100vh;display:flex;flex-direction:column;align-items:center;padding:2rem 1rem 4rem}
.hdr{text-align:center;margin-bottom:2.5rem;animation:fsd .8s ease-out}
.hdr-badge{display:inline-flex;align-items:center;gap:.5rem;background:linear-gradient(135deg,var(--accent),var(--accent2));
  color:#fff;font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:2px;padding:.35rem 1rem;border-radius:20px;margin-bottom:1rem}
.hdr h1{font-size:clamp(2rem,5vw,3.2rem);font-weight:700;line-height:1.1;
  background:linear-gradient(135deg,#fff 0%,var(--accent) 60%,var(--accent2) 100%);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.hdr p{color:var(--muted);font-size:1rem;margin-top:.5rem}
.mc{width:100%;max-width:580px;background:var(--card);border:1px solid var(--border);border-radius:16px;
  backdrop-filter:blur(20px);overflow:hidden;animation:fsu .8s ease-out .15s both}
.ch{padding:1.25rem 1.5rem;border-bottom:1px solid var(--border);display:flex;align-items:center;gap:.75rem}
.ch i{color:var(--accent);font-size:1.1rem}.ch span{font-weight:700;font-size:1rem;letter-spacing:.5px}
.cb{padding:1.5rem}
.tabs{display:flex;gap:.35rem;background:var(--bg);border-radius:10px;padding:.3rem;margin-bottom:1.5rem}
.tb{flex:1;padding:.6rem .5rem;border:none;background:0 0;color:var(--muted);font-family:'Rajdhani',sans-serif;
  font-size:.8rem;font-weight:600;cursor:pointer;border-radius:8px;transition:.3s;text-align:center}
.tb:hover{color:var(--fg)}
.tb.on{background:linear-gradient(135deg,var(--accent),var(--accent2));color:#fff;box-shadow:0 4px 15px var(--glow)}
.tp{display:none}.tp.on{display:block;animation:fi .3s ease}
.fg{margin-bottom:1rem}
.fl{display:block;font-size:.75rem;font-weight:600;color:var(--muted);text-transform:uppercase;letter-spacing:1px;margin-bottom:.4rem}
.fi{width:100%;padding:.7rem .9rem;background:var(--bg);border:1px solid var(--border);border-radius:8px;
  color:var(--fg);font-family:'Share Tech Mono',monospace;font-size:.85rem;transition:.25s;outline:none}
.fi:focus{border-color:var(--accent);box-shadow:0 0 0 3px var(--glow)}
.fi::placeholder{color:#4a4860}
textarea.fi{resize:vertical;min-height:70px;font-family:'Rajdhani',sans-serif;font-size:.95rem}
.fs{width:100%;padding:.7rem .9rem;background:var(--bg);border:1px solid var(--border);border-radius:8px;
  color:var(--fg);font-family:'Rajdhani',sans-serif;font-size:.9rem;font-weight:600;outline:none;cursor:pointer;
  appearance:none;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8'%3E%3Cpath d='M1 1l5 5 5-5' stroke='%237a7890' stroke-width='1.5' fill='none'/%3E%3C/svg%3E");
  background-repeat:no-repeat;background-position:right .9rem center;transition:.25s}
.fs:focus{border-color:var(--accent);box-shadow:0 0 0 3px var(--glow)}
.fs option{background:var(--bg2);color:var(--fg)}
.sb{width:100%;padding:.85rem;border:none;border-radius:10px;font-family:'Rajdhani',sans-serif;
  font-size:1rem;font-weight:700;letter-spacing:1px;text-transform:uppercase;cursor:pointer;
  position:relative;overflow:hidden;background:linear-gradient(135deg,var(--accent),var(--accent2));
  color:#fff;transition:.2s;margin-top:.5rem}
.sb:hover{transform:translateY(-2px);box-shadow:0 8px 25px var(--glow)}
.sb:active{transform:translateY(0)}
.sb:disabled{opacity:.5;cursor:not-allowed;transform:none;box-shadow:none}
.sb .rp{position:absolute;inset:0;background:linear-gradient(90deg,transparent,rgba(255,255,255,.15),transparent);
  transform:translateX(-100%)}
.sb:not(:disabled) .rp{animation:shim 2s infinite}
.rp2{width:100%;max-width:580px;margin-top:1.5rem;display:none;animation:fsu .5s ease-out}
.rp2.vis{display:block}
.rc{background:var(--card);border:1px solid var(--border);border-radius:16px;backdrop-filter:blur(20px);overflow:hidden}
.rh{padding:1rem 1.5rem;border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between}
.rhl{display:flex;align-items:center;gap:.6rem}
.rhl i{font-size:1rem}.rhl span{font-weight:700;font-size:.95rem}
.badge{font-size:.7rem;font-weight:700;padding:.25rem .7rem;border-radius:20px;text-transform:uppercase;letter-spacing:1px}
.badge.ok{background:rgba(0,230,118,.15);color:var(--ok)}
.badge.err{background:rgba(255,23,68,.15);color:var(--err)}
.badge.wr{background:rgba(255,196,0,.15);color:var(--warn)}
.rb{padding:1.25rem 1.5rem}
.rr{display:flex;justify-content:space-between;align-items:flex-start;padding:.55rem 0;border-bottom:1px solid rgba(42,42,58,.5)}
.rr:last-child{border-bottom:none}
.rk{font-size:.75rem;font-weight:600;color:var(--muted);text-transform:uppercase;letter-spacing:.5px;min-width:120px;flex-shrink:0}
.rv{font-family:'Share Tech Mono',monospace;font-size:.8rem;color:var(--fg);text-align:right;word-break:break-all;max-width:360px;line-height:1.4}
.rv.cp{cursor:pointer}.rv.cp:hover{color:var(--accent)}
.toast{position:fixed;bottom:2rem;left:50%;transform:translateX(-50%) translateY(20px);background:var(--accent);
  color:#fff;font-size:.8rem;font-weight:600;padding:.5rem 1.2rem;border-radius:8px;opacity:0;pointer-events:none;
  transition:.3s;z-index:999}
.toast.show{opacity:1;transform:translateX(-50%) translateY(0)}
.lo{display:none;position:fixed;inset:0;z-index:100;background:rgba(10,10,15,.85);backdrop-filter:blur(8px);
  justify-content:center;align-items:center}
.lo.vis{display:flex}
.lsp{width:50px;height:50px;border:3px solid var(--border);border-top-color:var(--accent);border-radius:50%;
  animation:spin .8s linear infinite;margin:0 auto 1rem}
.lt{color:var(--muted);font-size:.9rem;font-weight:600}
.ft{margin-top:3rem;text-align:center;color:#3a3850;font-size:.75rem;animation:fi 1s ease .5s both}
.frow{display:flex;gap:.75rem}.frow .fg{flex:1}
@keyframes fsd{from{opacity:0;transform:translateY(-20px)}to{opacity:1;transform:translateY(0)}}
@keyframes fsu{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}
@keyframes fi{from{opacity:0}to{opacity:1}}
@keyframes spin{to{transform:rotate(360deg)}}
@keyframes shim{0%{transform:translateX(-100%)}100%{transform:translateX(100%)}}
::-webkit-scrollbar{width:6px}::-webkit-scrollbar-track{background:var(--bg)}
::-webkit-scrollbar-thumb{background:var(--border);border-radius:3px}
@media(max-width:500px){.wrap{padding:1.2rem .75rem 3rem}.cb,.rb{padding:1.1rem}
  .frow{flex-direction:column;gap:0}.rr{flex-direction:column;gap:.2rem}.rv{text-align:left;max-width:100%}}
@media(prefers-reduced-motion:reduce){*,*::before,*::after{animation-duration:.01ms!important;transition-duration:.01ms!important}}
</style>
</head>
<body>
<canvas id="bgc"></canvas><div class="bgg"></div>
<div class="wrap">
  <header class="hdr">
    <div class="hdr-badge"><i class="fa-solid fa-fire"></i> Free Fire Tool</div>
    <h1>Bio Uploader</h1>
    <p>Update in-game bio via JWT, UID/Password, or Access Token</p>
  </header>
  <div class="mc">
    <div class="ch"><i class="fa-solid fa-terminal"></i><span>Configuration</span></div>
    <div class="cb">
      <div class="tabs" role="tablist">
        <button class="tb on" data-t="jwt" role="tab" aria-selected="true">JWT Token</button>
        <button class="tb" data-t="uidpass" role="tab" aria-selected="false">UID / Pass</button>
        <button class="tb" data-t="access" role="tab" aria-selected="false">Access Token</button>
      </div>
      <div class="tp on" id="p-jwt">
        <div class="fg"><label class="fl" for="i-jwt">JWT Token</label>
          <textarea class="fi" id="i-jwt" placeholder="Paste your JWT token here..." rows="3"></textarea></div>
      </div>
      <div class="tp" id="p-uidpass">
        <div class="frow">
          <div class="fg"><label class="fl" for="i-uid">UID</label>
            <input class="fi" id="i-uid" type="text" placeholder="e.g. 1234567890"></div>
          <div class="fg"><label class="fl" for="i-pass">Password</label>
            <input class="fi" id="i-pass" type="password" placeholder="Account password"></div>
        </div>
      </div>
      <div class="tp" id="p-access">
        <div class="fg"><label class="fl" for="i-acc">Access Token</label>
          <textarea class="fi" id="i-acc" placeholder="Paste your access token here..." rows="3"></textarea></div>
      </div>
      <div class="fg"><label class="fl" for="i-bio">Bio Text</label>
        <textarea class="fi" id="i-bio" placeholder="Enter the new bio content..." rows="2"></textarea></div>
      <div class="fg"><label class="fl" for="i-reg">Server Region</label>
        <select class="fs" id="i-reg">
          <option value="ME">Middle East</option><option value="IND">India</option>
          <option value="VN">Vietnam</option><option value="BD">Bangladesh</option>
          <option value="PK">Pakistan</option><option value="SG">Singapore</option>
          <option value="BR">Brazil</option><option value="NA">North America</option>
          <option value="ID">Indonesia</option><option value="RU">Russia</option>
          <option value="TH">Thailand</option>
        </select></div>
      <button class="sb" id="go" type="button"><span class="rp"></span><i class="fa-solid fa-bolt"></i>&nbsp; Upload Bio</button>
    </div>
  </div>
  <div class="rp2" id="rp">
    <div class="rc">
      <div class="rh">
        <div class="rhl"><i class="fa-solid fa-circle-info"></i><span>Response</span></div>
        <span class="badge" id="bdg">--</span>
      </div>
      <div class="rb" id="rbd"></div>
    </div>
  </div>
  <footer class="ft">FF Bio Uploader &middot; For educational purposes only</footer>
</div>
<div class="lo" id="lo"><div style="text-align:center"><div class="lsp"></div><div class="lt">Processing request...</div></div></div>
<div class="toast" id="ct">Copied to clipboard</div>
<script>
(function(){
  var c=document.getElementById('bgc'),x=c.getContext('2d'),ps=[],N=60;
  function rz(){c.width=innerWidth;c.height=innerHeight}rz();addEventListener('resize',rz);
  function P(){this.r=function(){this.x=Math.random()*c.width;this.y=c.height+Math.random()*100;
    this.s=Math.random()*2.5+.5;this.vy=-(Math.random()*.6+.15);this.vx=(Math.random()-.5)*.3;
    this.o=Math.random()*.5+.1;this.h=Math.random()*30+10};this.r()}
  for(var i=0;i<N;i++){var p=new P();p.y=Math.random()*c.height;ps.push(p)}
  var rm=matchMedia('(prefers-reduced-motion:reduce)').matches;
  function anim(){if(rm)return;x.clearRect(0,0,c.width,c.height);
    ps.forEach(function(p){p.y+=p.vy;p.x+=p.vx;p.o-=.001;
      if(p.y<-10||p.o<=0)p.r();x.beginPath();x.arc(p.x,p.y,p.s,0,Math.PI*2);
      x.fillStyle='hsla('+p.h+',100%,60%,'+p.o+')';x.fill()});requestAnimationFrame(anim)}
  anim();
  var tbs=document.querySelectorAll('.tb'),tps=document.querySelectorAll('.tp');
  tbs.forEach(function(b){b.addEventListener('click',function(){
    tbs.forEach(function(t){t.classList.remove('on');t.setAttribute('aria-selected','false')});
    tps.forEach(function(t){t.classList.remove('on')});
    b.classList.add('on');b.setAttribute('aria-selected','true');
    var p=document.getElementById('p-'+b.dataset.t);if(p)p.classList.add('on')})});
  var go=document.getElementById('go'),rp=document.getElementById('rp'),
      rbd=document.getElementById('rbd'),bdg=document.getElementById('bdg'),
      lo=document.getElementById('lo'),ct=document.getElementById('ct'),cto;
  go.addEventListener('click',async function(){
    var at=document.querySelector('.tb.on').dataset.t,
        bio=document.getElementById('i-bio').value.trim(),
        reg=document.getElementById('i-reg').value;
    if(!bio){ie('Please enter a bio text.');return}
    var q=new URLSearchParams;q.set('bio',bio);q.set('region',reg);
    if(at==='jwt'){var v=document.getElementById('i-jwt').value.trim();if(!v){ie('Please enter a JWT token.');return}q.set('jwt',v)}
    else if(at==='uidpass'){var u=document.getElementById('i-uid').value.trim(),
        pw=document.getElementById('i-pass').value.trim();if(!u||!pw){ie('Please enter both UID and Password.');return}
        q.set('uid',u);q.set('pass',pw)}
    else{var ac=document.getElementById('i-acc').value.trim();if(!ac){ie('Please enter an Access Token.');return}q.set('access_token',ac)}
    lo.classList.add('vis');go.disabled=true;rp.classList.remove('vis');
    try{var r=await fetch('/bio_upload?'+q.toString()),d=await r.json();render(d)}
    catch(e){renderE('Network error: '+e.message)}finally{lo.classList.remove('vis');go.disabled=false}});
  function ie(m){go.style.background='linear-gradient(135deg,#ff1744,#d50000)';
    go.innerHTML='<i class="fa-solid fa-triangle-exclamation"></i>&nbsp; '+m;
    setTimeout(function(){go.style.background='';go.innerHTML='<span class="rp"></span><i class="fa-solid fa-bolt"></i>&nbsp; Upload Bio'},2500)}
  function esc(s){var d=document.createElement('div');d.textContent=s;return d.innerHTML}
  function render(d){
    var ok=String(d.code).startsWith('2')||d.status.indexOf('Success')!==-1,
        wr=!ok&&!String(d.code).startsWith('4')&&!String(d.code).startsWith('5');
    bdg.textContent=ok?'Success':wr?'Warning':'Error';
    bdg.className='badge '+(ok?'ok':wr?'wr':'err');
    document.querySelector('.rhl i').className='fa-solid '+(ok?'fa-circle-check':wr?'fa-triangle-exclamation':'fa-circle-xmark');
    var rows=[['Status',d.status,0],['Login Method',d.login_method||'N/A',0],['HTTP Code',String(d.code),0],
      ['UID',d.uid||'N/A',1],['Region',[d.region,d.selected_region].filter(Boolean).join(' / ')||'N/A',0],
      ['Open ID',d.open_id||'N/A',1],['Bio Sent',d.bio||'N/A',0],
      ['Access Token',d.access_token||'N/A',1],['Generated JWT',d.generated_jwt||'N/A',1],
      ['Server Response',d.server_response||'N/A',1]];
    rbd.innerHTML=rows.map(function(r){return '<div class="rr"><span class="rk">'+r[0]+'</span><span class="rv'+(r[1]?' cp':'')+'" title="Click to copy">'+esc(String(r[1]))+'</span></div>'}).join('');
    rbd.querySelectorAll('.cp').forEach(function(el){el.addEventListener('click',function(){cp(el.textContent)})});
    rp.classList.add('vis');rp.scrollIntoView({behavior:'smooth',block:'nearest'})}
  function renderE(m){bdg.textContent='Error';bdg.className='badge err';
    document.querySelector('.rhl i').className='fa-solid fa-circle-xmark';
    rbd.innerHTML='<div class="rr"><span class="rk">Error</span><span class="rv">'+esc(m)+'</span></div>';
    rp.classList.add('vis')}
  function cp(t){if(!t||t==='N/A')return;navigator.clipboard.writeText(t).then(function(){
    ct.classList.add('show');clearTimeout(cto);cto=setTimeout(function(){ct.classList.remove('show')},1500)}).catch(function(){})}
  document.addEventListener('keydown',function(e){if(e.key==='Enter'&&!e.shiftKey&&e.target.tagName!=='TEXTAREA'){e.preventDefault();go.click()}});
})();
</script>
</body>
</html>"""


@app.route("/")
def index():
    """Serve the web interface."""
    return render_template_string(WEB_HTML)


@app.route("/bio_upload", methods=["GET", "POST"])
def combined_bio_upload():
    bio = request.args.get("bio") or request.form.get("bio")
    jwt_token = request.args.get("jwt") or request.form.get("jwt")
    uid = request.args.get("uid") or request.form.get("uid")
    password = request.args.get("pass") or request.form.get("pass")
    access_token = request.args.get("access") or request.form.get("access") or request.args.get("access_token")
    region = (request.args.get("region") or request.form.get("region") or DEFAULT_REGION).upper()

    if not bio:
        return jsonify({"status": "Error", "code": 400, "error": "Missing 'bio' parameter"}), 400

    if region not in REGION_CONFIG:
        return jsonify({"status": "Error", "code": 400, "error": f"Unsupported region '{region}'. Supported: {list(REGION_CONFIG.keys())}"}), 400

    login_url = REGION_CONFIG[region]["login"]
    server_url = REGION_CONFIG[region]["server"]

    final_jwt = None
    login_method = "Direct JWT"

    final_open_id = None
    final_access_token = None
    final_uid = None
    final_name = None
    final_region = None

    if jwt_token:
        final_jwt = jwt_token
        j_uid, j_name, j_region = decode_jwt_info(jwt_token)
        final_uid = j_uid
        final_name = j_name
        final_region = j_region

    elif uid and password:
        login_method = "UID/Pass Login"

        acc_token, login_openid = perform_guest_login(uid, password)

        if acc_token and login_openid:
            final_access_token = acc_token
            final_open_id = login_openid

            final_jwt = perform_major_login(final_access_token, final_open_id, login_url)

            if final_jwt:
                 j_uid, j_name, j_region = decode_jwt_info(final_jwt)
                 final_uid = j_uid
                 final_name = j_name
                 final_region = j_region
            else:
                 return jsonify({"status": "JWT Generation Failed", "code": 500}), 500

        else:
            return jsonify({"status": "Guest Login Failed (Check UID/Pass)", "code": 401}), 401

    elif access_token:
        login_method = "Access Token Login"
        final_access_token = access_token

        f_uid, f_name, f_region = get_name_region_from_reward(access_token)
        final_uid = f_uid
        final_name = f_name
        final_region = f_region

        if not final_uid:
            return jsonify({"status": "Invalid Access Token", "code": 400}), 400

        final_open_id = get_openid_from_shop2game(final_uid)

        if final_open_id:
            final_jwt = perform_major_login(access_token, final_open_id, login_url)
        else:
            return jsonify({"status": "Shop2Game OpenID Fetch Failed", "code": 400}), 400

    else:
        return jsonify({"status": "Error", "code": 400, "error": "Provide JWT, or UID/Pass, or Access Token"}), 400

    if not final_jwt:
        return jsonify({"status": "JWT Generation Failed", "code": 500}), 500

    result = upload_bio_request(final_jwt, bio, server_url)

    response_data = {
        "status": result["status"],
        "login_method": login_method,
        "code": result["code"],
        "bio": result["bio"],
        "uid": str(final_uid) if final_uid else None,
        "region": final_region,
        "selected_region": region,
        "open_id": final_open_id,
        "access_token": final_access_token,
        "server_response": result["server_response"],
        "generated_jwt": final_jwt
    }

    response = make_response(jsonify(response_data))
    response.headers["Content-Type"] = "application/json"
    return response

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)