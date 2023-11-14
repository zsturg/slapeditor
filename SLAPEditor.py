import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QAction, QVBoxLayout, QWidget, QSplitter, QMenuBar, QFileDialog, QStyleFactory, QSlider, QLabel, QInputDialog, QMessageBox, QLineEdit, QTextBrowser, QPushButton, QComboBox, QMenu
from PyQt5.QtGui import QPalette, QColor, QFont, QTextCharFormat, QTextDocument, QTextCursor, QBrush
from PyQt5.QtCore import QJsonDocument, Qt, QTimer, QUrl
from PyQt5.Qt import QJsonDocument
from PyQt5.QtWebEngineWidgets import QWebEngineView
from docx import Document
from bs4 import BeautifulSoup
from ebooklib import epub, ITEM_DOCUMENT
import fitz  # Added import for PyMuPDF
import json
import random
from art import *
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.probability import FreqDist
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import wordnet
from nltk.corpus import reuters
from nltk.tag import pos_tag
from sklearn.feature_extraction.text import CountVectorizer
nltk.download('vader_lexicon')
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')
nltk.download('reuters')
nltk.data.path.append('nltk_data')
from collections import defaultdict
import spacy
import os
from collections import Counter, defaultdict
from nltk.corpus import treebank
import requests
from urllib.parse import urljoin
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QAction, QVBoxLayout, QHBoxLayout, QWidget, QSplitter, QMenuBar, QFileDialog, QStyleFactory, QSlider, QLabel, QInputDialog, QMessageBox, QLineEdit, QTextBrowser, QPushButton

if getattr(sys, 'frozen', False):  # The application is running as a PyInstaller bundle
    base_dir = sys._MEIPASS
else:  # The application is running in a normal Python environment
    base_dir = os.path.dirname(os.path.abspath(__file__))

model_path = os.path.join(base_dir, 'en_core_web_sm', 'en_core_web_sm-3.7.0')
nlp = spacy.load(model_path)

from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QLineEdit, QTextEdit, QWidget, QSplitter
from PyQt5.QtCore import Qt

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QComboBox, QTextEdit, QPushButton
import json

class FormatDialog(QDialog):
    formats = ["flat", "nested", "array", "arrays of objects", "nested arrays", "mixed types", "optional fields"]

    def __init__(self, parent=None):
        super(FormatDialog, self).__init__(parent)

        # Create the format combo box
        self.comboBox = QComboBox()

        # Add the formats to the combo box
        self.comboBox.addItems(self.formats)

        # Create the example text box
        self.textEdit = QTextEdit()
        self.textEdit.setReadOnly(False)

        # Create the layout
        layout = QVBoxLayout()
        layout.addWidget(self.comboBox)
        layout.addWidget(self.textEdit)
        self.setLayout(layout)

        # Connect the combo box signal to the update_example slot
        # Connect the combo box signal to the update_example slot
        self.comboBox.currentTextChanged.connect(self.update_example)


        # Update the example
        self.update_example(self.comboBox.currentText())

    def update_example(self, format):
        # Get the text from text_widget2
        text = self.parent().text_widget2.toPlainText()

        # Split the text into lines
        lines = text.split('\n')

        # Initialize the dictionary
        dictionary = {}

        # Iterate over the lines
        for line in lines:
            # Skip lines that don't contain ' : '
            if ' : ' not in line:
                continue

            # Split the line into the word and its type
            word, word_type = line.split(' : ')

            # Add the word and its type to the dictionary
            if format == "flat":
                dictionary[word] = word_type
            elif format == "nested":
                dictionary[word] = {"type": word_type}
            elif format == "array":
                dictionary[word] = [word_type]
            elif format == "arrays of objects":
                dictionary[word] = [{"name": word, "type": word_type}]
            elif format == "nested arrays":
                dictionary[word] = [{"name": word, "type": [word_type]}]
            elif format == "mixed types":
                dictionary[word] = [{"name": word, "type": word_type, "extra": "example"}]
            elif format == "optional fields":
                dictionary[word] = {"name": word, "type": word_type, "optional": "example"}
            else:
                dictionary[word] = word_type  # Default case

        # Convert the dictionary to a JSON string
        example = json.dumps(dictionary, indent=4)

        # Set the example in the text box
        self.textEdit.setPlainText(example)

    def get_format(self):
        return self.comboBox.currentText()

class DualScreenTextEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('SLAP Editor')
        self.url_history = []  # Add this line to maintain a history of visited URLs
        self.initUI()
        
    def initUI(self):
        self.setGeometry(100, 100, 800, 400)
        self.setWindowTitle('SLAP Editor')
        self.statusBar()

        self.book_mode = False

        # Initialize self.url_input as a QLineEdit
        self.url_input = QLineEdit()

        # Connect the returnPressed signal to the load_web_page function
        self.url_input.returnPressed.connect(self.load_web_page)

        # Initialize self.text_widget1 and self.text_widget2 as QTextEdit
        self.text_widget1 = QTextBrowser(self)
        self.text_widget2 = QTextEdit(self)

        # Initialize self.text_widget3 as QWebEngineView
        self.text_widget3 = QWebEngineView(self)
        self.text_widget3.setMinimumHeight(50)  # Set a minimum height

        # Set the font size of text_widget3
        font = QFont()
        font.setPointSize(6)  # Set the font size to 6
        self.text_widget3.setFont(font)

        # Set the initial HTML content of text_widget3
        html_content = """
        <html>
        <head>
            <style>
                body { background-color: rgb(25, 25, 25); }
            </style>
        </head>
        <body>
            <!-- Your HTML content goes here -->
        </body>
        </html>
        """
        self.text_widget3.setHtml(html_content)

        # Create a QSplitter with horizontal orientation
        splitter1 = QSplitter(Qt.Horizontal)
        splitter1.addWidget(self.text_widget1)
        splitter1.addWidget(self.text_widget2)

        # Create a QVBoxLayout
        layout = QVBoxLayout()

        # Create the Go, Stop, and Back buttons
        self.back_button = QPushButton('Back')
        self.stop_button = QPushButton('Stop')
        self.go_button = QPushButton('Go')
        
        

        # Connect the buttons to their slots
        # Connect the buttons to their slots
        self.go_button.clicked.connect(self.go_or_next_page)
        self.stop_button.clicked.connect(self.stop_loading)
        self.back_button.clicked.connect(self.go_back_or_previous_page)

        # Create a horizontal layout for the URL input and the buttons
        url_layout = QHBoxLayout()
        url_layout.addWidget(self.url_input)
        url_layout.addWidget(self.back_button)
        url_layout.addWidget(self.stop_button)
        url_layout.addWidget(self.go_button)
        # Add the URL layout to the main layout
        layout.addLayout(url_layout)

        # Create a QSplitter with vertical orientation
        splitter2 = QSplitter(Qt.Vertical)
        splitter2.addWidget(splitter1)
        splitter2.addWidget(self.text_widget3)
        splitter2.setSizes([350,50])

        # Add the splitter to the main layout
        layout.addWidget(splitter2)

        # Create a central widget
        central_widget = QWidget()

        # Set the layout of the central widget
        central_widget.setLayout(layout)

        # Set the central widget of the main window
        self.setCentralWidget(central_widget)
        # ... rest of your code ...
        self.text_widget1.anchorClicked.connect(self.handle_link_clicked)

        # Set the application style to "Fusion" for a modern appearance
        QApplication.setStyle(QStyleFactory.create('Fusion'))

        # Set a dark palette
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.Text, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
        dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
        self.setPalette(dark_palette)

        self.init_file_menus()
        self.init_edit_menu()
        self.init_tool_menu()
        self.init_dictionaries_menu()
        self.init_annotation_menu()

        # Create a horizontal layout for the font size slider
        slider_layout = QVBoxLayout()
        slider_label = QLabel('Font Size:')
        self.font_size_slider = QSlider()
        self.font_size_slider.setOrientation(1)  # Set orientation to horizontal
        slider_layout.addWidget(slider_label)
        slider_layout.addWidget(self.font_size_slider)

        # Add the font size slider below the status bar
        status = self.statusBar()
        status.addPermanentWidget(self.font_size_slider)

        # Connect the slider to a function to change font size
        self.font_size_slider.valueChanged.connect(self.change_font_size)

            

    def change_font_size(self):
        font_size = self.font_size_slider.value()
        font = QFont()
        font.setPointSize(font_size)
        self.text_widget1.setFont(font)
        self.text_widget2.setFont(font)

    def init_file_menus(self):
        file_menu1 = self.menuBar().addMenu('File Left')
        file_menu2 = self.menuBar().addMenu('File Right')

        # Define font_submenu before adding it to file_menu1
        font_submenu = QMenu('Font', self)

        # List of popular fonts
        fonts = ['Arial', 'Verdana', 'Helvetica', 'Tahoma', 'Trebuchet MS', 'Georgia', 'Garamond', 'Courier New', 'Brush Script MT', 'Lucida Sans', 'Palatino', 'Goudy Old Style', 'Futura', 'Copperplate Gothic Bold', 'Papyrus', 'Gill Sans', 'Franklin Gothic', 'Rockwell', 'Courier']

        # Add actions for each font
        for font in fonts:
            font_action = QAction(font, self)
            font_action.triggered.connect(lambda font=font: self.set_font(font))
            font_submenu.addAction(font_action)

        # Now you can add font_submenu to file_menu1
        file_menu1.addMenu(font_submenu)

        new_action1 = QAction('New', self)
        new_action1.triggered.connect(self.new_file1)
        file_menu1.addAction(new_action1)

        open_action1 = QAction('Open', self)
        open_action1.triggered.connect(self.open_file1)
        file_menu1.addAction(open_action1)

        save_action1 = QAction('Save', self)
        save_action1.triggered.connect(self.save_file1)
        file_menu1.addAction(save_action1)

        toggle_read_only_action = QAction('Toggle Edit Mode', self)
        toggle_read_only_action.triggered.connect(self.toggle_read_only)
        file_menu1.addAction(toggle_read_only_action)

        toggle_book_mode_action = QAction('Toggle Book Mode', self)
        toggle_book_mode_action.triggered.connect(self.toggle_book_mode)
        file_menu1.addAction(toggle_book_mode_action)

        new_action2 = QAction('New', self)
        new_action2.triggered.connect(self.new_file2)
        file_menu2.addAction(new_action2)

        open_action2 = QAction('Open', self)
        open_action2.triggered.connect(self.open_file2)
        file_menu2.addAction(open_action2)

        save_action2 = QAction('Save', self)
        save_action2.triggered.connect(self.save_file2)
        file_menu2.addAction(save_action2)

        find_replace_action = QAction('Find and Replace', self)
        find_replace_action.triggered.connect(lambda: self.find_and_replace(self.text_widget1))
        file_menu1.addAction(find_replace_action)

        find_replaceR_action = QAction('Find and Replace', self)
        find_replaceR_action.triggered.connect(lambda: self.find_and_replaceR(self.text_widget2))
        file_menu2.addAction(find_replaceR_action)

        move_text_action = QAction('Move text to Left Editor', self)
        move_text_action.triggered.connect(self.move_text)
        file_menu2.addAction(move_text_action)

    def init_edit_menu(self):
        edit_menu = self.menuBar().addMenu('Edit')

        # Clipboard Operations Submenu
        clipboard_submenu = QMenu('Clipboard Operations', self)

        cut_action = QAction('Cut', self)
        cut_action.setShortcut('Ctrl+X')
        cut_action.triggered.connect(self.cut_text)
        clipboard_submenu.addAction(cut_action)

        copy_action = QAction('Copy', self)
        copy_action.setShortcut('Ctrl+C')
        copy_action.triggered.connect(self.copy_text)
        clipboard_submenu.addAction(copy_action)

        paste_action = QAction('Paste', self)
        paste_action.setShortcut('Ctrl+V')
        paste_action.triggered.connect(self.paste_text)
        clipboard_submenu.addAction(paste_action)

        edit_menu.addMenu(clipboard_submenu)

        # Undo/Redo Submenu
        undo_redo_submenu = QMenu('Undo/Redo', self)

        undo_action = QAction('Undo', self)
        undo_action.setShortcut('Ctrl+Z')
        undo_action.triggered.connect(self.undo_text)
        undo_redo_submenu.addAction(undo_action)

        redo_action = QAction('Redo', self)
        redo_action.setShortcut('Ctrl+Y')
        redo_action.triggered.connect(self.redo_text)
        undo_redo_submenu.addAction(redo_action)

        edit_menu.addMenu(undo_redo_submenu)

        # Text Manipulation Submenu
        text_manipulation_submenu = QMenu('Text Manipulation', self)

        decode_action = QAction('Switch Decoding', self)
        decode_action.triggered.connect(self.switch_decoding)
        text_manipulation_submenu.addAction(decode_action)

        select_all_action = QAction('Select All', self)
        select_all_action.triggered.connect(self.select_all)
        text_manipulation_submenu.addAction(select_all_action)

        go_to_line_action = QAction('Go To Line', self)
        go_to_line_action.triggered.connect(self.go_to_line)
        text_manipulation_submenu.addAction(go_to_line_action)

        toggle_comment_action = QAction('Toggle Comment', self)
        toggle_comment_action.triggered.connect(self.toggle_comment)
        text_manipulation_submenu.addAction(toggle_comment_action)

        edit_menu.addMenu(text_manipulation_submenu)

        # Text Formatting Submenu
        text_formatting_submenu = QMenu('Text Formatting', self)

        indent_action = QAction('Indent', self)
        indent_action.triggered.connect(self.indent)
        text_formatting_submenu.addAction(indent_action)

        unindent_action = QAction('Unindent', self)
        unindent_action.triggered.connect(self.unindent)
        text_formatting_submenu.addAction(unindent_action)

        toggle_case_action = QAction('Toggle Case', self)
        toggle_case_action.triggered.connect(self.toggle_case)
        text_formatting_submenu.addAction(toggle_case_action)

        remove_trailing_spaces_action = QAction('Remove Trailing Spaces', self)
        remove_trailing_spaces_action.triggered.connect(self.remove_trailing_spaces)
        text_formatting_submenu.addAction(remove_trailing_spaces_action)

        edit_menu.addMenu(text_formatting_submenu)

        # Text Conversion Submenu
        text_conversion_submenu = QMenu('Text Conversion', self)

        convert_encoding_action = QAction('Convert Encoding', self)
        convert_encoding_action.triggered.connect(self.convert_encoding)
        text_conversion_submenu.addAction(convert_encoding_action)

        convert_eol_action = QAction('Convert EOL', self)
        convert_eol_action.triggered.connect(self.convert_eol)
        text_conversion_submenu.addAction(convert_eol_action)

        edit_menu.addMenu(text_conversion_submenu)


    def init_tool_menu(self):
        tool_menu = self.menuBar().addMenu('Language Tools')

        # Tokenization Submenu
        tokenization_submenu = QMenu('Tokenization', self)

        word_tokenization_action = QAction('Word Tokenization', self)
        word_tokenization_action.triggered.connect(self.word_tokenization)
        tokenization_submenu.addAction(word_tokenization_action)

        sentence_tokenization_action = QAction('Sentence Tokenization', self)
        sentence_tokenization_action.triggered.connect(self.sentence_tokenization)
        tokenization_submenu.addAction(sentence_tokenization_action)

        whitespace_tokenization_action = QAction('Whitespace Tokenization', self)
        whitespace_tokenization_action.triggered.connect(self.whitespace_tokenization)
        tokenization_submenu.addAction(whitespace_tokenization_action)

        punctuation_tokenization_action = QAction('Punctuation Tokenization', self)
        punctuation_tokenization_action.triggered.connect(self.punctuation_tokenization)
        tokenization_submenu.addAction(punctuation_tokenization_action)

        tool_menu.addMenu(tokenization_submenu)

        # Text Processing Submenu
        text_processing_submenu = QMenu('Text Processing', self)

        remove_punctuation_action = QAction('Remove Punctuation', self)
        remove_punctuation_action.triggered.connect(self.remove_punctuation)
        text_processing_submenu.addAction(remove_punctuation_action)

        remove_stopwords_action = QAction('Remove Stopwords', self)
        remove_stopwords_action.triggered.connect(self.remove_stopwords)
        text_processing_submenu.addAction(remove_stopwords_action)

        lowercase_action = QAction('Lowercase', self)
        lowercase_action.triggered.connect(self.lowercase)
        text_processing_submenu.addAction(lowercase_action)

        create_bigrams_action = QAction('Create Bigrams', self)
        create_bigrams_action.triggered.connect(self.create_bigrams)
        text_processing_submenu.addAction(create_bigrams_action)

        tool_menu.addMenu(text_processing_submenu)

        # Linguistic Analysis Submenu
        linguistic_analysis_submenu = QMenu('Linguistic Analysis', self)

        pos_action = QAction('POS Tagging', self)
        pos_action.triggered.connect(self.pos_tagging)
        linguistic_analysis_submenu.addAction(pos_action)

        ner_action = QAction('Named Entity Recognition', self)
        ner_action.triggered.connect(self.ner_tagging)
        linguistic_analysis_submenu.addAction(ner_action)

        lemmatization_action = QAction('Lemmatization', self)
        lemmatization_action.triggered.connect(self.lemmatization)
        linguistic_analysis_submenu.addAction(lemmatization_action)

        dependency_parsing_action = QAction('Dependency Parsing', self)
        dependency_parsing_action.triggered.connect(self.dependency_parsing)
        linguistic_analysis_submenu.addAction(dependency_parsing_action)

        morphological_analysis_and_ner_action = QAction('Morphological Analysis and NER', self)
        morphological_analysis_and_ner_action.triggered.connect(self.morphological_analysis_and_ner)
        linguistic_analysis_submenu.addAction(morphological_analysis_and_ner_action)

        tool_menu.addMenu(linguistic_analysis_submenu)

        # Advanced Text Analysis Submenu
        advanced_analysis_submenu = QMenu('Advanced Analysis', self)

        sentence_segmentation_action = QAction('Sentence Segmentation', self)
        sentence_segmentation_action.triggered.connect(self.sentence_segmentation)
        advanced_analysis_submenu.addAction(sentence_segmentation_action)

        summary_action = QAction('Text Summary', self)
        summary_action.triggered.connect(self.text_summary)
        advanced_analysis_submenu.addAction(summary_action)

        perform_sentiment_analysis_action = QAction('Sentiment Analysis', self)
        perform_sentiment_analysis_action.triggered.connect(self.perform_sentiment_analysis)
        advanced_analysis_submenu.addAction(perform_sentiment_analysis_action)

        find_adjective_synonyms_action = QAction('Adjective Synonyms', self)
        find_adjective_synonyms_action.triggered.connect(self.find_adjective_synonyms)
        advanced_analysis_submenu.addAction(find_adjective_synonyms_action)

        opposite_day_action = QAction('Opposite Day', self)
        opposite_day_action.triggered.connect(self.opposite_day)
        advanced_analysis_submenu.addAction(opposite_day_action)

        text_analysis_action = QAction('Vader Analysis', self)
        text_analysis_action.triggered.connect(self.text_analysis)
        advanced_analysis_submenu.addAction(text_analysis_action)

        tool_menu.addMenu(advanced_analysis_submenu)


    def init_dictionaries_menu(self):
        dictionaries_menu = self.menuBar().addMenu('Dictionaries')

        self.explore_json_action = QAction('Explore JSON', self)
        self.explore_json_action.setCheckable(True)
        self.explore_json_action.triggered.connect(self.update_json_samples)
        dictionaries_menu.addAction(self.explore_json_action)

        save_as_dictionary_action = QAction('Save as a Dictionary', self)
        save_as_dictionary_action.setStatusTip('Add a new dictionary to the system')
        save_as_dictionary_action.triggered.connect(self.save_as_dictionary)
        dictionaries_menu.addAction(save_as_dictionary_action)

        extract_facts_action = QAction('Dictionary of Facts', self)
        extract_facts_action.setStatusTip('creates a dictionary of facts from the left screen')
        extract_facts_action.triggered.connect(self.extract_facts)
        dictionaries_menu.addAction(extract_facts_action)

        top_news_action = QAction('Dictionary of News (Reuters)', self)
        top_news_action.setStatusTip('creates a dictionary of news from the left screen')
        top_news_action.triggered.connect(self.top_news)
        dictionaries_menu.addAction(top_news_action)

        top_money_action = QAction('Dictionary of Financial News (Wall St Journal)', self)
        top_money_action.setStatusTip('creates a dictionary of news from the left screen')
        top_money_action.triggered.connect(self.top_money)
        dictionaries_menu.addAction(top_money_action)



    def init_annotation_menu(self):
        annotation_menu = self.menuBar().addMenu('Annotation')

        annotate_text_action = QAction('Add Annotation', self)
        annotate_text_action.setStatusTip('select a dictionary')
        annotate_text_action.triggered.connect(self.annotate_text)
        annotation_menu.addAction(annotate_text_action)

        news_anno_action = QAction('Reuters Annotation', self)
        news_anno_action.setStatusTip('annotate with reuters data')
        news_anno_action.triggered.connect(self.news_anno)
        annotation_menu.addAction(news_anno_action)

    def new_file1(self):
        self.text_widget1.clear()
        self.text_widget1.setReadOnly(False)
    
    def open_file1(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, 'Open File (Screen 1)', '', 'Text Files (*.txt);;Word Documents (*.doc *.docx);;HTML Files (*.html);;EPUB Files (*.epub);;PDF Files (*.pdf);;All Files (*)', options=options)
        if file_name:
            if file_name.endswith('.pdf'):
                pdf_document = fitz.open(file_name)
                text = ""
                for page_num in range(len(pdf_document)):
                    page = pdf_document.load_page(page_num)
                    text += page.get_text()
                self.text_widget1.setPlainText(text)
            elif file_name.endswith('.epub'):
                book = epub.read_epub(file_name)
                html_content = ''
                for item in book.get_items_of_type(ITEM_DOCUMENT):
                    html_content += item.get_content().decode('utf-8')
                self.text_widget1.setHtml(html_content)  # Set the HTML content in the QTextBrowser
            else:
                with open(file_name, 'rb') as file:
                    text = file.read().decode('utf-8', errors='ignore')
                    self.text_widget1.setPlainText(text)

    def save_file1(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, 'Save File (Screen 1)', '', 'Text Files (*.txt);;Word Documents (*.docx);;HTML Files (*.html);;EPUB Files (*.epub);;PDF Files (*.pdf);;All Files (*)', options=options)

        if file_name:
            if file_name.endswith('.txt'):
                with open(file_name, 'w', encoding='utf-8') as file:
                    file.write(self.text_widget1.toPlainText())
            elif file_name.endswith('.docx'):
                self.save_docx(file_name, self.text_widget1.toPlainText())
            elif file_name.endswith('.html'):
                self.save_html(file_name, self.text_widget1.toPlainText())
            elif file_name.endswith('.epub'):
                self.save_epub(file_name, self.text_widget1.toPlainText())
            elif file_name.endswith('.pdf'):
                # Implement saving as PDF here
                pass

    def new_file2(self):
        self.text_widget2.clear()

    def open_file2(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, 'Open File (Screen 2)', '', 'Text Files (*.txt);;Word Documents (*.doc *.docx);;HTML Files (*.html);;EPUB Files (*.epub);;PDF Files (*.pdf);;All Files (*)', options=options)
        if file_name:
            with open(file_name, 'rb') as file:
                text = file.read().decode('utf-8', errors='ignore')
                if file_name.endswith('.pdf'):
                    pdf_document = fitz.open(file_name)
                    text = ""
                    for page_num in range(len(pdf_document)):
                        page = pdf_document.load_page(page_num)
                        text += page.get_text()
                self.text_widget2.setPlainText(text)

    def save_file2(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, 'Save File (Screen 2)', '', 'Text Files (*.txt);;Word Documents (*.docx);;HTML Files (*.html);;EPUB Files (*.epub);;PDF Files (*.pdf);;All Files (*)', options=options)

        if file_name:
            if file_name.endswith('.txt'):
                with open(file_name, 'w', encoding='utf-8') as file:
                    file.write(self.text_widget2.toPlainText())
            elif file_name.endswith('.docx'):
                self.save_docx(file_name, self.text_widget2.toPlainText())
            elif file_name.endswith('.html'):
                self.save_html(file_name, self.text_widget2.toPlainText())
            elif file_name.endswith('.epub'):
                self.save_epub(file_name, self.text_widget2.toPlainText())
            elif file_name.endswith('.pdf'):
                # Implement saving as PDF here
                pass

    def switch_decoding(self):
        # Implement the functionality to switch between UTF-8 and Latin decoding here
        active_widget = self.activeWidget()
        if active_widget:
            # Get the current text
            text = active_widget.toPlainText()
            try:
                # Try to decode as UTF-8
                text = text.encode('latin-1').decode('utf-8')
            except UnicodeDecodeError:
                # If it fails, assume it's already Latin-1 and decode as UTF-8
                text = text.encode('utf-8').decode('latin-1')
            # Set the modified text back
            active_widget.setPlainText(text)

    def cut_text(self):
        active_widget = self.activeWidget()
        if active_widget:
            active_widget.cut()

    def copy_text(self):
        active_widget = self.activeWidget()
        if active_widget:
            active_widget.copy()

    def paste_text(self):
        active_widget = self.activeWidget()
        if active_widget:
            active_widget.paste()

    def undo_text(self):
        active_widget = self.activeWidget()
        if active_widget:
            active_widget.undo()

    def redo_text(self):
        active_widget = self.activeWidget()
        if active_widget:
            active_widget.redo()

    def activeWidget(self):
        if self.text_widget1.hasFocus():
            return self.text_widget1
        elif self.text_widget2.hasFocus():
            return self.text_widget2
        
    def find_and_replace(self, text_widget1):
        text_to_find = QInputDialog.getText(self, 'Find', 'Enter text to find:')
        text_to_replace = QInputDialog.getText(self, 'Replace', 'Enter text to replace:')
        if text_to_find[1] and text_to_replace[1]:  # if user clicked OK
            text = text_widget1.toPlainText()
            new_text = text.replace(text_to_find[0], text_to_replace[0])
            text_widget1.setPlainText(new_text)

    def find_and_replaceR(self, text_widget2):
        text_to_find = QInputDialog.getText(self, 'Find', 'Enter text to find:')
        text_to_replace = QInputDialog.getText(self, 'Replace', 'Enter text to replace:')
        if text_to_find[1] and text_to_replace[1]:  # if user clicked OK
            text = text_widget2.toPlainText()
            new_text = text.replace(text_to_find[0], text_to_replace[0])
            text_widget2.setPlainText(new_text)

    
    def select_all(self):
        self.text_widget1.selectAll()

    def go_to_line(self, line_number):
        cursor = self.text_widget1.textCursor()
        cursor.setPosition(line_number)
        self.text_widget1.setTextCursor(cursor)

    def toggle_comment(self):
        cursor = self.text_widget1.textCursor()
        text = cursor.selectedText()
        if text.startswith('#'):
            text = text[1:]
        else:
            text = '#' + text
        cursor.insertText(text)

    def indent(self):
        cursor = self.text_widget1.textCursor()
        text = cursor.selectedText()
        text = '\t' + text.replace('\n', '\n\t')
        cursor.insertText(text)

    def unindent(self):
        cursor = self.text_widget1.textCursor()
        text = cursor.selectedText()
        text = text.replace('\t', '', 1)
        text = text.replace('\n\t', '\n')
        cursor.insertText(text)

    def toggle_case(self):
        cursor = self.text_widget1.textCursor()
        text = cursor.selectedText()
        if text.islower():
            text = text.upper()
        else:
            text = text.lower()
        cursor.insertText(text)

    def remove_trailing_spaces(self):
        text = self.text_widget1.toPlainText()
        text = '\n'.join(line.rstrip() for line in text.split('\n'))
        self.text_widget1.setPlainText(text)

    def convert_encoding(self, encoding):
        text = self.text_widget1.toPlainText()
        text = text.encode(encoding).decode(encoding)
        self.text_widget1.setPlainText(text)

    def convert_eol(self, eol):
        text = self.text_widget1.toPlainText()
        text = text.replace('\n', eol)
        self.text_widget1.setPlainText(text)
        
    def word_tokenization(self):
        nlp = spacy.load("en_core_web_sm")
        text = self.text_widget1.toPlainText()
        doc = nlp(text)
        tokens = [token.text for token in doc]
        self.text_widget2.setPlainText(" ".join(tokens))

    def sentence_tokenization(self):
        nlp = spacy.load("en_core_web_sm")
        text = self.text_widget1.toPlainText()
        doc = nlp(text)
        sentences = [sent.text for sent in doc.sents]
        self.text_widget2.setPlainText("\n".join(sentences))

    def whitespace_tokenization(self):
        text = self.text_widget1.toPlainText()
        tokens = text.split()
        self.text_widget2.setPlainText("\n".join(tokens))

    def punctuation_tokenization(self):
        nlp = spacy.load("en_core_web_sm")
        text = self.text_widget1.toPlainText()
        doc = nlp(text)
        punctuation = "!\"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"
        punct_tokens = [token.text for token in doc if token.text in punctuation]
        self.text_widget2.setPlainText(" ".join(punct_tokens))

    def pos_tagging(self):
        with open('status.txt', 'w') as f:
            f.write("POS tagging started\n")

        # Load English tokenizer, tagger, parser, NER and word vectors
        nlp = spacy.load("en_core_web_sm")

        # Get text from text_widget1
        text = self.text_widget1.toPlainText()

        # Process whole documents
        doc = nlp(text)

        # Perform POS tagging and join with space
        pos_text = ' '.join(f'{token.text}/{token.pos_}' for token in doc)

        # Output to text_widget2
        self.text_widget2.setPlainText(pos_text)

        with open('status.txt', 'a') as f:
            f.write("POS tagging completed\n")

    def ner_tagging(self):
        # Load English tokenizer, tagger, parser, NER and word vectors
        nlp = spacy.load("en_core_web_sm")

        # Get text from text_widget1
        text = self.text_widget1.toPlainText()

        # Process whole documents
        doc = nlp(text)

        # Perform NER and join with '\n' for new line
        ner_text = '\n'.join(f'{ent.text} : {ent.label_}' for ent in doc.ents)

        # Output to text_widget2
        self.text_widget2.setPlainText(ner_text)

    def lemmatization(self):
        # Load English tokenizer, tagger, parser, NER and word vectors
        nlp = spacy.load("en_core_web_sm")

        # Get text from text_widget1
        text = self.text_widget1.toPlainText()

        # Process whole documents
        doc = nlp(text)

        # Perform lemmatization and join with '\n' for new line
        lemma_text = '\n'.join(f'{token.text} : {token.lemma_}' for token in doc)

        # Output to text_widget2
        self.text_widget2.setPlainText(lemma_text)

    def sentence_segmentation(self):
        # Load English tokenizer, tagger, parser, NER and word vectors
        nlp = spacy.load("en_core_web_sm")

        # Get text from text_widget1
        text = self.text_widget1.toPlainText()

        # Process whole documents
        doc = nlp(text)

        # Perform sentence segmentation and join with '\n' for new line
        sentences = '\n'.join([sent.text for sent in doc.sents])

        # Output to text_widget2
        self.text_widget2.setPlainText(sentences)
    def dependency_parsing(self):
        # Load English tokenizer, tagger, parser, NER and word vectors
        nlp = spacy.load("en_core_web_sm")

        # Get text from text_widget1
        text = self.text_widget1.toPlainText()

        # Process whole documents
        doc = nlp(text)

        # Perform dependency parsing and join with '\n' for new line
        dependencies = '\n'.join([f'{token.text} : {token.dep_}' for token in doc])

        # Output to text_widget2
        self.text_widget2.setPlainText(dependencies)

    def morphological_analysis_and_ner(self):
        # Load English tokenizer, tagger, parser, NER and word vectors
        nlp = spacy.load("en_core_web_sm")

        # Get text from text_widget1
        text = self.text_widget1.toPlainText()

        # Process whole documents
        doc = nlp(text)

        # POS tag to full name mapping
        pos_map = {
            "VB": "verb",
            "NN": "noun",
            "PRP": "pronoun",
            "JJ": "adjective",
            "RB": "adverb",
            # Add more mappings as needed
        }

        # Perform morphological analysis and NER
        result = []
        for token in doc:
            pos = pos_map.get(token.tag_, token.tag_)
            synsets = ', '.join(synset.lemmas()[0].name() for synset in wordnet.synsets(token.text))
            result.append(f"{token.text} : {token.lemma_}, {pos}, {synsets}")

        for ent in doc.ents:
            if ent.text in result:
                result.append(f"{ent.text} : {ent.label_}")

        # Output to text_widget2
        self.text_widget2.setPlainText('\n'.join(result))
    

    def text_summary(self):
        # Load English tokenizer, tagger, parser, NER and word vectors
        nlp = spacy.load("en_core_web_sm")

        # Get text from text_widget1
        text = self.text_widget1.toPlainText()

        # Process whole documents
        doc = nlp(text)

        # Split text into sentences and count named entities in each sentence
        sentences = [(len(sent.ents), sent.text.strip()) for sent in doc.sents]

        # Rank sentences by number of named entities
        ranked_sentences = sorted(sentences, reverse=True)

        # Select top-ranked sentences for summary
        num_sentences_in_summary = 5  # or however many sentences you want in the summary
        summary_sentences = [sentence for num_ents, sentence in ranked_sentences[:num_sentences_in_summary]]

        # Combine summary sentences into a single string
        summary = ' '.join(summary_sentences)

        # Output to text_widget2
        self.text_widget2.setPlainText(summary)

    

    def remove_stopwords(self):
        text = self.text_widget1.toPlainText()
        doc = nlp(text)
        new_text = ' '.join([token.text for token in doc if not token.is_stop])
        self.text_widget2.setPlainText(new_text)

    def remove_punctuation(self):
        text = self.text_widget1.toPlainText()
        doc = nlp(text)
        new_text = ''.join([token.text for token in doc if not token.is_punct])
        self.text_widget2.setPlainText(new_text)

    def lowercase(self):
        text = self.text_widget1.toPlainText()
        new_text = text.lower()
        self.text_widget2.setPlainText(new_text)

    def create_bigrams(self):
        text = self.text_widget1.toPlainText()
        doc = nlp(text)
        new_text = '\n'.join([' '.join([token.text for token in doc[i:i+2]]) for i in range(len(doc)-1)])
        self.text_widget2.setPlainText(new_text)


    def open_file():
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(None, "QFileDialog.getOpenFileName()", "", "JSON Files (*.json);;All Files (*)", options=options)
        if file_name:
            with open(file_name, 'r') as f:
                dictionary = json.load(f)
            return dictionary

    def annotate_text(self):
        # Open a dialog box to select a JSON file
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Dictionary", "", "JSON Files (*.json);;All Files (*)", options=options)
        
        # Load the selected dictionary
        dictionary = {}
        if file_name:
            with open(file_name, 'r') as f:
                try:
                    dictionary = json.load(f)
                except json.JSONDecodeError:
                    QMessageBox.critical(self, "Error", "Invalid JSON file.")
                    return

        # Get the text from text_widget1
        text = self.text_widget1.toPlainText()

        # Split the text into lines
        lines = text.split('\n')

        # Initialize the annotated text
        annotated_text = ""

        # Iterate over the lines
        for line in lines:
            # Split the line into words
            words = line.split()

            # Iterate over the words
            for word in words:
                # If the word is in the dictionary, add the word and its definition to the annotated text
                if word.upper() in dictionary:
                    annotated_text += '<span style="background-color: #FFFF00">' + word + '</span> (' + dictionary[word.upper()] + ') '
                    # Show the word and its definition in the status bar
                    self.statusBar().showMessage(word + ': ' + dictionary[word.upper()])
                # If the word is not in the dictionary, just add the word to the annotated text
                else:
                    annotated_text += word + ' '

            # Add a newline character to the annotated text to maintain the original line breaks
            annotated_text += '\n'

        # Set the annotated text in text_widget2
        self.text_widget2.setHtml(annotated_text)

    

    

   

    def save_as_dictionary(self):
        # Get the text from text_widget2
        text = self.text_widget2.toPlainText()

        # Split the text into lines
        lines = text.split('\n')

        # Initialize the dictionary
        dictionary = {}

        # Analyze the text to suggest the most appropriate format
        suggested_format = "flat"
        for line in lines:
            if ' : ' in line:
                _, word_type = line.split(' : ')
                if ',' in word_type:
                    suggested_format = "array"
                    break
                elif ';' in word_type:
                    suggested_format = "nested"
                    break

        # Ask for the JSON format
        dialog = FormatDialog(self)
        result = dialog.exec_()
        if result == QDialog.Accepted:
            format = dialog.get_format()
        else:
            return

        # Iterate over the lines
        for line in lines:
            # Skip lines that don't contain ' : '
            if ' : ' not in line:
                continue

            # Split the line into the word and its type
            word, word_type = line.split(' : ')

            # Add the word and its type to the dictionary
            if format == "flat":
                dictionary[word.upper()] = word_type
            elif format == "nested":
                dictionary[word.upper()] = {"type": word_type}
            elif format == "array":
                dictionary[word.upper()] = [word_type]

        # Get the directory of the executable
        exe_dir = os.path.dirname(os.path.abspath(__file__))

        # Ask for a file name
        file_name, ok = QInputDialog.getText(self, "File Name", "Enter a file name:")
        if ok and file_name:
            # Append .json if not present
            if not file_name.endswith('.json'):
                file_name += '.json'
            # Set the full file path
            file_path = os.path.join(exe_dir, file_name)

            # Save the dictionary in the file
            with open(file_path, 'w') as f:
                json.dump(dictionary, f)

    

   

    

    

    def extract_facts(self):
        # Load the English spaCy model
        nlp = spacy.load('en_core_web_sm')

        # Get the text from text_widget1
        text = self.text_widget1.toPlainText()

        # Process the text
        doc = nlp(text)

        # Initialize the extracted facts
        extracted_facts = ""

        # Iterate over the sentences
        for sent in doc.sents:
            for token in sent:
                # Check if the token is 'is' or 'are'
                if token.lemma_ == 'be':
                    subj = [w for w in token.children if w.dep_ in ('nsubj', 'nsubjpass')]
                    attr = [w for w in token.children if w.dep_ in ('acomp', 'attr')]
                    if subj and attr:
                        # Add the fact to the extracted facts
                        extracted_facts += subj[0].text + ' : ' + attr[0].text + '\n'

        # Set the extracted facts in text_widget2
        self.text_widget2.setPlainText(extracted_facts)


    

    

    def perform_sentiment_analysis(self):
        # Initialize VADER
        ia = SentimentIntensityAnalyzer()

        # Get the text from text_widget1
        text = self.text_widget1.toPlainText()

        # Perform sentiment analysis
        sentiment = ia.polarity_scores(text)

        # Format the sentiment scores as a string
        sentiment_text = "\n".join(f"{k}: {v}" for k, v in sentiment.items())

        # Tokenize the text and create a frequency distribution
        tokens = word_tokenize(text)
        freq_dist = FreqDist(tokens)

        # Get the 10 most common words
        most_common = freq_dist.most_common(10)

        # Format the most common words as a string
        most_common_text = "\n".join(f"{word}: {freq}" for word, freq in most_common)

        # Set the sentiment scores and most common words in text_widget2
        self.text_widget2.setPlainText(sentiment_text + "\n\nMost common words:\n" + most_common_text)

    

    def find_adjective_synonyms(self):
        # Get the text from text_widget1
        text = self.text_widget1.toPlainText()

        # Tokenize the text and tag the parts of speech
        tokens = nltk.word_tokenize(text)
        tagged = nltk.pos_tag(tokens)

        # Filter for adjectives
        adjectives = [word for word, pos in tagged if pos.startswith('JJ')]

        # Find synonyms for each adjective
        synonyms = {}
        for adj in adjectives:
            synsets = wordnet.synsets(adj, pos=wordnet.ADJ)
            # Get the lemmas for each synset
            lemmas = [lemma.name() for synset in synsets for lemma in synset.lemmas()]
            # Remove any duplicates
            lemmas = list(set(lemmas))
            # Store the synonyms in the dictionary
            synonyms[adj] = lemmas

        # Format the synonyms as a string
        synonyms_text = "\n".join(f"{adj}: {', '.join(syns)}" for adj, syns in synonyms.items())

        # Set the synonyms in text_widget2
        self.text_widget2.setPlainText(synonyms_text)

    

    

    def opposite_day(self):
        # Get the text from text_widget1
        text = self.text_widget1.toPlainText()

        # Tokenize the text into sentences and shuffle them
        sentences = sent_tokenize(text)
        random.shuffle(sentences)

        # Tokenize each sentence into words and tag parts of speech
        new_sentences = []
        for sentence in sentences:
            tokens = word_tokenize(sentence)
            tagged = pos_tag(tokens)

            # Loop over the tagged tokens and replace words with their antonyms or random words
            for i, (word, pos) in enumerate(tagged):
                if pos.startswith(('JJ', 'VB', 'RB')):  # Check for adjectives, verbs, and adverbs
                    # Get the synsets for the word
                    pos_map = {'J': 'a', 'V': 'v', 'R': 'r', 'N': 'n'}
                    synsets = wordnet.synsets(word, pos=pos_map.get(pos[0].upper(), 'n'))
                    if synsets:
                        # Get the antonyms for the first synset
                        antonyms = synsets[0].lemmas()[0].antonyms()
                        if antonyms:
                            # Replace the word with the first antonym
                            tokens[i] = antonyms[0].name()
                elif pos.startswith('NN'):  # Check for nouns
                    # Replace the word with a random noun
                    tokens[i] = random.sample(list(wordnet.all_synsets(pos='n')), 1)[0].lemmas()[0].name()

            # Randomly capitalize words
            tokens = [word.upper() if random.random() < 0.2 else word for word in tokens]

            # Join the tokens back into a sentence
            new_sentences.append(' '.join(tokens))

        # Join the sentences back into a string and set the text in text_widget2
        self.text_widget2.setPlainText(' '.join(new_sentences))

    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    from sklearn.feature_extraction.text import CountVectorizer

    def text_analysis(self):
        # Load English tokenizer, tagger, parser, NER and word vectors
        nlp = spacy.load("en_core_web_sm")

        # Get text from text_widget1
        text = self.text_widget1.toPlainText()

        # Split the text into 10 equal parts
        parts = text.split('\n')
        parts = [parts[i::10] for i in range(10)]

        results = []
        for part in parts:
            part = ' '.join(part)
            # Process part
            doc = nlp(part)

            # Perform sentiment analysis using NLTK's VADER
            sid = SentimentIntensityAnalyzer()
            sentiment_scores = sid.polarity_scores(part)
            sentiment = 'positive' if sentiment_scores['compound'] > 0 else 'negative'
            result = [f"Sentiment: {sentiment}"]

            # Find semantic similarity between first two sentences
            if len(list(doc.sents)) > 1:
                sent1 = nlp(str(list(doc.sents)[0]))
                sent2 = nlp(str(list(doc.sents)[1]))
                similarity = sent1.similarity(sent2)
                result.append(f"Semantic similarity between first two sentences: {similarity}")

            # Extract main topics using bag of words model
            vectorizer = CountVectorizer(stop_words='english')
            if doc.text.split():
                X = vectorizer.fit_transform(doc.text.split())
                words = vectorizer.get_feature_names_out()
                frequencies = X.sum(axis=0).A1
                index = frequencies.argsort()
                words = [words[i] for i in index[::-1]]
                result.append("Main topics:")
                result.extend(words[:5])  # top 5 topics
            else:
                result.append("No topics found")

            results.append('\n'.join(result))

        # Output to text_widget2
        self.text_widget2.setPlainText('\n\n'.join(results))

    
    from collections import defaultdict

    def news_anno(self):
        # Load the Spacy English language model
        nlp = spacy.load('en_core_web_sm')

        # Build an index of the Reuters corpus
        index = defaultdict(list)
        for id in reuters.fileids():
            for sent in reuters.sents(id):
                for word in set(sent):
                    index[word].append(sent)

        # Get text from text_widget1
        text = self.text_widget1.toPlainText()

        # Split the text into paragraphs
        paragraphs = text.split('\n')

        # Clear text_widget2
        self.text_widget2.clear()

        # Iterate over the paragraphs
        for paragraph in paragraphs:
            # Process the paragraph with Spacy
            doc = nlp(paragraph)

            # Create a list to store the output for this paragraph
            output = []

            # Iterate over the entities in the Spacy Doc
            for entity in doc.ents:
                # Get the entity text
                entity_text = entity.text

                # Look up the sentences for the entity in the index
                sentences = index[entity_text]

                # If any sentences were found, add the entity and the first sentence to the output list
                if sentences:
                    output.append(f"{entity_text}: {' '.join(sentences[0])}")

            # Join the output list into a single string with one line per entry
            output_text = "\n".join(output)

            # Append the output text to text_widget2
            self.text_widget2.append(output_text)

    
    

    

    def top_news(self):
        # Load the Spacy English language model
        nlp = spacy.load('en_core_web_sm')

        # Build an index of the Reuters corpus
        index = defaultdict(list)
        for id in reuters.fileids():
            for sent in reuters.sents(id):
                for word in set(sent):
                    index[word].append(sent)

        # Get text from text_widget1
        text = self.text_widget1.toPlainText()

        # Process the text with Spacy
        doc = nlp(text)

        # Count the frequency of each entity
        entity_freq = Counter([entity.text for entity in doc.ents])

        # Get the top 30% of entities
        top_entities = [entity for entity, _ in entity_freq.most_common(int(len(entity_freq) * 0.1))]

        # Create a list to store the output
        output = []

        # Iterate over the top entities
        for entity in top_entities:
            # Look up the sentences for the entity in the index
            sentences = index[entity]

            # If any sentences were found, add the entity and the first sentence to the output list
            if sentences:
                output.append(f"{entity}: {' '.join(sentences[0])}")

        # Join the output list into a single string with one line per entry
        output_text = "\n".join(output)

        # Set the output text in text_widget3
        self.text_widget3.setPlainText(output_text)

        # Highlight the top entities in text_widget2
        self.text_widget2.setPlainText(text)
        format = QTextCharFormat()
        format.setBackground(QBrush(QColor("yellow")))
        for entity in top_entities:
            cursor = self.text_widget2.textCursor()
            cursor.setPosition(0)
            while self.text_widget2.document().find(entity, cursor.position()):
                cursor = self.text_widget2.textCursor()
                cursor.mergeCharFormat(format)

    

    from PyQt5.QtGui import QBrush, QColor, QTextCharFormat

    from PyQt5.QtGui import QBrush, QColor, QTextCharFormat

    from PyQt5.QtGui import QBrush, QColor, QTextCharFormat

    from PyQt5.QtGui import QBrush, QColor, QTextCharFormat

    from PyQt5.QtGui import QBrush, QColor, QTextCharFormat

    from PyQt5.QtGui import QBrush, QColor, QTextCharFormat, QTextCursor

    from PyQt5.QtWebEngineWidgets import QWebEngineView
    from PyQt5.QtCore import QUrl
    from PyQt5.QtWidgets import QApplication

    def top_money(self):
        # Load the Spacy English language model
        nlp = spacy.load('en_core_web_sm')

        # Get text from text_widget1
        text = self.text_widget1.toPlainText()

        # Process the text with Spacy
        doc = nlp(text)

        # Count the frequency of each entity
        entity_freq = Counter([entity.text for entity in doc.ents])

        # Get the top 30% of entities
        top_entities = [entity for entity in doc.ents if entity.text in [text for text, _ in entity_freq.most_common(int(len(entity_freq) * 0.3))]]

        # Define a dictionary to map entity types to colors
        entity_colors = {
            "PERSON": "yellow",
            "NORP": "green",
            "FAC": "blue",
            "ORG": "red",
            "GPE": "purple",
            "LOC": "orange",
            "PRODUCT": "pink",
            "EVENT": "brown",
            "WORK_OF_ART": "grey",
            "LAW": "lightblue",
            "LANGUAGE": "lightgreen",
            "DATE": "lightyellow",
            "TIME": "lightgrey",
            "PERCENT": "darkgreen",
            "MONEY": "darkblue",
            "QUANTITY": "darkred",
            "ORDINAL": "darkgrey",
            "CARDINAL": "darkorange",
        }

        # Initialize an empty HTML string with a style tag to set the font size and background color
        html = """
        <style>
        body {
            font-size: 10px;
            color: #fff;
            background-color: rgb(25, 25, 25);
        }
        </style>
        """

        # Iterate over the top entities and keep track of the indices of the "PERSON" entities
        person_indices = []
        for i, entity in enumerate(top_entities):
            # Append to the HTML string with the entity label, and the color for the entity type
            html += f'<span id="entity{i}" style="border:1px solid {entity_colors.get(entity.label_, "black")}; color:{entity_colors.get(entity.label_, "black")}; padding:2px; margin:10px 20px;">{entity.label_}</span>'
            if entity.label_ == "PERSON":
                person_indices.append(i)

        # Add JavaScript code to draw a line underneath each "PERSON" entity
        html += """
        <div id="svgContainer" style="position: relative;">
            <svg id="svg" style="width: 100%; height: 100%; position: absolute; top: 0; left: 0;"></svg>
        </div>
        <script src="https://d3js.org/d3.v5.min.js"></script>
        <script>
        window.onload = function() {
            var svg = d3.select("#svg");
            var person_indices = """ + str(person_indices) + """;

            // Draw a line underneath each 'PERSON'
            for (var i = 0; i < person_indices.length; i++) {
                var person = document.getElementById('entity' + person_indices[i]);

                var x1 = person.offsetLeft;
                var y1 = person.offsetTop + person.offsetHeight;

                var x2 = person.offsetLeft + person.offsetWidth;
                var y2 = y1;

                // Get the color of the 'PERSON' entity
                var color = window.getComputedStyle(person).backgroundColor;

                // Draw a line underneath the 'PERSON'
                svg.append("line")
                    .attr("x1", x1)
                    .attr("y1", y1)
                    .attr("x2", x2)
                    .attr("y2", y2)
                    .attr("stroke", color);  // Use the color of the 'PERSON' entity
            }
        }
        </script>
        """

        # Load the HTML string into text_widget3
        self.text_widget3.setHtml(html)

        # Copy the text from text_widget1 to text_widget2
        self.text_widget2.setPlainText(text)

        # Highlight the top entities in text_widget2
        for entity in top_entities:
            format = QTextCharFormat()
            format.setBackground(QBrush(QColor(entity_colors.get(entity.label_, "white"))))
            cursor = self.text_widget2.textCursor()
            cursor.setPosition(0)
            while True:
                new_cursor = self.text_widget2.document().find(entity.text, cursor.position())
                if new_cursor.isNull():
                    break
                cursor = new_cursor
                cursor.mergeCharFormat(format)

    

    def load_web_page(self):
        # Initialize an empty HTML string with a style tag to set the font size and background color
        html = """
        <style>
        body {
            font-size: 10px;
            color: #fff;
            background-color: rgb(25, 25, 25);
        }
        </style>
        """
        url = self.url_input.text().strip()
        self.text_widget1.setReadOnly(True)
        try:
            base_url = self.url_input.text()
            if '://' not in base_url:
                base_url = 'http://' + base_url
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
            }
            response = requests.get(base_url, headers=headers)    
            
            self.url_history.append(base_url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                # Extract the HTML of the body
                body = soup.body
                if body is not None:
                    html = str(body)
                else:
                    html = str(soup)

                # Extract the hyperlinks
                links = [f'<a href="{urljoin(base_url, a["href"])}">{a.get_text()}</a>' for a in soup.find_all('a', href=True)]

                # Extract the image map links
                for area in soup.find_all('area', href=True):
                    links.append(f'<a href="{urljoin(base_url, area["href"])}">{area.get("alt", "Image Map Link")}</a>')

                # Extract the image tags and replace them with ASCII art
                for img in soup.find_all('img', src=True):
                    alt_text = img.get('alt', '')
                    if alt_text:
                        ascii_art = text2art(alt_text)
                        img.replace_with(ascii_art)

                # Set the HTML and the hyperlinks in the text widget
                self.text_widget1.setHtml(str(soup) + '\n\nLinks:\n' + '\n'.join(links))
            else:
                self.text_widget1.setPlainText(f"Error: Unable to load web page. Status code: {response.status_code}")
        except Exception as e:
            print(f"Error in load_web_page: {e}")

        
    def handle_return_pressed(self):
        url = self.url_input.text()
        self.load_web_page()\
    
    from PyQt5.QtCore import QUrl


    def handle_link_clicked(self, url: QUrl):
        self.url_input.setText(url.toString())
        self.load_web_page()

    def stop_loading(self):
        # Stop loading the web page
        # This functionality depends on how you're loading the web page
        pass

    def go_back(self):
        # Go back to the previous URL
        if self.url_history:
            # Remove the current URL from the history
            self.url_history.pop()

            if self.url_history:
                # Load the previous URL
                self.url_input.setText(self.url_history[-1])
                self.load_web_page()    

    def move_text(self):
        # Get the text from text_widget2
        text = self.text_widget2.toPlainText()

        # Set the text in text_widget1
        self.text_widget1.setPlainText(text)

        # Clear the text in text_widget2
        self.text_widget2.clear()

    def toggle_read_only(self):
        # Toggle the readOnly status of text_widget1
        self.text_widget1.setReadOnly(not self.text_widget1.isReadOnly())

    def toggle_book_mode(self):
        self.book_mode = not self.book_mode
        if self.book_mode:
            # Estimate the number of lines that can fit in the text widget
            font_metrics = self.text_widget1.fontMetrics()
            lines_per_page = self.text_widget1.height() // font_metrics.lineSpacing()

            # Split the text into lines
            lines = self.text_widget1.toPlainText().split('\n')

            # Group the lines into pages
            self.text_content = ['\n'.join(lines[i:i+lines_per_page]) for i in range(0, len(lines), lines_per_page)]

            self.current_page = 0
            self.display_pages()

            # Add margins and spacing
            margin = 10  # Adjust this to change the margin
            self.text_widget1.setViewportMargins(margin, margin, margin, margin)
            self.text_widget2.setViewportMargins(margin, margin, margin, margin)

            spacing = 2  # Adjust this to change the spacing between lines
            self.text_widget1.setCursorWidth(spacing)
            self.text_widget2.setCursorWidth(spacing)
        else:
            self.text_widget1.clear()
            self.text_widget2.clear()

            # Remove margins and spacing
            self.text_widget1.setViewportMargins(0, 0, 0, 0)
            self.text_widget2.setViewportMargins(0, 0, 0, 0)
            self.text_widget1.setCursorWidth(1)
            self.text_widget2.setCursorWidth(1)

    def display_pages(self):
        self.text_widget1.setPlainText(self.text_content[self.current_page])  # Display current page
        if self.current_page + 1 < len(self.text_content):  # If there is a next page
            self.text_widget2.setPlainText(self.text_content[self.current_page + 1])  # Display next page
        else:
            self.text_widget2.clear()  # Clear the second widget if there is no next page

    def next_page(self):
        if self.book_mode and self.current_page + 2 < len(self.text_content):  # If there are more pages
            self.current_page += 2  # Go to the next pair of pages
            self.display_pages()

    def previous_page(self):
        if self.book_mode and self.current_page - 2 >= 0:  # If there are previous pages
            self.current_page -= 2  # Go to the previous pair of pages
            self.display_pages()


    def go_or_next_page(self):
        if self.book_mode:
            self.next_page()
        else:
            self.load_web_page()

    def go_back_or_previous_page(self):
        if self.book_mode:
            self.previous_page()
        else:
            self.go_back()
    
    def set_font(self, font_name):
        font = QFont(font_name)
        self.text_widget1.setFont(font)
    
    def update_json_samples(self):
        if not self.explore_json_action.isChecked():
            return
        # Get the selected text
        selected_text = self.text_widget1.textCursor().selectedText()

        # Generate the JSON structures
        json_samples = [
            ("Simple key-value pair", json.dumps({"key1": selected_text})),
            ("Nested dictionary", json.dumps({"key1": {"key2": selected_text}})),
            ("List as value", json.dumps({"key1": ["item1", selected_text]})),
            ("Nested dictionary with list", json.dumps({"key1": {"key2": ["item1", selected_text]}})),
            ("Nested dictionaries", json.dumps({"key1": {"key2": {"key3": selected_text}}}))
        ]

        # Display the JSON structures in text_widget2 with labels
        self.text_widget2.setPlainText("\n\n".join(f"{label}:\n{json_sample}" for label, json_sample in json_samples))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    editor = DualScreenTextEditor()
    editor.show()
    sys.exit(app.exec_())
