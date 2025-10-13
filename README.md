# ⚽ Futbol Sevenler - WhatsApp Attendance Tracker

A professional Streamlit web application to track attendance for your football group by analyzing WhatsApp messages. Automatically detects who's coming, who's not, and who's unsure based on their messages.

## 🌟 Features

- **Automatic Message Processing**: Parse WhatsApp group chat exports
- **Smart Response Detection**: Recognizes Turkish and English responses
- **Visual Analytics**: Beautiful charts and statistics
- **Multiple Input Methods**: Paste messages, upload files, or manual entry
- **Data Export**: Export to CSV, Excel, or text summary
- **Real-time Processing**: Instant results with professional UI
- **Mobile Friendly**: Responsive design for all devices

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone or download this repository**
   ```bash
   git clone https://github.com/yourusername/futbol-sevenler.git
   cd futbol-sevenler
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   streamlit run app.py
   ```

4. **Open in browser**
   The app will automatically open at `http://localhost:8501`

## 📱 How to Use

### Method 1: WhatsApp Message Export

1. **Export WhatsApp Chat**:
   - Open your WhatsApp group
   - Tap the group name → More → Export chat
   - Choose "Without Media"
   - Save the file or copy the text

2. **Process in App**:
   - Paste the messages in the sidebar
   - Click "Process Messages"
   - View results instantly

### Method 2: Manual Entry

1. Use the "Manual Entry" option in the sidebar
2. Add individual responses with names
3. Track attendance in real-time

### Method 3: File Upload

1. Upload your exported WhatsApp chat file (.txt)
2. The app will automatically process it
3. View comprehensive results

## 🎯 Supported Response Patterns

The app intelligently recognizes various response patterns:

### Turkish Responses
- **Positive**: geliyorum, varım, katılıyorum, evet, tamam, olur
- **Negative**: gelemem, yokum, maalesef, hayır, olmaz
- **Maybe**: belki, muhtemelen, sanırım, emin değilim

### English Responses  
- **Positive**: yes, coming, will come, count me in, sure
- **Negative**: no, can't, won't, not coming, sorry
- **Maybe**: maybe, probably, might, not sure

### Emojis
- **Positive**: 👍, ✅, ☑️, 💪, ⚽
- **Negative**: ❌, 👎, 😢, 🚫
- **Maybe**: 🤔, 🤷, ❓

## 📊 Features Overview

### Dashboard
- **Summary Statistics**: Total responses, confirmed attendance
- **Visual Charts**: Pie charts and bar graphs
- **Real-time Updates**: Instant processing and display

### Data Management
- **Smart Detection**: Automatic name and response extraction
- **Duplicate Handling**: Latest response from each person
- **Data Validation**: Ensures message format compatibility

### Export Options
- **CSV Export**: Spreadsheet-compatible format
- **Excel Export**: Professional reports with multiple sheets
- **Text Summary**: Ready-to-share attendance lists
- **Quick Copy**: One-click copying for messaging

## 🔧 Advanced Usage

### Customizing Response Patterns

Edit `config.py` to add new response patterns:

```python
# Add custom patterns
POSITIVE_PATTERNS_TR.append("your_custom_pattern")
NEGATIVE_PATTERNS_TR.append("another_pattern")
```

### Batch Processing

For multiple events, save different message sets and process them separately using the file upload feature.

## 📂 Project Structure

```
futbol_sevenler/
├── app.py                 # Main Streamlit application
├── utils.py               # Core processing functions
├── config.py              # Configuration settings
├── styles.css             # Custom styling
├── requirements.txt       # Python dependencies
├── sample_messages.txt    # Example WhatsApp messages
└── README.md             # This file
```

## 🛠️ Technical Details

### Dependencies
- **Streamlit**: Web application framework
- **Pandas**: Data manipulation and analysis
- **Plotly**: Interactive charts and graphs
- **Regex**: Advanced pattern matching
- **OpenPyXL**: Excel file processing

### Performance
- Handles groups with 100+ members
- Processes messages in real-time
- Optimized for mobile and desktop use

## 📝 Example Usage

### Sample WhatsApp Messages
```
[10/13/25, 3:45:23 PM] Ali: Geliyorum yarın ⚽
[10/13/25, 4:12:15 PM] Mehmet: Ben de varım 👍
[10/13/25, 4:30:02 PM] Ayşe: Maalesef gelemem 😞
[10/13/25, 4:45:33 PM] Ahmet: Belki gelirim 🤔
```

### Expected Output
- **Ali**: Coming ✅
- **Mehmet**: Coming ✅  
- **Ayşe**: Not Coming ❌
- **Ahmet**: Maybe 🤔

## 🎨 UI Features

- **Professional Design**: Clean, modern interface
- **Responsive Layout**: Works on all screen sizes
- **Interactive Charts**: Hover effects and animations
- **Color-coded Results**: Easy visual identification
- **Export Buttons**: One-click data download

## 🔒 Privacy & Security

- **Local Processing**: All data stays on your device
- **No Data Storage**: Messages are not saved permanently
- **No Internet Required**: Works offline after installation
- **No Personal Data Collection**: Complete privacy

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature-name`
3. **Make your changes**
4. **Test thoroughly**
5. **Submit a pull request**

### Areas for Contribution
- Additional language support
- New response pattern detection
- UI/UX improvements
- Performance optimizations
- Mobile app version

## 📞 Support

If you encounter any issues:

1. **Check the sample data**: Use "Load Sample Data" to verify the app works
2. **Verify message format**: Ensure WhatsApp export format is correct
3. **Update dependencies**: Run `pip install -r requirements.txt --upgrade`
4. **Create an issue**: Report bugs with sample data and error messages

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🏆 Acknowledgments

- Built with ❤️ for football communities
- Inspired by the need for better group coordination
- Designed for Turkish football groups but works globally

## 🔄 Version History

### v1.0.0 (Current)
- Initial release
- WhatsApp message parsing
- Turkish and English support
- Export functionality
- Professional UI

### Roadmap
- [ ] Mobile app version
- [ ] Multi-language support
- [ ] Calendar integration
- [ ] SMS notifications
- [ ] Team statistics
- [ ] Historical data tracking

---

**Made with ⚽ for football lovers everywhere!**

*For questions, suggestions, or support, feel free to reach out or create an issue.*