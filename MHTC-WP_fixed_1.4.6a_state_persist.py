# MHTC-WP_fixed_1.4.6a_state_persist.py
# Hotfix: break one-line "q=...; if ..." into valid multi-line Python
# (Full script included for drop-in replacement.)

import os, time, re, json, random, base64, subprocess, shutil
from pathlib import Path
from typing import Optional, List, Tuple
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

CDP_URL = "http://localhost:9222"
STATE_FILE = str(Path("state") / "comet_welcome_state.json")
EMAILS_FILE = "emails.txt"
REG_LINKS_FILE = "registration_links.txt"
REGISTRATION_URL_FALLBACK = "https://www.perplexity.ai/browser/claim-invite"
FINAL_URL = "https://example.com/final"
FINAL_TEXT_TO_ENTER = "hello from automation"
CLAIM_TEXTS = ["claim invitation", "claim", "get invite", "nhận lời mời"]
CLAIM_WAIT_TIMEOUT_MS = 20000
SELECTOR_EMAIL_INPUT = "input[type='email'], input[name='email'], input[autocomplete='email']"
SELECTOR_SUBMIT_BTN  = "button[type='submit'], input[type='submit'], [role='button']"
SELECTOR_OTP_INPUT   = "input[name='otp'], input[type='tel'], input[autocomplete='one-time-code'], input[data-otp]"
OTP_CONFIG_FILE = "otp_config.json"
OTP_SEARCH_TIMEOUT = 120
OTP_POLL_INTERVAL = 5
PERPLEXITY_HOME = "https://www.perplexity.ai/b/home"
SEARCH_TEXTS = ["ai tools list","how to use perplexity","best ai image generator","how to get invite","perplexity ai review","top ai browsers","tìm kiếm mẫu tiếng việt","tin tức ai hôm nay"]
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly','https://www.googleapis.com/auth/gmail.modify']
CREDENTIALS_FILE = "credentials.json"
STEP_DELAY_RANGE = (3.0, 8.0)
POST_SEARCH_SCRIPT = "display.bat"
RUN_POST_SCRIPT_AFTER_STEP75 = True
RUN_LOGIN_AFTER_LOGOUT = True
LOGIN_USERNAME = "administrator"
LOGIN_PASSWORD = "Lktoday@321"
LOGIN_URLS = ["https://www.perplexity.ai/signin","https://www.perplexity.ai/login"]
LOGOUT_TRIGGERS = ["Sign out","Log out","Đăng xuất","Sign Out","Logout","Log Out"]
USERNAME_SELECTORS = ["input[name='username']","input[id='username']","input[name='user']","input[id='user']","input[type='text']"]
PASSWORD_SELECTORS = ["input[type='password']","input[name='password']","input[id='password']"]
SUBMIT_SELECTORS   = ["button[type='submit']","input[type='submit']","button:has-text('Sign in')","button:has-text('Log in')","button:has-text('Đăng nhập')"]

def ensure_state_folder():
    p = Path(STATE_FILE).expanduser().resolve()
    p.parent.mkdir(parents=True, exist_ok=True)
    return str(p)

def human_sleep(min_s=0.5, max_s=1.5):
    time.sleep(random.uniform(min_s, max_s))

def between_steps_sleep():
    lo, hi = STEP_DELAY_RANGE
    time.sleep(random.uniform(lo, hi))

def human_typing_delay():
    return random.uniform(0.04, 0.18)

def human_move_and_click(page, locator_or_point, click_delay=(0.05, 0.18)):
    try:
        if isinstance(locator_or_point, tuple):
            x, y = locator_or_point
            page.mouse.move(x + random.uniform(-5,5), y + random.uniform(-5,5), steps=random.randint(5,15))
            human_sleep(*click_delay)
            page.mouse.click(x, y)
            return True
        else:
            el = locator_or_point
            box = el.bounding_box()
            if not box:
                return False
            cx = box["x"] + box["width"]/2 + random.uniform(-8,8)
            cy = box["y"] + box["height"]/2 + random.uniform(-6,6)
            page.mouse.move(cx, cy, steps=random.randint(8,20))
            human_sleep(0.08, 0.28)
            page.mouse.click(cx, cy)
            return True
    except Exception:
        try:
            locator_or_point.click()
            return True
        except Exception:
            return False

def human_type(page, selector_or_el, text: str):
    try:
        el = page.query_selector(selector_or_el) if isinstance(selector_or_el, str) else selector_or_el
        if not el:
            return False
        el.click()
        human_sleep(0.05, 0.18)
        for ch in text:
            page.keyboard.insert_text(ch)
            time.sleep(human_typing_delay())
        human_sleep(0.1, 0.35)
        return True
    except Exception:
        try:
            if isinstance(selector_or_el, str):
                page.evaluate(
                    """(s, v) => { const el = document.querySelector(s); if(!el) return false;
                                   el.value = v;
                                   el.dispatchEvent(new Event('input', {bubbles:true}));
                                   el.dispatchEvent(new Event('change', {bubbles:true}));
                                   return true; }""",
                    selector_or_el, text
                )
                return True
        except Exception:
            return False
    return False

def read_nonempty_lines(path: Path) -> List[str]:
    if not path.exists():
        return []
    return [ln.strip() for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]

def peek_first_email(path: Path) -> Optional[str]:
    lines = read_nonempty_lines(path)
    return lines[0] if lines else None

def pop_first_email_if(peek_email: str, path: Path) -> None:
    lines = read_nonempty_lines(path)
    removed = False
    new_lines = []
    for ln in lines:
        if not removed and ln.strip() == peek_email:
            removed = True
            continue
        new_lines.append(ln)
    path.write_text("\n".join(new_lines) + ("\n" if new_lines else ""), encoding="utf-8")

def pick_random_registration_url(path: Path) -> str:
    links = read_nonempty_lines(path)
    if not links:
        return REGISTRATION_URL_FALLBACK
    return random.choice(links)

def load_otp_config():
    if not os.path.exists(OTP_CONFIG_FILE):
        raise FileNotFoundError(f"{OTP_CONFIG_FILE} missing.")
    with open(OTP_CONFIG_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    data.setdefault("unread_only", True)
    data.setdefault("newest_only", True)
    data.setdefault("mark_read_after", False)
    data.setdefault("otp_subject_exact", "Sign in to Perplexity")
    data.setdefault("subject_match_mode", "exact")
    for k in ("otp_inbox_account", "search_query", "code_regex"):
        if not data.get(k):
            raise ValueError(f"Missing {k} in {OTP_CONFIG_FILE}")
    return data

def get_gmail_service_for(account_email: str):
    token_file = f"token_{account_email.replace('@','_at_')}.json"
    creds = None
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    if not creds or not creds.valid:
        from google.auth.transport.requests import Request
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError("credentials.json missing.")
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_file, "w") as f:
            f.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def extract_plain_text_from_message(msg) -> str:
    payload = msg.get('payload', {})
    def decode_data(data):
        if not data:
            return ""
        b = base64.urlsafe_b64decode(data + "==")
        return b.decode('utf-8', errors='ignore')
    if payload.get('body', {}).get('data'):
        return decode_data(payload['body']['data'])
    parts = payload.get('parts') or []
    for part in parts:
        if part.get('mimeType') == 'text/plain' and part.get('body', {}).get('data'):
            return decode_data(part['body']['data'])
        if part.get('parts'):
            for sp in part['parts']:
                if sp.get('mimeType') == 'text/plain' and sp.get('body', {}).get('data'):
                    return decode_data(sp['body']['data'])
    return msg.get('snippet', '')

def _gmail_list_messages(service, q: str, max_results: int = 20) -> List[Tuple[str, int]]:
    resp = service.users().messages().list(userId='me', q=q, maxResults=max_results).execute()
    msgs = []
    for it in resp.get('messages', []):
        mid = it['id']
        full_meta = service.users().messages().get(userId='me', id=mid, format='metadata').execute()
        internal_ts = int(full_meta.get('internalDate', 0))
        msgs.append((mid, internal_ts))
    msgs.sort(key=lambda x: x[1], reverse=True)
    return msgs

def _norm_subject(s: str) -> str:
    return (s or "").strip().lower()

def search_messages_for_otp_fixed_account(service, search_query: str, subject_regex: str, code_regex: str,
                                          timeout=OTP_SEARCH_TIMEOUT, poll_interval=OTP_POLL_INTERVAL,
                                          unread_only: bool = True, newest_only: bool = True,
                                          mark_read_after: bool = False,
                                          subject_match_mode: str = "exact",
                                          otp_subject_exact: str = "Sign in to Perplexity") -> Optional[str]:
    print(f"[STEP_50_WAIT_OTP] Polling Gmail q={search_query!r} mode={subject_match_mode} exact='{otp_subject_exact}' unread_only={unread_only} newest_only={newest_only} timeout={timeout}s")
    deadline = time.time() + timeout
    subj_p = re.compile(subject_regex, re.IGNORECASE) if subject_regex and subject_match_mode == "regex" else None
    code_p = re.compile(code_regex)

    # FIXED: multi-line statements
    q = search_query.strip()
    if unread_only and "label:unread" not in q:
        q = (q + " label:unread").strip()

    exact_norm = _norm_subject(otp_subject_exact) if otp_subject_exact else None

    while time.time() < deadline:
        try:
            candidates = _gmail_list_messages(service, q, max_results=20)
            if newest_only:
                candidates = candidates[:5]
            for mid, _ts in candidates:
                full = service.users().messages().get(userId='me', id=mid, format='full').execute()
                headers = {h['name'].lower(): h['value'] for h in full.get('payload', {}).get('headers', [])}
                subject = headers.get('subject', '')

                match_subject = False
                if subject_match_mode == "exact" and exact_norm:
                    match_subject = (_norm_subject(subject) == exact_norm)
                elif subject_match_mode == "regex" and subj_p:
                    match_subject = bool(subj_p.search(subject or ""))
                else:
                    match_subject = otp_subject_exact.lower() in (subject or "").lower()

                if not match_subject:
                    continue

                body = extract_plain_text_from_message(full)
                m = code_p.search(body or "")
                if m:
                    code = m.group(1)
                    print(f"[STEP_50_WAIT_OTP] Found OTP: {code} (subject={subject})")
                    if mark_read_after:
                        try:
                            service.users().messages().modify(
                                userId='me', id=mid,
                                body={"removeLabelIds": ["UNREAD"]}
                            ).execute()
                            print("[STEP_50_WAIT_OTP] Marked message as READ")
                        except Exception as e:
                            print("[STEP_50_WAIT_OTP] Mark read failed:", e)
                    return code
        except Exception as e:
            print("[GMAIL] poll error:", e)
        time.sleep(poll_interval)
    print("[STEP_50_WAIT_OTP] OTP not found in time.")
    return None

def click_claim_button(page) -> bool:
    try:
        for txt in CLAIM_TEXTS:
            sel_variants = [f"button:has-text('{txt}')", f"[role=button]:has-text('{txt}')", f"text={txt}"]
            for sel in sel_variants:
                try:
                    page.wait_for_selector(sel, timeout=3000)
                    el = page.locator(sel).first
                    el.scroll_into_view_if_needed()
                    human_sleep(0.12, 0.4)
                    human_move_and_click(page, el)
                    print(f"[STEP_35_CLICK_CLAIM] Clicked via selector {sel}")
                    return True
                except Exception:
                    pass
        js = f"""
        () => {{
          function norm(t){{return (t||'').trim().toLowerCase().replace(/\\s+/g,' ');}}
          const texts = {CLAIM_TEXTS!r};
          const all = Array.from(document.querySelectorAll('button, a, [role=\\"button\\"]'));
          const found = all.find(el => {{
            const label = norm(el.innerText || el.textContent || el.getAttribute('aria-label'));
            return texts.some(t => label.includes(t));
          }});
          if(found){{ found.scrollIntoView({{block:'center',inline:'center'}}); found.click(); return true; }}
          return false;
        }}
        """
        t0 = time.time()
        while (time.time()-t0)*1000 < CLAIM_WAIT_TIMEOUT_MS:
            ok = page.evaluate(js)
            if ok:
                print("[STEP_35_CLICK_CLAIM] Clicked via JS fallback")
                return True
            time.sleep(0.3)
        print("[STEP_35_CLICK_CLAIM] Claim button not found")
        return False
    except Exception as e:
        print("[STEP_35_CLICK_CLAIM] error:", e)
        return False

def submit_email(page, email: str) -> bool:
    try:
        page.wait_for_selector(SELECTOR_EMAIL_INPUT, timeout=15000)
        ok_type = human_type(page, SELECTOR_EMAIL_INPUT, email)
        if not ok_type:
            page.fill(SELECTOR_EMAIL_INPUT, email)
        human_sleep(0.12, 0.4)
        try:
            el = page.query_selector(SELECTOR_SUBMIT_BTN)
            if el:
                human_move_and_click(page, el)
            else:
                page.keyboard.press("Enter")
        except Exception:
            page.keyboard.press("Enter")
        print(f"[STEP_40_ENTER_EMAIL] Submitted email {email}")
        return True
    except Exception as e:
        print("[STEP_40_ENTER_EMAIL] error:", e)
        return False

def enter_otp_and_submit(page, code: str) -> bool:
    try:
        page.wait_for_selector(SELECTOR_OTP_INPUT, timeout=15000)
        ok = human_type(page, SELECTOR_OTP_INPUT, code)
        if not ok:
            page.fill(SELECTOR_OTP_INPUT, code)
        human_sleep(0.08, 0.25)
        try:
            el = page.query_selector(SELECTOR_SUBMIT_BTN)
            if el:
                human_move_and_click(page, el)
            else:
                page.keyboard.press("Enter")
        except Exception:
            page.keyboard.press("Enter")
        print("[STEP_60_ENTER_OTP] OTP entered & submitted")
        return True
    except PWTimeout:
        try:
            human_type(page, "input", code)
            page.keyboard.press("Enter")
            print("[STEP_60_ENTER_OTP] OTP blind-typed & Enter sent")
            return True
        except Exception as e:
            print("[STEP_60_ENTER_OTP] blind type failed:", e)
            return False
    except Exception as e:
        print("[STEP_60_ENTER_OTP] error:", e)
        return False

def final_action(page):
    try:
        page.goto(FINAL_URL, wait_until="load", timeout=30000)
        human_sleep(0.8, 1.6)
        target = page.query_selector("input, textarea, [contenteditable='true']")
        if target:
            human_type(page, target, FINAL_TEXT_TO_ENTER)
            human_sleep(0.5, 1.2)
            print("[STEP_70_FINAL_ACTION] done")
            return True
        print("[STEP_70_FINAL_ACTION] no input found")
        return False
    except Exception as e:
        print("[STEP_70_FINAL_ACTION] error:", e)
        return False

def step_75_search_home(page, texts_pool=SEARCH_TEXTS, times=3, gap_seconds=5) -> bool:
    did_any = False
    try:
        page.goto(PERPLEXITY_HOME, wait_until="domcontentloaded", timeout=30000)
    except Exception as e:
        print("[STEP_75_SEARCH_HOME] open home error:", e)
        return False

    human_sleep(0.8, 1.6)
    for i in range(1, times + 1):
        try:
            possible = [
                "input[type='search']",
                "input[name='q']",
                "input[placeholder*='Search']",
                "textarea[placeholder*='Search']",
                "input[aria-label*='Search']",
                "[role='search'] input",
                "input"
            ]
            el = None
            for s in possible:
                e = page.query_selector(s)
                if e and e.bounding_box():
                    el = e
                    break
            if not el:
                el = page.query_selector("[contenteditable='true']")
            if not el:
                print(f"[STEP_75_SEARCH_HOME] search input not found (try {i}/{times})")
                human_sleep(0.6, 1.4)
                continue

            text = random.choice(texts_pool)
            if not human_type(page, el, text):
                try:
                    el.fill(text)
                except Exception:
                    pass
            human_sleep(0.4, 1.0)

            try:
                page.keyboard.press("Enter")
            except Exception:
                btn = page.query_selector("button[type='submit'], button:has-text('Search')")
                if btn:
                    human_move_and_click(page, btn)
            print(f"[STEP_75_SEARCH_HOME] ({i}/{times}) searched: {text}")
            did_any = True

            human_sleep(1.2, 2.5)
            if i < times:
                time.sleep(gap_seconds)
        except Exception as e:
            print(f"[STEP_75_SEARCH_HOME] try {i}/{times} error:", e)
            human_sleep(0.8, 1.6)
    return did_any

def load_context_with_state(browser):
    safe_state_path = ensure_state_folder()
    if os.path.exists(safe_state_path):
        print(f"[STATE] Loading storage_state from {safe_state_path}")
        return browser.new_context(storage_state=safe_state_path)
    else:
        print("[STATE] No storage_state found; creating plain context.")
        return browser.new_context()

def maybe_export_state(ctx):
    safe_state_path = ensure_state_folder()
    try:
        ctx.storage_state(path=safe_state_path)
        print(f"[STATE] Exported storage_state to {safe_state_path}")
    except Exception as e:
        print("[STATE] Export failed:", e)

def try_logout(page) -> bool:
    tried = False
    try:
        menu_candidates = [
            "[data-testid='user-menu']","[aria-label*='account']","[aria-label*='menu']",
            "button:has([data-testid='avatar'])","button[aria-label*='profile']"
        ]
        for msel in menu_candidates:
            el = page.query_selector(msel)
            if el:
                el.click()
                human_sleep(0.2, 0.6)
                break
    except Exception:
        pass

    for text in LOGOUT_TRIGGERS:
        sel = f"text={text}"
        try:
            if page.query_selector(sel):
                human_move_and_click(page, page.locator(sel).first)
                tried = True
                print(f"[LOGOUT] Clicked {text}")
                break
        except Exception:
            continue

    human_sleep(0.8, 1.6)
    return tried

def find_first(page, selectors: List[str]):
    for s in selectors:
        el = page.query_selector(s)
        if el and el.bounding_box():
            return el
    return None

def login_with_username_password(page, username: str, password: str) -> bool:
    def do_login_on_current() -> bool:
        user_el = find_first(page, USERNAME_SELECTORS)
        pass_el = find_first(page, PASSWORD_SELECTORS)
        if not user_el or not pass_el:
            return False
        if not human_type(page, user_el, username):
            try: user_el.fill(username)
            except Exception: return False
        human_sleep(0.1, 0.3)
        if not human_type(page, pass_el, password):
            try: pass_el.fill(password)
            except Exception: return False
        human_sleep(0.1, 0.3)
        btn = find_first(page, SUBMIT_SELECTORS)
        if btn:
            human_move_and_click(page, btn)
        else:
            page.keyboard.press("Enter")
        print("[LOGIN] Submitted username/password")
        human_sleep(2.0, 3.0)
        return True

    if do_login_on_current():
        return True
    for url in LOGIN_URLS:
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=20000)
            human_sleep(0.6, 1.2)
            if do_login_on_current():
                return True
        except Exception:
            continue
    print("[LOGIN] No compatible username/password form found.")
    return False

def run_post_search_script() -> bool:
    try:
        script = os.path.join(os.getcwd(), POST_SEARCH_SCRIPT)
        if not os.path.exists(script):
            print(f"[POST] Script not found: {script}")
            return False

        ext = os.path.splitext(script)[1].lower()
        if ext == ".ps1":
            pwsh = shutil.which("pwsh") or shutil.which("powershell")
            if not pwsh:
                print("[POST] PowerShell not found on PATH")
                return False
            cmd = [pwsh, "-ExecutionPolicy", "Bypass", "-File", script]
        elif ext in (".bat", ".cmd"):
            cmd = ["cmd", "/c", script]
        else:
            print(f"[POST] Unsupported script type: {ext}")
            return False

        print(f"[POST] Running: {' '.join(cmd)}")
        rc = subprocess.run(cmd, cwd=os.getcwd(), shell=False).returncode
        print(f"[POST] Exit code: {rc}")
        return rc == 0
    except Exception as e:
        print("[POST] error:", e)
        return False

def main():
    emails_path = Path(EMAILS_FILE)
    reg_links_path = Path(REG_LINKS_FILE)

    otp_cfg = load_otp_config()
    otp_account = otp_cfg["otp_inbox_account"]
    otp_query = otp_cfg["search_query"]
    otp_subj_rx = otp_cfg.get("subject_regex", "")
    otp_code_rx = otp_cfg["code_regex"]
    unread_only = bool(otp_cfg.get("unread_only", True))
    newest_only = bool(otp_cfg.get("newest_only", True))
    mark_read_after = bool(otp_cfg.get("mark_read_after", False))
    subject_match_mode = str(otp_cfg.get("subject_match_mode", "exact")).lower()
    otp_subject_exact = otp_cfg.get("otp_subject_exact", "Sign in to Perplexity")

    gmail = get_gmail_service_for(otp_account)
    print("[INFO] Using OTP inbox:", otp_account)

    ensure_state_folder()

    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp(CDP_URL)
        except Exception as e:
            print("CDP connect failed:", e)
            return

        ctx = load_context_with_state(browser)
        page = ctx.new_page()

        email = peek_first_email(emails_path)
        if not email:
            print("[EXIT] No email in emails.txt")
            return

        reg_url = pick_random_registration_url(reg_links_path)
        print(f"[RUN] email={email} | link={reg_url}")

        try:
            page.goto(reg_url, wait_until="domcontentloaded", timeout=30000)
        except Exception as e:
            print("[STEP_30_OPEN_PAGE] open error:", e)
            return
        between_steps_sleep()

        _ = click_claim_button(page)
        between_steps_sleep()

        if not submit_email(page, email):
            print("[STEP_40_ENTER_EMAIL] submit failed; keep email for later")
            return
        pop_first_email_if(email, emails_path)
        print("[INFO] Consumed email:", email)
        between_steps_sleep()

        code = search_messages_for_otp_fixed_account(
            gmail, otp_query, otp_subj_rx, otp_code_rx,
            timeout=OTP_SEARCH_TIMEOUT,
            unread_only=unread_only,
            newest_only=newest_only,
            mark_read_after=mark_read_after,
            subject_match_mode=subject_match_mode,
            otp_subject_exact=otp_subject_exact
        )
        if not code:
            print("[WARN] OTP not found; exit")
            return
        between_steps_sleep()

        if not enter_otp_and_submit(page, code):
            print("[WARN] OTP submit failed; exit")
            return
        between_steps_sleep()

        _ = final_action(page)
        between_steps_sleep()

        # Save state right after onboarding/login is confirmed
        maybe_export_state(ctx)

        ok_search = step_75_search_home(page, texts_pool=SEARCH_TEXTS, times=3, gap_seconds=5)
        if ok_search:
            print("[STEP_75_SEARCH_HOME] 3 searches done.")
        else:
            print("[STEP_75_SEARCH_HOME] failed to perform searches.")
        between_steps_sleep()

        if RUN_POST_SCRIPT_AFTER_STEP75:
            ok_post = run_post_search_script()
            print("[POST] done" if ok_post else "[POST] failed")

        if RUN_LOGIN_AFTER_LOGOUT:
            print("[AUTH] Trying to logout...")
            _ = try_logout(page)
            human_sleep(1.0, 2.0)
            print(f"[AUTH] Trying to login with username/password ({LOGIN_USERNAME}/******)")
            _ = login_with_username_password(page, LOGIN_USERNAME, LOGIN_PASSWORD)

        try:
            page.close()
        except Exception:
            pass
        try:
            ctx.close()
        except Exception:
            pass

if __name__ == "__main__":
    main()
