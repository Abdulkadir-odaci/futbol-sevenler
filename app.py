import streamlit as st
import pandas as pd
from datetime import datetime
from utils import RegistrationManager

st.set_page_config(
    page_title="Futbol Sevenler",
    page_icon="⚽",
    layout="centered"
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
@media (max-width: 768px) {
    .main-header { font-size: 1.5rem; }
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

def main():
    st.markdown('<h1 class="main-header">⚽ Futbol Sevenler</h1>', unsafe_allow_html=True)
    
    if 'registration_manager' not in st.session_state:
        st.session_state.registration_manager = RegistrationManager()
    if 'registered_players' not in st.session_state:
        st.session_state.registered_players = []
    
    deadline = datetime.now().replace(hour=13, minute=0, second=0, microsecond=0)
    is_deadline_passed = datetime.now().weekday() == 6 and datetime.now() > deadline
    
    if is_deadline_passed:
        st.error("🚫 KAYIT SÜRESİ DOLDU! Kayıtlar Pazar saat 13:00'a kadar alınır. Maç saat 20:00'de başlayacak.")
    elif datetime.now().weekday() == 6:
        time_left = deadline - datetime.now()
        st.warning(f"⏰ Kayıt için {time_left.seconds//3600} saat {(time_left.seconds//60)%60} dakika kaldı! Maç saat 20:00'de.")
    
    with st.sidebar:
        with st.expander("ℹ️ BİLGİ ve KURALLAR", expanded=False):
            st.markdown("""
            ### 📋 KURALLAR
            
            **🕒 KAYIT SÜRESİ:**
            - Pazar saat 13:00'a kadar
            - Maç saat 20:00'de başlayacak
            
            **👥 MAÇ SİSTEMİ:**
            - Çift sayıda oyuncu = Herkes oynar
            - Tek sayıda oyuncu = 1 kişi bekler
            - Maksimum 18 kişi sahada
            - 18+ kişi = Yedek listesinde
            """)
        
        st.markdown("---")
        st.header("👤 KAYIT")
        
        if is_deadline_passed:
            st.warning("⏰ Kayıt süresi sona erdi")
        else:
            player_name = st.text_input(
                "Ad Soyad:",
                placeholder="Örnek: Ali Veli"
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
        
        if st.session_state.registered_players and not is_deadline_passed:
            st.markdown("---")
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
                st.session_state.registration_manager.reorder_positions(st.session_state.registered_players)
                st.success(f"✅ {player_to_remove} kaydı silindi!")
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
    
    # Oyuncu listesi (varsa)
    if st.session_state.registered_players:
        st.markdown("---")
        st.subheader("👥 Kayıtlı Oyuncular")
        
        # Single list view with status indicators
        for player in st.session_state.registered_players:
            status = get_player_status(player['position'], total_registered)
            
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
                <strong style="font-size: 1.1rem;">{player['position']}. {player['name']}</strong>
                <span style="float: right; font-weight: bold;">{status_emoji} {status_text}</span>
                <br>
                <small style="color: #666;">📅 {player['timestamp']}</small>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("👥 Henüz kayıt yapan yok reis.")

if __name__ == "__main__":
    main()
