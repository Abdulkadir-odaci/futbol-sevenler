import streamlit as st
import pandas as pd
from datetime import datetime
from utils import RegistrationManager
import json
import os
from pathlib import Path

st.set_page_config(
    page_title="Futbol Sevenler",
    page_icon="⚽",
    layout="centered",
    initial_sidebar_state="collapsed"  # Sidebar mobilde kapalı başlar
)

st.markdown("""
<style>
.main-header {
    font-size: 2rem;
    color: #1f77b4;
    text-align: center;
    margin-bottom: 1rem;
    font-weight: bold;
}
.stButton > button {
    background-color: #1f77b4;
    color: white;
    border-radius: 20px;
}
.player-card {
    padding: 0.5rem;
    margin: 0.3rem 0;
    border-radius: 8px;
    border-left: 4px solid;
}
.playing { border-left-color: #28a745; background-color: #d4edda; }
.waiting { border-left-color: #ffc107; background-color: #fff3cd; }
.reserve { border-left-color: #dc3545; background-color: #f8d7da; }

/* Mobil için özel ayarlar */
@media (max-width: 768px) {
    .main-header { 
        font-size: 1.5rem; 
    }
    /* Sidebar butonu daha küçük */
    [data-testid="collapsedControl"] {
        font-size: 0.8rem !important;
        padding: 0.3rem !important;
    }
    /* Metrikler mobilde daha kompakt */
    [data-testid="stMetricValue"] {
        font-size: 1.2rem !important;
    }
    /* Player kartları mobilde daha dar */
    .player-card {
        padding: 0.6rem 0.4rem;
        font-size: 0.9rem;
    }
}
</style>
""", unsafe_allow_html=True)

def get_player_status(position, total_count):
    """Determine if player is playing, waiting, or reserve based on even/odd logic"""
    if position <= 10:
        return 'playing'
    elif position <= 18:
        # For positions 11-18, check if total count makes an even number
        # If current total is odd, the last person waits
        if total_count % 2 == 1 and position == total_count:
            return 'waiting'
        else:
            return 'playing'
    else:
        return 'reserve'

def load_players():
    """JSON dosyasından oyuncuları yükle"""
    try:
        data_file = Path("players_data.json")
        if data_file.exists():
            with open(data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        st.error(f"Veri yükleme hatası: {e}")
    return []

def save_players(players):
    """Oyuncuları JSON dosyasına kaydet"""
    try:
        with open("players_data.json", 'w', encoding='utf-8') as f:
            json.dump(players, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"Veri kaydetme hatası: {e}")
        return False

def backup_to_archive():
    """Haftalık verileri arşive kaydet - VERİ SİLİNMEZ"""
    try:
        # Archive klasörü oluştur
        archive_dir = Path("archive")
        archive_dir.mkdir(exist_ok=True)
        
        # Aktif veriyi oku
        data_file = Path("players_data.json")
        if data_file.exists():
            with open(data_file, 'r', encoding='utf-8') as f:
                current_data = json.load(f)
            
            # Hafta numarası ile arşiv dosyası oluştur
            week_num = datetime.now().isocalendar()[1]
            year = datetime.now().year
            archive_file = archive_dir / f"week_{year}_{week_num}.json"
            
            # Arşiv dosyasına kaydet
            with open(archive_file, 'w', encoding='utf-8') as f:
                archive_entry = {
                    'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'week': week_num,
                    'year': year,
                    'players': current_data
                }
                json.dump(archive_entry, f, ensure_ascii=False, indent=2)
            
            return True
    except Exception as e:
        print(f"Arşiv hatası: {e}")
        return False

def main():
    st.markdown('<h1 class="main-header">⚽ Futbol Sevenler</h1>', unsafe_allow_html=True)
    
    if 'registration_manager' not in st.session_state:
        st.session_state.registration_manager = RegistrationManager()
    
    # İlk açılışta JSON'dan yükle
    if 'registered_players' not in st.session_state:
        st.session_state.registered_players = load_players()
    
    # Hafta başında otomatik backup ve temizleme (Pazartesi sabahı) - Sadece bir kez
    if 'last_cleanup_date' not in st.session_state:
        st.session_state.last_cleanup_date = None
    
    today = datetime.now().date()
    # Pazartesi ve daha önce temizlenmediyse
    if datetime.now().weekday() == 0 and st.session_state.last_cleanup_date != today:
        # BACKUP AL - Veri silinmeden önce arşive kaydet
        if backup_to_archive():
            st.info("📦 Geçmiş hafta verisi arşivlendi ve korunuyor...")
        
        # Şimdi aktif listeyi temizle
        st.session_state.registered_players = []
        save_players([])
        st.session_state.last_cleanup_date = today
        st.success("✅ Yeni hafta başladı! Arşiv dosyada korunuyor.")
    
    deadline = datetime.now().replace(hour=13, minute=0, second=0, microsecond=0)
    is_deadline_passed = datetime.now().weekday() == 6 and datetime.now() > deadline
    
    # Test aşaması uyarısı - Kırmızı not
    st.error("⚠️ **TEST AŞAMASI** - Cuma gününden itibaren gerçek oylama buradan olacaktır! Oylama pazar saat 13:00 dan sonra kitlenicek ve kullanicilar ekleme yapamayacak. Toplam sayi tek sayi ise, oyuncu beklemede gozukecek ve sayi cift olunca listeye obur oyuncu ile beraber dahil olucak. Lutfen kullanici isminizi girin ve cumaya kadar test yapalim, boylelikle herkes sistemin nasil calistigini gormus olur. Ektra oneri ve fikir icin waatsaptan bildiriniz.")
    
    if is_deadline_passed:
        st.error("🚫 KAYIT SÜRESİ DOLDU! Kayıtlar Pazar saat 13:00'a kadar alınır. Maç saat 20:00'de başlayacak.")
    elif datetime.now().weekday() == 6:
        time_left = deadline - datetime.now()
        st.warning(f"⏰ Kayıt için {time_left.seconds//3600} saat {(time_left.seconds//60)%60} dakika kaldı! Maç saat 20:00'de.")
    
    # Kurallar - Mobilde küçük expander
    with st.expander("ℹ️ Bilgi ve Kurallar"):
        st.markdown("""
        **🕒 Kayıt:** Pazar 13:00'a kadar | **⚽ Maç:** 20:00  
        **👥 Sistem:** Çift sayı = Hepsi oynar | Tek sayı = 1 kişi bekler  
        **📊 Kapasite:** Maks 18 sahada | 18+ yedek
        """)
    
    # Kayıt formu - Tek satırda
    if not is_deadline_passed:
        col1, col2 = st.columns([3, 1])
        with col1:
            player_name = st.text_input(
                "Ad Soyad",
                placeholder="Adınızı yazın",
                label_visibility="collapsed"
            )
        with col2:
            if st.button("📝 Kayıt", type="primary", use_container_width=True):
                if player_name.strip():
                    result = st.session_state.registration_manager.register_player(
                        player_name.strip().title(), 
                        st.session_state.registered_players
                    )
                    if result['success']:
                        st.session_state.registered_players = result['player_list']
                        # JSON'a kaydet
                        if save_players(st.session_state.registered_players):
                            st.success(f"✅ {result['message']}")
                        st.rerun()
                    else:
                        st.error(f"❌ {result['message']}")
                else:
                    st.error("❌ Lütfen adınızı yazın!")
    
    # Silme bölümü - Kompakt
    if st.session_state.registered_players and not is_deadline_passed:
        with st.expander("🗑️ Kayıt Sil"):
            col1, col2 = st.columns([3, 1])
            with col1:
                player_to_remove = st.selectbox(
                    "Oyuncu seç",
                    ["Seçiniz..."] + [p['name'] for p in st.session_state.registered_players],
                    label_visibility="collapsed"
                )
            with col2:
                if st.button("🗑️ Sil", use_container_width=True) and player_to_remove != "Seçiniz...":
                    st.session_state.registered_players = [
                        p for p in st.session_state.registered_players 
                        if p['name'] != player_to_remove
                    ]
                    st.session_state.registration_manager.reorder_positions(st.session_state.registered_players)
                    # JSON'a kaydet
                    save_players(st.session_state.registered_players)
                    st.success(f"✅ {player_to_remove} silindi!")
                    st.rerun()
    
    # Oyuncu sayıları her zaman gösterilir (kayıt olsun ya da olmasın)
    col1, col2, col3, col4 = st.columns(4)
    
    total_registered = len(st.session_state.registered_players)
    
    # Calculate playing, waiting, reserve based on even/odd logic
    playing_count = 0
    waiting_count = 0
    reserve_count = 0
    
    for player in st.session_state.registered_players:
        status = get_player_status(player['position'], total_registered)
        if status == 'playing':
            playing_count += 1
        elif status == 'waiting':
            waiting_count += 1
        else:  # reserve
            reserve_count += 1
    
    with col1:
        st.metric("Toplam Kayıt", total_registered)
    with col2:
        st.metric("Oynuyor 🎯", playing_count)
    with col3:
        st.metric("Bekliyor ⏳", waiting_count)
    with col4:
        st.metric("Yedek 📝", reserve_count)
    
    st.markdown("---")
    
    # Tabs for player list and team selection
    tab1, tab2 = st.tabs(["👥 Oyuncu Listesi", "🟦 Takım Seçme"])
    
    # TAB 1: Oyuncu Listesi
    with tab1:
        if st.session_state.registered_players:
            st.subheader("👥 Kayıtlı Oyuncular")
            
            # Single list view with status indicators
            for player in st.session_state.registered_players:
                status = get_player_status(player['position'], total_registered)
                team = player.get('team', '⚪')  # Get team, default to white circle
                
                if status == 'playing':
                    status_emoji = "✅"
                    status_text = "Oynuyor"
                    card_color = "#d4edda"
                elif status == 'waiting':
                    status_emoji = "⏳"
                    status_text = "Bekliyor"
                    card_color = "#fff3cd"
                else:  # reserve
                    status_emoji = "📝"
                    status_text = "Yedek"
                    card_color = "#f8d7da"
                
                st.markdown(f"""
                <div class="player-card" style="background-color: {card_color}; padding: 0.8rem; margin: 0.5rem 0; border-radius: 10px; border-left: 4px solid {'#28a745' if status == 'playing' else '#ffc107' if status == 'waiting' else '#dc3545'};">
                    <strong style="font-size: 1.1rem;">{player['position']}. {player['name']} {team}</strong>
                    <span style="float: right; font-weight: bold;">{status_emoji} {status_text}</span>
                    <br>
                    <small style="color: #666;">📅 {player['timestamp']}</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("👥 Henüz kayıt yapan yok suan icin yok.")
    
    # TAB 2: Takım Seçimi
    with tab2:
        st.subheader("🟦🟨 Takım Seçimi")
        st.markdown("Adınızı seçin ve hangi takımda oynamak istediğinizi belirtin")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            selected_player = st.selectbox(
                "Oyuncu seç",
                ["Seçiniz..."] + [p['name'] for p in st.session_state.registered_players],
                label_visibility="collapsed",
                key="team_select"
            )
        
        with col2:
            team_choice = st.selectbox(
                "Takım seç",
                ["⚪ Takımsız", "🟦 Mavi Takım", "🟨 Sarı Takım"],
                label_visibility="collapsed",
                key="team_choice"
            )
        
        with col3:
            if st.button("✅ Takım Seç", use_container_width=True):
                if selected_player != "Seçiniz...":
                    # Find player and update team
                    for player in st.session_state.registered_players:
                        if player['name'] == selected_player:
                            if "Mavi" in team_choice:
                                player['team'] = "🟦"
                            elif "Sarı" in team_choice:
                                player['team'] = "🟨"
                            else:
                                player['team'] = "⚪"
                            break
                    # Save to JSON
                    save_players(st.session_state.registered_players)
                    st.success(f"✅ {selected_player} {team_choice} seçildi!")
                    st.rerun()
                else:
                    st.error("Lütfen bir oyuncu seçin!")
        
        # Takım özeti
        st.markdown("---")
        st.subheader("📊 Takım Özeti")
        
        col1, col2, col3 = st.columns(3)
        
        blue_players = [p for p in st.session_state.registered_players if p.get('team') == '🟦']
        yellow_players = [p for p in st.session_state.registered_players if p.get('team') == '🟨']
        no_team = [p for p in st.session_state.registered_players if p.get('team') in ['⚪', None]]
        
        with col1:
            st.metric("🟦 Mavi Takım", len(blue_players))
            if blue_players:
                for p in blue_players:
                    st.write(f"  • {p['name']}")
        
        with col2:
            st.metric("🟨 Sarı Takım", len(yellow_players))
            if yellow_players:
                for p in yellow_players:
                    st.write(f"  • {p['name']}")
        
        with col3:
            st.metric("⚪ Takımsız", len(no_team))
            if no_team:
                for p in no_team:
                    st.write(f"  • {p['name']}")

if __name__ == "__main__":
    main()
