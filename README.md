EN / [RU](README.ru.md) / [KK](README.kk.md)

<h1 align="center">🌍 PARSER FOR zakup.sk.kz 🛠️</h1>

---

# Table of Contents 📃

- [Description 😼](#description-)
- [Functions 🛠️](#functions-️)
- [Stack 📂](#stack-)
- [Quick Start 👾](#quick-start-)
- [Settings 📁](#settings-)
- [Errors ❌](#errors-)
- [Q&A ❓](#qa-)
- [Restrictions 📢](#restrictions-)
- [Roadmap 🗺️](#roadmap-️)
- [Links 🙀](#links-)

---

# Description 😼

A console application for collecting data from **zakup.sk.kz**.

The program first collects procurement numbers from search result pages, then opens the cards to gather detailed information. After processing, it saves the results as **CSV** — for Excel, BI, or further processing with your own scripts.

The project was originally **commissioned by a company for its employees**. It is now getting an updated structure, a more convenient console interface, and support for three languages.

---

# Functions 🛠️

- Search by keywords or procurement number
- Multiple search queries separated by commas
- Status selection: published / preliminary discussion published
- Filters to exclude services and works
- Collection across multiple pages
- Saved procurement numbers to check for duplicates on the next run
- A single configuration or multiple configurations in separate folders
- Progress panel: current stage, procurement count, warnings, and errors
- Interface in Russian, English, and Kazakh
- Detailed logs
- CSV export: link, number, application start and end dates, name, customer, and amount

---

# Stack 📂

- Python
- Selenium
- Microsoft Edge + Selenium Manager
- Rich
- JSON / INI / CSV

---

# Quick Start 👾

## Requirements

- Windows — the currently tested environment
- Python 3.12 or newer
- Microsoft Edge
- Internet connection
- Git — if downloading with `git clone`

## Installation

1. Download the project or clone the repository:

   ```powershell
   git clone https://github.com/AmbreKitsune/Parser-for-zakup.sk.kz.git
   cd Parser-for-zakup.sk.kz
   ```

2. Create a virtual environment:

   ```powershell
   python -m venv venv
   ```

3. Install the dependencies:

   ```powershell
   .\venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

4. Run the program from the project root:

   ```powershell
   .\venv\Scripts\python.exe src/main.py
   ```

## First Run

1. Choose a language: `ru`, `en`, or `kk`.
2. Follow the prompts to create a configuration, or select an existing one.
3. Wait for collection to finish.
4. Find your CSV in `data/output/`.

## Notes

- If the virtual environment is already activated, use `python src/main.py`.
- The `data/` folder is created automatically.
- Selenium Manager automatically selects the Edge driver. You do not need to place `msedgedriver.exe` next to the program manually.
- The first browser startup may take longer while the driver is prepared.
- Press **Ctrl+C** to stop.

---

# Settings 📁

Working files are stored in **`data/`** at the project root.

| File or folder | Purpose |
| --- | --- |
| `data/settings.json` | Interface language |
| `data/config.ini` | Single search configuration |
| `data/configs/<name>/config.ini` | Configurations in separate folders |
| `data/save_id.txt` | Procurement numbers used to check for duplicates |
| `data/parser.log` | Detailed log |
| `data/parser.log.1` and other archives | Previous logs |
| `data/output/` | CSV results |

If `data/configs/` exists, the program checks configurations in that folder first.

The language applies to the entire program. To change it, set `language` in `data/settings.json` to `ru`, `en`, or `kk`, then restart. You can also delete just `settings.json` to show the language selection again.

It is better to create configurations through the menu. If `site` is missing, empty, or contains only whitespace, the selected configuration is deleted. The program asks you to restart and create a new one.

---

# Errors ❌

**Invalid menu input**  
The program displays a message and repeats the question. Choose one of the listed options.

**The configuration is damaged and has been deleted**  
Restart and create a new configuration. This check covers a missing or empty `site`; other damage to the file can also cause loading errors.

**Edge will not start**  
Check that the browser is installed and an internet connection is available. See `data/parser.log` for details.

**Timeout / a card did not load**  
Check your connection and the website, then try again. The program makes up to three attempts per card. If the problem persists, send the log to the author.

**Processing stopped**  
The reason is recorded in `data/parser.log`. No need to photograph the entire console — the log is more useful :D

---

# Q&A ❓

**Q: Where are the results?**  
**A:** In `data/output/`. A CSV is created when new procurement notices have been collected.

**Q: Why are there no new procurement notices on another run?**  
**A:** Their numbers may already be in `data/save_id.txt`. To collect them again, delete that file while the program is stopped.

**Q: Does the language change the CSV or website data?**  
**A:** No. Only the program interface is translated. CSV headers and technical logs remain in Russian; website data is saved as received.

**Q: Can I edit the configuration manually?**  
**A:** Yes, but at your own risk. Creating a new one through the menu is easier.

**Q: Where are the EXE and installer?**  
**A:** Download the EXE or installer from [Releases](https://github.com/AmbreKitsune/Parser-for-zakup.sk.kz/releases/latest).

---

# Restrictions 📢

- Operation depends on your internet connection and the website's response speed.
- Changes to the website structure may require parser updates.
- CAPTCHA, anti-bot systems, or other website restrictions can stop collection.
- The author cannot guarantee that the website will not block access.
- Contracts are not available yet.
- The menu allows lots to be selected, but the current detail collector opens procurement notice cards (`advert`). Full lot support needs separate testing and development.
- Number history is shared across all configurations and does not track changes to previously found procurement notices.
- Other operating systems have not been tested yet.

---

# Links 🙀

- **Website**: [Click](https://ambrekitsune.dev/)
- **Telegram**: [@NightAmbreKitsune](https://t.me/NightAmbreKitsune)
- **Discord Server**: [Connect](https://discord.gg/U59cgYUNwv)
