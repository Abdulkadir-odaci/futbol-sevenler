import streamlit as st
import pandas as pd
import regex as re
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from utils import WhatsAppParser, AttendanceTracker, RegistrationManager
import io

# Page config
st.set_page_config(
    page_title="⚽ Futbol Sevenler - Attendance Tracker",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    
    .stats-card {
        background-color: #f0f8ff;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin: 1rem 0;
    }
    
    .attendance-yes {
        color: #28a745;
        font-weight: bold;
    }
    
    .attendance-maybe {
        color: #ffc107;
        font-weight: bold;
    }
    
    .attendance-no {
        color: #dc3545;
        font-weight: bold;
    }
    
    .stButton > button {
        background-color: #1f77b4;
        color: white;
        border-radius: 20px;
        border: none;
        padding: 0.5rem 2rem;
        font-weight: bold;
    }
    
    .sidebar-content {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

def show_info_modal():
    """Display information modal with rules and registration process."""
    st.info("""
    📋 **FUTBOL KAYIT SİSTEMİ KURALLARI**
    
    🕒 **KAYIT SÜRESİ:**
    • Kayıtlar Cumartesi saat 13:00'a kadar alınır
    • Bu saatten sonra kayıt yapılamaz
    
    👥 **LİSTE SİSTEMİ:**
    • **Ana Liste (1-10):** İlk 10 kişi kesin oynar
    • **Bekleme Listesi (11-18):** 10. kişi gelmezse sırayla oynar
    • **Yedek Listesi (18+):** 18'den fazla kayıt olursa yedek listesinde bekler
    
    ⚽ **KURAL:**
    • Maksimum 18 kişi sahada oynayabilir
    • Yedek listesindekiler, öncelikli listeden birisi gelmezse sahaya alınır
    • İsim kayıt etmek = kesin gelecek demektir
    
    🔥 **DİKKAT:** Sadece ismini yazan ve kesin gelecek olan oyuncular kayıt olsun!
    """)

def main():
    # Header with info button
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown('<h1 class="main-header">⚽ Futbol Sevenler - Kayıt Sistemi</h1>', unsafe_allow_html=True)
    with col2:
        if st.button("ℹ️ Bilgi", help="Kayıt kuralları ve sistem bilgileri"):
            show_info_modal()
    
    # Initialize session state
    if 'attendance_data' not in st.session_state:
        st.session_state.attendance_data = pd.DataFrame()
    if 'parser' not in st.session_state:
        st.session_state.parser = WhatsAppParser()
    if 'tracker' not in st.session_state:
        st.session_state.tracker = AttendanceTracker()
    if 'registration_manager' not in st.session_state:
        st.session_state.registration_manager = RegistrationManager()
    if 'registered_players' not in st.session_state:
        st.session_state.registered_players = []
    
    # Check deadline
    deadline = datetime.now().replace(hour=13, minute=0, second=0, microsecond=0)
    if datetime.now().weekday() == 5 and datetime.now() > deadline:  # Saturday after 13:00
        st.error("🚫 KAYIT SÜRESİ DOLDU! Kayıtlar Cumartesi saat 13:00'a kadar alınır.")
        st.stop()
    elif datetime.now().weekday() == 5:  # Saturday before 13:00
        time_left = deadline - datetime.now()
        st.warning(f"⏰ Kayıt için {time_left.seconds//3600} saat {(time_left.seconds//60)%60} dakika kaldı!")
    
    # Sidebar
    with st.sidebar:
        st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
        st.header("� OYUNCU KAYDI")
        
        # Player registration form
        st.subheader("✍️ İsim Kayıt Et")
        player_name = st.text_input(
            "Adınızı ve Soyadınızı yazın:",
            placeholder="Örnek: Ali Veli",
            help="Tam adınızı yazın"
        )
        
        if st.button("📝 Kayıt Ol", type="primary", use_container_width=True):
            if player_name.strip():
                result = st.session_state.registration_manager.register_player(
                    player_name.strip().title(), 
                    st.session_state.registered_players
                )
                if result['success']:
                    st.session_state.registered_players = result['player_list']
                    st.success(f"✅ {result['message']}")
                    st.rerun()
                else:
                    st.error(f"❌ {result['message']}")
            else:
                st.error("❌ Lütfen adınızı yazın!")
        
        # Remove player option
        if st.session_state.registered_players:
            st.subheader("🗑️ Kayıt Silme")
            player_to_remove = st.selectbox(
                "Silmek istediğiniz oyuncu:",
                ["Seçiniz..."] + [p['name'] for p in st.session_state.registered_players]
            )
            
            if st.button("🗑️ Kaydı Sil") and player_to_remove != "Seçiniz...":
                st.session_state.registered_players = [
                    p for p in st.session_state.registered_players 
                    if p['name'] != player_to_remove
                ]
                # Reorder positions after removal
                st.session_state.registration_manager.reorder_positions(st.session_state.registered_players)
                st.success(f"✅ {player_to_remove} kaydı silindi!")
                st.rerun()
        
        st.markdown("---")
        st.header("📱 WhatsApp Mesaj İşleme")
        st.caption("(Eski sistem - İsteğe bağlı)")
        
        # Input method selection
        input_method = st.radio(
            "Mesaj yöntemi seçin:",
            ["Mesaj Yapıştır", "Dosya Yükle", "Manuel Giriş"]
        )
        
        messages_text = ""
        
        if input_method == "Mesaj Yapıştır":
            messages_text = st.text_area(
                "WhatsApp mesajlarını buraya yapıştırın:",
                height=150,
                placeholder="Örnek:\n[13/10/25, 15:45:23] Ali: Geliyorum yarın\n[13/10/25, 16:12:15] Mehmet: Ben de varım"
            )
        
        elif input_method == "Dosya Yükle":
            uploaded_file = st.file_uploader(
                "Metin dosyası seçin",
                type=['txt'],
                help="WhatsApp sohbet dışa aktarımı yükleyin"
            )
            if uploaded_file is not None:
                messages_text = str(uploaded_file.read(), "utf-8")
        
        elif input_method == "Manuel Giriş":
            st.subheader("Tekil Yanıt Ekle")
            name = st.text_input("İsim:")
            response = st.selectbox("Yanıt:", ["Evet", "Belki", "Hayır"])
            message = st.text_input("Mesaj (isteğe bağlı):")
            
            if st.button("Yanıt Ekle") and name:
                new_entry = {
                    'name': name,
                    'response': response,
                    'message': message,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                if st.session_state.attendance_data.empty:
                    st.session_state.attendance_data = pd.DataFrame([new_entry])
                else:
                    st.session_state.attendance_data = pd.concat([
                        st.session_state.attendance_data,
                        pd.DataFrame([new_entry])
                    ], ignore_index=True)
                st.success(f"{name} için yanıt eklendi")
                st.rerun()
        
        # Process button
        if messages_text and st.button("🔍 Process Messages", type="primary"):
            with st.spinner("Processing messages..."):
                parsed_data = st.session_state.parser.parse_messages(messages_text)
                attendance_data = st.session_state.tracker.extract_attendance(parsed_data)
                st.session_state.attendance_data = attendance_data
                st.success("Messages processed successfully!")
                st.rerun()
        
        # Clear data button
        if st.button("🗑️ Clear All Data"):
            st.session_state.attendance_data = pd.DataFrame()
            st.success("Data cleared!")
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Main content
    if st.session_state.registered_players:
        # Registration statistics
        col1, col2, col3, col4 = st.columns(4)
        
        total_registered = len(st.session_state.registered_players)
        main_list = [p for p in st.session_state.registered_players if p['position'] <= 10]
        waiting_list = [p for p in st.session_state.registered_players if 10 < p['position'] <= 18]
        reserve_list = [p for p in st.session_state.registered_players if p['position'] > 18]
        
        with col1:
            st.metric("Toplam Kayıt", total_registered, delta=None)
        
        with col2:
            st.metric("Ana Liste 🎯", len(main_list), delta=f"{10-len(main_list)} yer boş" if len(main_list) < 10 else "Dolu")
        
        with col3:
            st.metric("Bekleme Listesi ⏳", len(waiting_list), delta=f"{18-len(main_list)-len(waiting_list)} yer boş" if len(main_list)+len(waiting_list) < 18 else "Dolu")
        
        with col4:
            st.metric("Yedek Listesi 📝", len(reserve_list), delta=None)
        
        # Charts section
        st.subheader("📊 Kayıt Durumu")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Registration distribution pie chart
            fig_pie = px.pie(
                values=[len(main_list), len(waiting_list), len(reserve_list)],
                names=['Ana Liste (1-10)', 'Bekleme (11-18)', 'Yedek (18+)'],
                title="Liste Dağılımı",
                color_discrete_map={
                    'Ana Liste (1-10)': '#28a745',
                    'Bekleme (11-18)': '#ffc107',
                    'Yedek (18+)': '#dc3545'
                }
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Capacity bar chart
            fig_bar = go.Figure(data=[
                go.Bar(
                    x=['Ana Liste', 'Bekleme', 'Yedek'],
                    y=[len(main_list), len(waiting_list), len(reserve_list)],
                    marker_color=['#28a745', '#ffc107', '#dc3545'],
                    text=[f"{len(main_list)}/10", f"{len(waiting_list)}/8", f"{len(reserve_list)}"],
                    textposition='auto'
                )
            ])
            fig_bar.update_layout(title="Liste Kapasiteleri", yaxis_title="Oyuncu Sayısı")
            st.plotly_chart(fig_bar, use_container_width=True)
        
        # Player Lists
        st.subheader("� Oyuncu Listeleri")
        
        # Display lists in tabs
        tab1, tab2, tab3 = st.tabs(["🎯 Ana Liste (1-10)", "⏳ Bekleme Listesi (11-18)", "📝 Yedek Listesi (18+)"])
        
        with tab1:
            if main_list:
                st.success(f"Ana listede {len(main_list)} oyuncu var (Kesin oynayacaklar)")
                for i, player in enumerate(main_list, 1):
                    st.write(f"**{i}.** {player['name']} - ⏰ {player['timestamp']}")
            else:
                st.info("Ana liste boş. İlk 10 kayıt bu listeye girecek.")
        
        with tab2:
            if waiting_list:
                st.warning(f"Bekleme listesinde {len(waiting_list)} oyuncu var")
                for i, player in enumerate(waiting_list, 11):
                    st.write(f"**{i}.** {player['name']} - ⏰ {player['timestamp']}")
                st.caption("Bu oyuncular, ana listeden biri gelmezse sırayla sahaya alınır.")
            else:
                st.info("Bekleme listesi boş.")
        
        with tab3:
            if reserve_list:
                st.error(f"Yedek listesinde {len(reserve_list)} oyuncu var")
                for i, player in enumerate(reserve_list, 19):
                    st.write(f"**{i}.** {player['name']} - ⏰ {player['timestamp']}")
                st.caption("Bu oyuncular sadece 18 kişiden biri gelmezse sahaya alınır.")
            else:
                st.info("Yedek listesi boş.")
        
        # Export options
        st.subheader("📤 Veri İndirme")
        
        col1, col2, col3 = st.columns(3)
        
        # Create DataFrame from registered players
        export_df = pd.DataFrame(st.session_state.registered_players)
        
        with col1:
            # CSV export
            csv_buffer = io.StringIO()
            export_df.to_csv(csv_buffer, index=False)
            st.download_button(
                label="📄 CSV İndir",
                data=csv_buffer.getvalue(),
                file_name=f"futbol_kayitlari_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        with col2:
            # Excel export
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                export_df.to_excel(writer, sheet_name='Oyuncular', index=False)
                
                # Add summary sheet
                summary_data = pd.DataFrame({
                    'Liste': ['Ana Liste', 'Bekleme', 'Yedek', 'Toplam'],
                    'Sayı': [len(main_list), len(waiting_list), len(reserve_list), total_registered]
                })
                summary_data.to_excel(writer, sheet_name='Özet', index=False)
            
            st.download_button(
                label="📊 Excel İndir",
                data=excel_buffer.getvalue(),
                file_name=f"futbol_kayitlari_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        with col3:
            # Summary text export
            summary_text = f"""🏆 FUTBOL SEVENLER KAYIT LİSTESİ
Oluşturulma Tarihi: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

📊 ÖZET:
Toplam Kayıt: {total_registered}
Ana Liste: {len(main_list)}/10
Bekleme Listesi: {len(waiting_list)}/8
Yedek Listesi: {len(reserve_list)}

🎯 ANA LİSTE (Kesin Oynayacaklar):
"""
            for i, player in enumerate(main_list, 1):
                summary_text += f"{i}. {player['name']}\n"
            
            summary_text += f"\n⏳ BEKLEME LİSTESİ:\n"
            for i, player in enumerate(waiting_list, 11):
                summary_text += f"{i}. {player['name']}\n"
            
            if reserve_list:
                summary_text += f"\n📝 YEDEK LİSTESİ:\n"
                for i, player in enumerate(reserve_list, 19):
                    summary_text += f"{i}. {player['name']}\n"
            
            st.download_button(
                label="📝 Özet İndir",
                data=summary_text,
                file_name=f"futbol_ozet_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
        
        # Quick actions
        st.subheader("⚡ Hızlı İşlemler")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📋 Ana Liste Kopyala"):
                main_names = [p['name'] for p in main_list]
                main_text = "🎯 Ana Liste: " + ", ".join(main_names)
                st.code(main_text)
        
        with col2:
            if st.button("📋 Bekleme Listesi Kopyala"):
                waiting_names = [p['name'] for p in waiting_list]
                waiting_text = "⏳ Bekleme: " + ", ".join(waiting_names)
                st.code(waiting_text)
        
        with col3:
            if st.button("📋 Tam Özet Kopyala"):
                summary = f"⚽ Futbol Kayıt Özeti\nAna: {len(main_list)} | Bekleme: {len(waiting_list)} | Yedek: {len(reserve_list)}"
                st.code(summary)
    
    elif not st.session_state.attendance_data.empty:
        # Show old system data if exists but no new registrations
        st.info("📱 Eski WhatsApp mesaj verisi mevcut. Yeni kayıt sistemini kullanmak için sidebar'dan isim kayıt edin.")
        
        # Display old system data in a collapsed section
        with st.expander("📊 Eski Mesaj Verilerini Görüntüle"):
            total_responses = len(st.session_state.attendance_data)
            yes_count = len(st.session_state.attendance_data[st.session_state.attendance_data['response'].isin(['Yes', 'Evet'])])
            maybe_count = len(st.session_state.attendance_data[st.session_state.attendance_data['response'].isin(['Maybe', 'Belki'])])
            no_count = len(st.session_state.attendance_data[st.session_state.attendance_data['response'].isin(['No', 'Hayır'])])
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Toplam", total_responses)
            with col2:
                st.metric("Evet", yes_count)
            with col3:
                st.metric("Belki", maybe_count)
            with col4:
                st.metric("Hayır", no_count)
            
            st.dataframe(st.session_state.attendance_data, use_container_width=True)
    
    else:
        # Welcome screen
        st.markdown("""
        <div style="text-align: center; padding: 3rem; background-color: #f8f9fa; border-radius: 15px; margin: 2rem 0;">
            <h2>🎯 Futbol Sevenler Kayıt Sistemi'ne Hoş Geldiniz!</h2>
            <p style="font-size: 1.2rem; color: #666;">
                Futbol maçınız için profesyonel oyuncu kayıt sistemi
            </p>
            
            <h3>📝 Nasıl Kullanılır:</h3>
            <ol style="text-align: left; display: inline-block;">
                <li>Sol panel'den adınızı ve soyadınızı yazın</li>
                <li>"Kayıt Ol" butonuna tıklayın</li>
                <li>Listenizde yerinizi görün</li>
                <li>Kayıt listelerini takip edin</li>
            </ol>
            
            <h3>✨ Sistem Özellikleri:</h3>
            <ul style="text-align: left; display: inline-block;">
                <li>🎯 Ana Liste: İlk 10 kişi kesin oynar</li>
                <li>⏳ Bekleme Listesi: 11-18 arası oyuncular</li>
                <li>📝 Yedek Listesi: 18+ oyuncular</li>
                <li>📊 Gerçek zamanlı istatistikler</li>
                <li>📤 Excel, CSV, TXT indirme</li>
                <li>🕒 Cumartesi 13:00 deadline</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # Demo button
        if st.button("🧪 Demo Verisi Yükle", type="primary"):
            demo_players = [
                {'name': 'Ali Veli', 'position': 1, 'timestamp': '2025-10-13 10:30:00'},
                {'name': 'Mehmet Özkan', 'position': 2, 'timestamp': '2025-10-13 10:35:00'},
                {'name': 'Ayşe Yılmaz', 'position': 3, 'timestamp': '2025-10-13 10:40:00'},
                {'name': 'Fatma Kaya', 'position': 4, 'timestamp': '2025-10-13 10:45:00'},
                {'name': 'Ahmet Şahin', 'position': 5, 'timestamp': '2025-10-13 10:50:00'},
                {'name': 'Zeynep Arslan', 'position': 11, 'timestamp': '2025-10-13 11:00:00'},
                {'name': 'Murat Koç', 'position': 12, 'timestamp': '2025-10-13 11:05:00'},
                {'name': 'Elif Doğan', 'position': 19, 'timestamp': '2025-10-13 11:10:00'},
            ]
            st.session_state.registered_players = demo_players
            st.success("Demo verisi yüklendi! Sayfayı kaydırarak sonuçları görün.")
            st.rerun()

if __name__ == "__main__":
    main()