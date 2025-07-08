import sys
import json
import os
import random
import threading
import time
import requests
import urllib3
import re
import unicodedata
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QLineEdit, QMessageBox, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QLinearGradient, QColor, QBrush, QIcon

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ContrepeteriesGame(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ContreProut")
        self.setGeometry(100, 100, 800, 350)
        self.setWindowIcon(QIcon("icon.png"))
        self.filename = 'contrepeteries.json'
        self.base_url = "https://lapoulequimue.fr/top/page/"
        self.start_page = 1
        self.end_page = 100
        self.contrepeteries = self.load_contrepeteries()
        self.current = None
        # Dégradé de fond
        palette = QPalette()
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0.0, QColor("lightblue"))
        gradient.setColorAt(1.0, QColor("plum"))
        palette.setBrush(QPalette.Window, QBrush(gradient))
        self.setAutoFillBackground(True)
        self.setPalette(palette)

        # Layout
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignCenter)

        # Label principal
        self.label = QLabel("Cliquez sur 'Nouvelle' pour commencer.")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(QFont("Courier", 32))
        self.label.setStyleSheet("color: #333333;")
        self.label.setWordWrap(True)

        # Champ de saisie
        self.input = QLineEdit()
        self.input.setPlaceholderText("Entrer les syllabes de la contrepetrie")
        self.input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #ccc;
                border-radius: 10px;
                padding: 8px;
                font-size: 18px;
            }
            QLineEdit:focus {
                border: 2px solid #66afe9;
                background-color: #f0f8ff;
                color: #222;
            }
        """)

        # Ajout de l'effet d'ombre
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setOffset(2, 2)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.input.setGraphicsEffect(shadow)


        # Boutons
        self.check_btn = QPushButton("✅ Vérifier")
        self.solution_btn = QPushButton("💡 Solution")
        self.next_btn = QPushButton("🆕 Nouvelle")
        self.input.returnPressed.connect(self.check_btn.click)
        
        for btn, color in zip([self.check_btn, self.solution_btn, self.next_btn], ["#007BFF", "#FFA500", "#28A745"]):
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 10px 20px;
                    font-size: 16px;
                }}
                QPushButton:hover {{
                    background-color: #444;
                }}
            """)

        # Ajout au layout
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.input)
        self.layout.addWidget(self.check_btn)
        self.layout.addWidget(self.solution_btn)
        self.layout.addWidget(self.next_btn)
        self.setLayout(self.layout)

        # Connexions
        self.solution_btn.clicked.connect(self.show_solution)
        self.next_btn.clicked.connect(self.new_contrepeterie)
        self.check_btn.clicked.connect(self.check_answer)

        threading.Thread(target=self.background_scraping, daemon=True).start()

    def load_contrepeteries(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def save_contrepeteries(self):
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(self.contrepeteries, f, ensure_ascii=False, indent=2)

    def scrape_solution(self, url):
        try:
            response = requests.get(url, verify=False)
            soup = BeautifulSoup(response.content, 'html.parser')
            spans = soup.find_all('span', class_='syllabe')
            return [span.get_text().strip().lower() for span in spans] if spans else []
        except:
            return []

    def scrape_contrepeteries(self, url):
        try:
            response = requests.get(url, verify=False)
            soup = BeautifulSoup(response.content, 'html.parser')
            contrepeteries = []
            for item in soup.find_all('article', class_='fl-post'):
                try:
                    title_tag = item.find('h2', class_='fl-post-title')
                    title = title_tag.text.strip()
                    link = title_tag.find('a')['href']
                    solution_list = self.scrape_solution(link)
                    contrepeteries.append((title, link, solution_list))
                except:
                    continue
            return contrepeteries
        except:
            return []

    def background_scraping(self):
        while True:
            for page in range(self.start_page, self.end_page + 1):
                url = f"{self.base_url}{page}/"
                scraped = self.scrape_contrepeteries(url)
                self.contrepeteries.extend(scraped)
                self.remove_duplicates()
                self.save_contrepeteries()
            time.sleep(3600)

    def remove_duplicates(self):
        seen = set()
        unique = []
        for title, link, solution in self.contrepeteries:
            if title not in seen:
                unique.append((title, link, solution))
                seen.add(title)
        self.contrepeteries = unique

    def new_contrepeterie(self):
        if not self.contrepeteries:
            self.label.setText("Aucune contrepèterie disponible.")
            return
        self.current = random.choice(self.contrepeteries)
        self.label.setText(f"{self.current[0]}")
        self.input.clear()

    def show_solution(self):
        if self.current:
            solution_text = ' <-> '.join(self.current[2]) if isinstance(self.current[2], list) else str(self.current[2])
            QMessageBox.information(self, "Solution", solution_text)

    def normalize_text(self, text):
        text = text.lower()
        text = ''.join(c for c in unicodedata.normalize('NFD', text)
                       if unicodedata.category(c) != 'Mn')
        return text.strip()

    def check_answer(self):
        if self.current:
            user_input = self.normalize_text(self.input.text())
            separators = r"\s*(?:<->|et|&|,|/|:|\s)\s*"
            user_parts = sorted([
                part.strip() for part in re.split(separators, user_input)
                if part.strip()
            ])
            correct_parts = sorted([
                self.normalize_text(part) for part in self.current[2]
            ])
            if user_parts == correct_parts:
                msg = QMessageBox(QMessageBox.Information, "Résultat", "✅ Correct !", parent=self)
                msg.finished.connect(self.new_contrepeterie)
                msg.exec_()
            else:
                solution_text = ' <-> '.join(self.current[2])
                QMessageBox.warning(self, "Résultat", f"❌ Incorrect. Solution : {solution_text}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ContrepeteriesGame()
    window.show()
    sys.exit(app.exec_())
