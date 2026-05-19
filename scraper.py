import os
import requests
from bs4 import BeautifulSoup
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
import time
import cloudscraper

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

def get_soup(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code == 429:
            print(f"  [!] Rate limited on {url}. Sleeping for 5 seconds...")
            time.sleep(5)
            r = requests.get(url, headers=HEADERS, timeout=15)
        return BeautifulSoup(r.text, "html.parser")
    except Exception as e:
        print(f"  [!] Failed {url}: {e}")
        return None

def clean(text):
    if not text:
        return ""
    return " ".join(text.split())

def scrape_wikipedia(url, label):
    print(f"[Wikipedia] {label}...")
    soup = get_soup(url)
    if not soup:
        return []
    lines = []
    content = soup.find("div", {"id": "mw-content-text"})
    if not content:
        return []
    for tag in content.select("p, li, h2, h3"):
        text = clean(tag.get_text())
        if len(text) > 40 and not text.startswith("Coordinates:"):
            lines.append(text)
    return lines

def scrape_fandom(url, label, prefix=""):
    print(f"[Fandom] {label}...")
    soup = get_soup(url)
    if not soup:
        return []
    lines = []
    content = soup.find("div", class_="mw-parser-output")
    if not content:
        return []
    for tag in content.select("p, li, h2, h3, td"):
        text = clean(tag.get_text())
        if len(text) > 30:
            entry = f"{prefix}{text}" if prefix else text
            lines.append(entry)
    return lines

AGENTS = {
    "Duelist": ["Jett", "Reyna", "Phoenix", "Yoru", "Neon", "Iso"],
    "Initiator": ["Sova", "Breach", "Skye", "Fade", "Gekko", "KAY/O"],
    "Controller": ["Brimstone", "Viper", "Omen", "Astra", "Harbor", "Clove"],
    "Sentinel": ["Killjoy", "Cypher", "Sage", "Chamber", "Deadlock", "Vyse"]
}

def scrape_all_agents():
    print("\n[Agents] Scraping all agents...")
    lines = []
    for role, agents in AGENTS.items():
        lines.append(f"=== ROLE: {role} ===")
        for agent in agents:
            url = f"https://valorant.fandom.com/wiki/{agent.replace('/', '%2F').replace(' ', '_')}"
            soup = get_soup(url)
            if not soup:
                time.sleep(1)
                continue
            content = soup.find("div", class_="mw-parser-output")
            if not content:
                time.sleep(1)
                continue
            
            lines.append(f"\n--- Agent: {agent} (Role: {role}) ---")
            
            count = 0
            for p in content.select("p"):
                text = clean(p.get_text())
                if len(text) > 40 and count < 8:
                    lines.append(text)
                    count += 1
            
            ability_blocks = content.select(".ability-box, .skill")
            if ability_blocks:
                for block in ability_blocks:
                    header = block.find(["h3", "h4", "span", "div"], class_="skill-name")
                    name = clean(header.get_text()) if header else "Ability"
                    lines.append(f"Abilities of {agent}: {name}")
                    
                    for desc in block.select("p, .skill-description"):
                        desc_text = clean(desc.get_text())
                        if desc_text:
                            lines.append(f"  - Description: {desc_text}")
            else:
                for h in content.select("h2, h3"):
                    heading = clean(h.get_text()).replace("[edit]", "").strip()
                    if any(kw in heading.lower() for kw in ["abilit", "skill", "signature", "ultimate", "basic"]):
                        lines.append(f"Abilities of {agent} ({heading}):")
                        sibling = h.find_next_sibling()
                        ab_count = 0
                        while sibling and sibling.name not in ["h2", "h3"] and ab_count < 10:
                            text = clean(sibling.get_text())
                            if len(text) > 20:
                                lines.append(f"  - {text}")
                                ab_count += 1
                            sibling = sibling.find_next_sibling()

            infobox = content.find("aside", class_="portable-infobox")
            if infobox:
                lines.append(f"Stats & Info for {agent}:")
                for data in infobox.select(".pi-item"):
                    label = data.find(class_="pi-data-label")
                    value = data.find(class_="pi-data-value")
                    if label and value:
                        lines.append(f"  - {clean(label.get_text())}: {clean(value.get_text())}")

            time.sleep(0.8)
    return lines

MAPS = ["Bind", "Haven", "Split", "Ascent", "Icebox", "Breeze",
        "Fracture", "Pearl", "Lotus", "Sunset", "Abyss"]

def scrape_all_maps():
    print("\n[Maps] Scraping all maps...")
    lines = []
    for m in MAPS:
        url = f"https://valorant.fandom.com/wiki/{m}"
        soup = get_soup(url)
        if not soup:
            time.sleep(1)
            continue
        content = soup.find("div", class_="mw-parser-output")
        if not content:
            time.sleep(1)
            continue
        lines.append(f"\n--- Map: {m} ---")
        
        count = 0
        for tag in content.select("p, li, h2, h3"):
            text = clean(tag.get_text())
            if len(text) > 30 and count < 30 and not text.startswith("Sign In"):
                lines.append(text)
                count += 1
        time.sleep(0.8)
    return lines

WEAPONS = [
    "Classic", "Shorty", "Frenzy", "Ghost", "Sheriff",
    "Stinger", "Spectre", "Bucky", "Judge",
    "Bulldog", "Guardian", "Phantom", "Vandal",
    "Marshal", "Outlaw", "Operator",
    "Ares", "Odin", "Tactical_Knife"
]

def scrape_all_weapons():
    print("\n[Weapons] Scraping all weapons...")
    lines = []
    overview = scrape_fandom("https://valorant.fandom.com/wiki/Weapons", "Weapons overview")
    lines.extend(overview[:30])
    
    for weapon in WEAPONS:
        url = f"https://valorant.fandom.com/wiki/{weapon}"
        soup = get_soup(url)
        if not soup:
            time.sleep(1)
            continue
        content = soup.find("div", class_="mw-parser-output")
        if not content:
            time.sleep(1)
            continue
        
        display_name = weapon.replace("_", " ")
        lines.append(f"\n--- Weapon: {display_name} ---")
        
        stats_table = content.find("table", class_="wikitable")
        if stats_table:
            lines.append(f"Technical Stats for {display_name}:")
            for row in stats_table.select("tr"):
                cells = [clean(td.get_text()) for td in row.select("th, td") if clean(td.get_text())]
                if cells:
                    lines.append(" | ".join(cells))
        
        count = 0
        for tag in content.select("p, li"):
            text = clean(tag.get_text())
            if len(text) > 20 and count < 15:
                lines.append(text)
                count += 1
        time.sleep(0.8)
    return lines

def scrape_game_modes():
    print("\n[Game Modes] Scraping...")
    lines = scrape_fandom("https://valorant.fandom.com/wiki/Game_Modes", "Game Modes")
    modes = ["Unrated", "Competitive", "Spike_Rush", "Deathmatch", "Escalation", "Replication", "Swiftplay"]
    for mode in modes:
        url = f"https://valorant.fandom.com/wiki/{mode}"
        extra = scrape_fandom(url, mode, prefix=f"[{mode.replace('_',' ')}] ")
        lines.extend(extra[:20])
        time.sleep(0.8)
    return lines

def scrape_history():
    print("\n[History] Scraping Valorant history & lore...")
    lines = []
    wiki = scrape_wikipedia("https://en.wikipedia.org/wiki/Valorant", "Valorant Wikipedia")
    lines.extend(wiki)
    lore_pages = [
        ("https://valorant.fandom.com/wiki/VALORANT_Protocol", "VALORANT Protocol"),
        ("https://valorant.fandom.com/wiki/Kingdom_Corporation", "Kingdom Corporation"),
        ("https://valorant.fandom.com/wiki/First_Light", "First Light event"),
        ("https://valorant.fandom.com/wiki/Radianite", "Radianite"),
        ("https://valorant.fandom.com/wiki/Radiants", "Radiants"),
    ]
    for url, label in lore_pages:
        extra = scrape_fandom(url, label, prefix=f"[{label}] ")
        lines.extend(extra[:25])
        time.sleep(0.8)
    return lines

def scrape_vct_wikipedia():
    print("\n[VCT] Wikipedia VCT article...")
    return scrape_wikipedia("https://en.wikipedia.org/wiki/Valorant_Champions_Tour", "VCT Wikipedia")

def scrape_vct_liquipedia_pages():
    print("[VCT] Liquipedia VCT pages...")
    lines = []
    pages = [
        ("https://liquipedia.net/valorant/Valorant_Champions_Tour", "VCT Overview"),
        ("https://liquipedia.net/valorant/Valorant_Champions/2024", "Champions 2024"),
        ("https://liquipedia.net/valorant/Valorant_Champions/2023", "Champions 2023"),
        ("https://liquipedia.net/valorant/VCT/2024/Masters/Shanghai", "Masters Shanghai 2024"),
        ("https://liquipedia.net/valorant/VCT/2024/Masters/Madrid", "Masters Madrid 2024"),
    ]
    for url, label in pages:
        soup = get_soup(url)
        if not soup:
            time.sleep(1.5)
            continue
        page_lines = []
        
        content = soup.find("div", id="mw-content-text")
        if content:
            for tag in content.select("p, h2, h3, .wikitable tr")[:70]:
                if tag.name == "tr":
                    cells = [clean(td.get_text()) for td in tag.select("td") if clean(td.get_text())]
                    if cells:
                        page_lines.append(f"[{label} Match/Result] " + " | ".join(cells))
                else:
                    text = clean(tag.get_text())
                    if len(text) > 25 and not text.startswith("▲"):
                        page_lines.append(f"[{label}] {text}")
                        
        lines.extend(page_lines)
        print(f"  -> {label}: {len(page_lines)} lines extracted")
        time.sleep(1.5)
    return lines

def scrape_vct_teams():
    print("[VCT] Pro teams...")
    lines = []
    teams = [
        ("Sentinels", "North America"), ("Cloud9", "North America"), ("NRG", "North America"),
        ("LOUD", "Brazil"), ("Fnatic", "EMEA"), ("Team_Liquid", "EMEA"),
        ("Paper_Rex", "Pacific"), ("DRX", "Pacific"), ("Gen.G", "Pacific"),
        ("EDward_Gaming", "China")
    ]
    for team, region in teams:
        url = f"https://liquipedia.net/valorant/{team}"
        soup = get_soup(url)
        if not soup:
            time.sleep(1.5)
            continue
        name = team.replace("_", " ")
        lines.append(f"\n--- Team: {name} (Region: {region}) ---")
        
        content = soup.find("div", id="mw-content-text")
        if content:
            for p in content.select("p")[:8]:
                text = clean(p.get_text())
                if len(text) > 30:
                    lines.append(text)
            
            roster_table = content.find("table", class_="roster-table") or content.find("table", class_="wikitable")
            if roster_table:
                for row in roster_table.select("tr"):
                    id_cell = row.find("span", class_="id") or row.find("td")
                    if id_cell:
                        player_info = clean(row.get_text(separator=" "))
                        lines.append(f"Active Roster / Info: {player_info}")
                        
        time.sleep(1.5)
    return lines

def scrape_vct_notable_players():
    print("[VCT] Notable pro players...")
    lines = []
    players = [
        "TenZ", "Yay", "ScreaM", "Derke", "Alfajer",
        "Aspas", "Less", "Sacy", "Zekken", "Chronicle"
    ]
    for player in players:
        url = f"https://liquipedia.net/valorant/{player}"
        soup = get_soup(url)
        if not soup:
            time.sleep(1.5)
            continue
        lines.append(f"\n--- Player: {player} ---")
        
        content = soup.find("div", id="mw-content-text")
        if content:
            for p in content.select("p")[:6]:
                text = clean(p.get_text())
                if len(text) > 30:
                    lines.append(text)
            
            infobox = soup.find("div", class_="fo-ntm-infobox") or soup.find("table", class_="infobox-table")
            if infobox:
                for row in infobox.select(".infobox-cell-2, tr"):
                    text = clean(row.get_text(separator=": "))
                    if text and len(text) > 5:
                        lines.append(f"Player Bio Data: {text}")
        time.sleep(1.2)
    return lines

def scrape_pro_settings():
    print("\n[ProSettings] Scraping player mouse configurations and hardware data...")
    lines = []
    scraper = cloudscraper.create_scraper()
    url = "https://prosettings.net/lists/valorant/"
    
    try:
        response = scraper.get(url, timeout=15)
        if response.status_code != 200:
            print(f"  [!] Cloudflare check failed or site blocked. Status code: {response.status_code}")
            return []
            
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table")
        if table:
            rows = table.find_all("tr")
            print(f"  -> Extracting hardware configs across {len(rows)} player segments.")
            
            # Grabbing primary active rows to supply dense data chunks
            for row in rows[:80]:
                cells = row.find_all(["td", "th"])
                cell_data = [clean(cell.get_text()) for cell in cells if clean(cell.get_text())]
                
                if cell_data:
                    player_line = " | ".join(cell_data)
                    lines.append(f"[Pro Player Setup Metric] {player_line}")
        else:
            print("  [!] Target table configuration missing from document root layout.")
    except Exception as e:
        print(f"  [!] ProSettings pipeline fault occurred: {e}")
        
    return lines

def build_pdf(sections):
    print("\n[PDF] Building valorant_knowledge.pdf ...")
    os.makedirs("data", exist_ok=True)
    doc = SimpleDocTemplate(
        "data/valorant_knowledge.pdf",
        pagesize=letter,
        rightMargin=0.8 * inch,
        leftMargin=0.8 * inch,
        topMargin=inch,
        bottomMargin=inch
    )
    styles = getSampleStyleSheet()
    story = []
    story.append(Paragraph("Valorant Complete Knowledge Base", styles["Title"]))
    story.append(Spacer(1, 0.1 * inch))
    story.append(Paragraph(
        "Comprehensive reference covering game history, agents, maps, weapons, game modes, "
        "and the full Valorant Champions Tour (VCT) pro scene.",
        styles["Normal"]
    ))
    story.append(PageBreak())
    total_lines = 0
    for section_title, lines in sections:
        if not lines:
            print(f"  [!] Skipping '{section_title}' — no data extracted")
            continue
        story.append(Paragraph(section_title, styles["Heading1"]))
        story.append(Spacer(1, 0.1 * inch))
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            line = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            line = "".join(c for c in line if ord(c) < 128)
            
            try:
                if line.startswith("---") or line.startswith("==="):
                    story.append(Paragraph(line, styles["Heading2"]))
                else:
                    story.append(Paragraph(line, styles["Normal"]))
                story.append(Spacer(1, 2))
                total_lines += 1
            except Exception:
                pass
        story.append(PageBreak())
    doc.build(story)
    print(f"[PDF] Done! Saved to data/valorant_knowledge.pdf")
    print(f"[PDF] Total lines written: {total_lines}")

if __name__ == "__main__":
    sections = []
    print("=" * 55)
    print("Valorant Knowledge Base Scraper — Full Edition")
    print("=" * 55)
    sections.append(("Valorant History & Overview", scrape_history()))
    time.sleep(1)
    sections.append(("Agents — All Roles & Abilities", scrape_all_agents()))
    time.sleep(1)
    sections.append(("Maps — All Maps Detailed", scrape_all_maps()))
    time.sleep(1)
    sections.append(("Weapons — All Weapons Detailed", scrape_all_weapons()))
    time.sleep(1)
    sections.append(("Game Modes", scrape_game_modes()))
    time.sleep(1)
    sections.append(("VCT — Valorant Champions Tour Overview", scrape_vct_wikipedia()))
    time.sleep(1)
    sections.append(("VCT — Tournaments & Results", scrape_vct_liquipedia_pages()))
    time.sleep(1)
    sections.append(("VCT — Pro Teams", scrape_vct_teams()))
    time.sleep(1)
    sections.append(("VCT — Notable Pro Players", scrape_vct_notable_players()))
    time.sleep(1)
    sections.append(("VCT — Pro Player Gear and Settings", scrape_pro_settings()))
    
    build_pdf(sections)
    print("\nAll done! Run python rag.py to start querying.")