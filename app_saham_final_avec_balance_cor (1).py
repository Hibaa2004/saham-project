import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import numpy as np
from datetime import datetime
import base64

# Configuration de la page
st.set_page_config(
    page_title="Saham Bank - Analyse de Données",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        text-align: center;
        background: linear-gradient(135deg, #1a4d3e 0%, #2d5f4e 100%);
        padding: 2.5rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .metric-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border-left: 5px solid #ff6b35;
    }
    
    .metric-value {
        font-size: 3em;
        font-weight: bold;
        color: #1a4d3e;
        margin: 0;
    }
    
    .metric-label {
        font-size: 1.1em;
        color: #6c757d;
        margin-top: 0.5rem;
    }
    
    .login-box {
        max-width: 450px;
        margin: 5rem auto;
        background: white;
        padding: 3rem;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
    }
    
    .module-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        cursor: pointer;
        transition: all 0.3s;
        border: 3px solid transparent;
    }
    
    .module-card:hover {
        border-color: #ff6b35;
        transform: translateY(-5px);
        box-shadow: 0 8px 20px rgba(255, 107, 53, 0.3);
    }
    
    .module-card.active {
        border-color: #1a4d3e;
        background: #f0f8f5;
    }
    
    .warning-box {
        background: #fff3cd;
        border-left: 5px solid #ffc107;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .info-box {
        background: #d1ecf1;
        border-left: 5px solid #17a2b8;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .success-box {
        background: #d4edda;
        border-left: 5px solid #28a745;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #ff6b35 0%, #ff8c61 100%);
        color: white;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-weight: bold;
        border: none;
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #ff8c61 0%, #ff6b35 100%);
        transform: translateY(-2px);
    }
    
    h1, h2, h3 {
        color: #1a4d3e;
    }
    
    .logo-container {
        text-align: center;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialisation des variables de session
if 'show_welcome' not in st.session_state:
    st.session_state.show_welcome = True  # Activer la page d'accueil
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = ''
if 'selected_module' not in st.session_state:
    st.session_state.selected_module = None
if 'uploaded_files_bam' not in st.session_state:
    st.session_state.uploaded_files_bam = []
if 'combined_data_bam' not in st.session_state:
    st.session_state.combined_data_bam = None
if 'cleaning_report_bam' not in st.session_state:
    st.session_state.cleaning_report_bam = None
if 'processing_done' not in st.session_state:
    st.session_state.processing_done = False

# Variables pour Visualisations Saham Bank
if 'saham_referentiel' not in st.session_state:
    st.session_state.saham_referentiel = None
if 'saham_financial' not in st.session_state:
    st.session_state.saham_financial = None
if 'saham_aggregated' not in st.session_state:
    st.session_state.saham_aggregated = None

# Variables pour les totaux BAM (référence pour PDM)
if 'total_depots_bam' not in st.session_state:
    st.session_state.total_depots_bam = None
if 'total_credits_bam' not in st.session_state:
    st.session_state.total_credits_bam = None

# Fonctions de calcul des totaux
def calculate_total_depots(df):
    """Calcule le total des dépôts"""
    if 'Montant_Depots' in df.columns:
        return df['Montant_Depots'].sum()
    return 0

def calculate_total_credits(df):
    """Calcule le total des crédits"""
    if 'Montant_Credits' in df.columns:
        return df['Montant_Credits'].sum()
    return 0

def calculate_total_guichets(df):
    """Calcule le total des guichets"""
    if 'Nombre_Guichets' in df.columns:
        return df['Nombre_Guichets'].sum()
    return 0

# Logo Saham encodé en base64
SAHAM_LOGO_BASE64 = "/9j/4AAQSkZJRgABAQAAAQABAAD/4gHYSUNDX1BST0ZJTEUAAQEAAAHIAAAAAAQwAABtbnRyUkdCIFhZWiAH4AABAAEAAAAAAABhY3NwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAA9tYAAQAAAADTLQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAlkZXNjAAAA8AAAACRyWFlaAAABFAAAABRnWFlaAAABKAAAABRiWFlaAAABPAAAABR3dHB0AAABUAAAABRyVFJDAAABZAAAAChnVFJDAAABZAAAAChiVFJDAAABZAAAAChjcHJ0AAABjAAAADxtbHVjAAAAAAAAAAEAAAAMZW5VUwAAAAgAAAAcAHMAUgBHAEJYWVogAAAAAAAAb6IAADj1AAADkFhZWiAAAAAAAABimQAAt4UAABjaWFlaIAAAAAAAACSgAAAPhAAAts9YWVogAAAAAAAA9tYAAQAAAADTLXBhcmEAAAAAAAQAAAACZmYAAPKnAAANWQAAE9AAAApbAAAAAAAAAABtbHVjAAAAAAAAAAEAAAAMZW5VUwAAACAAAAAcAEcAbwBvAGcAbABlACAASQBuAGMALgAgADIAMAAxADb/2wBDAAUDBAQEAwUEBAQFBQUGBwwIBwcHBw8LCwkMEQ8SEhEPERETFhwXExQaFRERGCEYGh0dHx8fExciJCIeJBweHx7/2wBDAQUFBQcGBw4ICA4eFBEUHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh7/wAARCAHGAekDASIAAhEBAxEB/8QAHAABAAIDAQEBAAAAAAAAAAAAAAEGAgMEBQcI/8QAMhAAAgEDBAEEAQMDBAMBAQAAAAECAwQRBRIhMUEGEyJRYRQycSNCgTNScpFlYsEkU//EABwBAQABBQEBAAAAAAAAAAAAAAABAgQFBgcDCP/EAC0RAAICAgICAgICAgICAwEAAAABAgMEEQUhBhITMSJBFFEjMkJhM4EHFTRi/9oADAMBAAIRAxEAPwD8/gA9TCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABKAABUiH30AGmu+AH0UgAyUCuKTIBLIKGyWtAAAAAAAADQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABKAABUh/RCJBHy+itIr0SACdAAAgkAApYAAIIYYSb46BDG9BfZvt7SnUTTqNzzwmb5aVeRhuVPdF9YPFCU11LB6KF9dUf2VX/nk8X7N9F7VKv6maalOpST305Qx9oxhlrODsUNXjU+N5ShNfeD2U46PdR2xqe3J9LBQ7XEyEONqv7gV0HdudArOLnbyVRfycm4srqg/nSaIWTH9lN3E2Vr8Vs0APKeGsA942Rl9GJnTOL76AAPX1etni5JfZDIJIKHLQAAJT2SkAACQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACSlPb0AAh1+yt1+wcEyFFLoz7eDdSt60lxbzl9cFMrqo/bPenAuseoxPOTk6FPTLyssU6Oz/AJI2PQr/AGvO3rwWzzq/7L5cFmv6iclkI98tPr26fu05NfweTbHe1FP/ACe1V8LFtMtreKyav91oxYIqZTwQj3Mfpp6ZkAClnowACCAGAEQQlgkBE9FLi2OFywpx7jwyVj8B7fGCZRi19HvVfdV/qz2WGp3dnLNOpJp9pvJ2rfXqNd7LqjFL+CsEp+GW1mLGS6Mvi83OvqzsuMdM0zUI7qTSf1k5l96erUpP2luXg5Nvd1beWadRr/J3dL9RuLUa/wAl+TG2V219xNjquwMxf5OmcG4tatB/OLRpL46lhqNPDjHL/By73025pytZxx9ZJr5CcXqw8MnxyN0fensqxDaPbeafc2T/AKlNy/hHhk5OWNrX+DK131TXTNWyuOvxpalEkDDBX9/RZNa+wABop0wAwuSRvS2AAQQ2AACoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAq0AACjZDIbwTBOXRKx5DhUk8Q/b5EpxitnrTRObSiTODisvH+Hk9em6dXvJKUYP20/k3xwdTQdGjUpqpXXHhMsEFTpUnSpU1FPgwGZyvr+MToHBeJW3tWWLo5lto9lSUZyk5TXjB04OlCKjCnHj8GtxaJzg1+3PnN9M6pieO4lFa0uzOU5PhLAzLHZhuMslg7bN7bMisampaUScxxunBTzxhnF1/TKfs+/brbLto7E+hUpqvazg+MLsyWFlzUktmv8APcXTZjys12fPsybe7tPAPReUlTuZxXhmnBveNJSqTPnrKqcMiQAaBUUN7AABAAAADAH0U7MGvslLjgywCdjYABGyJQ9jBrkknAwJdoivdb2mbaNzcUpJ0ptY8Z7LFo+vJJQuouLf9yZWYiTeeyxuwq7V39myYHkN2M1H9H0aEqF1T+E6c448pNnK1DRKFfM6K2z+nwVeyvrm1knTqPC8Fr0bWqN1DFw1Gp4MPbi248tr6N7xeVweSgoWrTKzf6bdWsvnCTj9pZPGfRKlWnNbXTU4s5eo6JaV4Opb/CX0e9PK+v4ssOS8R6+WnvZTyM8nsvLC5t5NOm2vtHhaafJmMfIjb9HP8vArl9FoVnUlBp9rDPPv9un5PD9Q6wof9Ig+u2XODiOclvtGK5zmqsOtkZk5SYmTGz7NJMS0vHJxNR1xPNC2+KXGTgzk5ScpPLfk26hbyt7qVKSxzwedm8YVEHBNHz9z/I5U8mUJPol4wQQmSZb6NaT/ZD7AfYJKWwACnYAAIYAACIb0A/lwuMAiXC58kN6RXCDlJJI9OiWU728UF+1csu7UaVGFvFL4+TnemrRWtgq8lzLydFJtObNP5PL9n6HcPEOJ/j1K6SMZPa1jvyzi+rbvdttabSS7SOxf1Y0LGVRvEn0Ui7qyrV5VG+Wz04nEf+zRYea8y4f4kYriGF0RjAX+nFfk32ttUua0adOLll8/wbPc41V72cvxMeWbb2j1aFYyvLpPD2xfJcJx2RjSXSNGl0adjbunHiTwemTSjvb4NSzcid09I7L43xUOPo+SX2jwazdK0s5RT+T6KdKbk5Tk+ZM6XqO7VxcbYyyonKM3xeH6w2znHlPLvMyZQT+jHySiQZlrSNOgvySOh6bt3W1DbN5T8M9/qXTZ209umm4fg2ek7fNX3scqPB3JydWOypHcvBrV/IOu3R1Pi/GFm4bZQMY7Hg7etaTOi3Xox3RfePBw8OTePDMziZcbEmaJynDzwZuCQbMU3ntmWOcEwjyi82m+jBVRlvTMqjy0k/B3vR0X+pqPHgr8Ibazl9otXpOnKFOpOSxFvgxHJz1Bm5eHYjszdnVb5f8k5RhLmbwQkaLL/Zn0LWvjjFGXDM6c5Q/azCKMsEqxx+iHUp/wC30Zu4lnPT/Brq1JVP3PKIxySl9k/LJlPwUx7SMecE54ElwYxjkp+/s9ox93s220cTnUb4USl69VdW+qSz/cXVONO0qyk8LBQb6W+6qNcrcbPw9O3tHJvP8pacNmlNmRik8k4NrcfVI5EpeyRIAKSQAAAAAAACpMhpv6DM6dJ1JRiouTf14FGlOrNKCzyWvRNKo2dP9TcZlN9LwjG5uSqU+zZeA8fuzbU9dDSNLo2tONSqt82v+jpVJ1G1tfx6wTNqSUuE/peDGPDf5NPzcqdjO5cTwVWHCK/ownnc8snPAx8l9eSJqcZ4xwY7tmadkHNxTJYi2pLBktvkh7dywSm0ymUfaDicj1Tab3SuIrpfJorc1jJfa1JV7apRks7lwUi9oOjXlTkumbbxGZ7fjI4r5fxEq7HbFfZ5UZRIaJRssmn9HN1v9kPsjkl9gjY7AAIJQAAJABjJ4JKXHfZkezSqH6mts2N4Z4qbcm/4LZ6OtVTo/qai4ksox/I5Kphs2XxjBeZkrr6OtXhsoQpQWElyZUecLx5FeSlM1Vaqo29SpJ4xE0iPtffs7tZH+LhvfWkcH1VeJ1Vb03wV9rBnc1HXvJ1G8rIowq16mymss3bGiqqezhHKZc+RypRMqFCdWsqcFlly0XT6dnQ9ySW9rk8ug6X7DVetxNcpfZ0pSdSq85X0kYXPz9pxR0LxTxnpXWL6GHKfXB4tfvI2lqqKeZz4TXg6FarGjZznJpSiUrU7uV7cOb/auEW3FUSvl7NF75Ty6xaHVW9HlqJ5bby88s25FSeODGL5Nzrh6LSOJX3+8nJ/bMyYRc5KK7bMYczSO56a0517j3qqeyL4PDKyIVRe2ZPheMsy7l6rZ3NMoSs9Jg3H5s9UeOTO4qSknSwsRfBrW7HJoOXa5zcon0Tw2EsWhRn0ZpwnmE1mL7OPquhQk3UtMRzzg6knjozpSk+X0emJmyq6LXmOBozItxXZRbq1qUqjhUi4NcZaPMoyVRLcmmfQbqnp9xHZWpuT+znrQ7GU8rdFfhmxVcvFLs5jm+C3uftD6K1Z21S5qKMYvvBdrelG3tYUo4ylyzTQoWtm1KjBuaN9KMp5k3jPgw/I8grPo3PxzxtcdBTn9mOOTOUYwoupKSSJccfk5Pqi5lRoxpR43Fhj4ztl0bDzPKQw6tyOhb1adbOySyvBtwvLKfpV7OzuFNtyi+0y1U6sLqiqlKX+C6y8D4o7SMVw/kdWfL42zY8E9I1xyuw5MxiWjbUk3r9EykKcsvCQSybqSVLdUl1FFcK3OSRb5mRHDg22cr1HcOja+zGXL7Ki++Toa7duveSa6yc5PJvnGY3wVpnz/wCXcj/JvaRIAMnLtGowjpAAHmVAAEgAAABJtpLlsJZjnwdf03aK4rqq+VBlrlX/ABGV4bAlm3qCOl6d0tUKfu3Ec55WTsTfwwlnHSJrVZVEotYS4MM+DS+RyZTn0z6A4TjYYlSSXZjGMd258TfaNkUY5MovLwY+MvaXZmcibjA8GvXX6alBUntbfOPJ7qFVXNrCsvKKv6inOep7Gmoro63pe4dazdu+4ftRnJ4UVT7o0fF5Xee65PR75kRM5RaWWuOiF0YGXTN8Uk47RlTbycT1ZabmrmisJfuSO5AxlThVhKE+mZDCv+KWzX+c4v8AmYsnFdooT6IPVq1CVteShJYXaPKjeMa1WQ2j555GiWNc4NEPsEsjkuVos9AAE+oAAI0yGPBi+Q8iCcpYIfRVBe79Ub7Kg61anTj3KWH/AAXylSjbW8beH7YLCSK56UtY1K8q0+qfn8ljqVN8d65yalzWV7P1Oy+FcYqalJrs1c7sZOb6muMWKpQ+M2+f4OtSW6cX9FT9RXLr6k34isFtxVW5dmZ8z5F4+MoJnLVOqkoQjulJ9lt9PabTt6EbirFKb5OZodfT7Z77nbOfa/B2oaxp0pucquPpGbzHOK1FGicBVgxn8tr7PbXk8xSzhcoxhJKeZLLOfca7aRhNUYylJrhmzRr+jqWdy2Shw19muW4du/ZnScXnMWa+Kt6MtXsa93FOlUcVjlLyV240q5oxcYxcn94Lk5+2pKKwn0jUqkvKLrD5NYq9Gix5Xxqvkdy39lClZXKniVJ/zg3UdPvKs1CnQ4f9zRd24t8wX/RP6j2/jTpr+S6nzia0ka/X/wDHsE+2V/TdBk6i95Ljl5O9SjTtqKpU0kka5VakpZkzbRpe4s5MVmZ0shG1cT43Hjn7IxcnFOb67PJZ61b17p27iljtmfqOurSw29NrBSqUpJqpB4aMlh8YradmD5vyaVGTGuL6Rf5pOTa5j4GWljPB4fT2oU7q39mrJKaXB7sS3NSWOeDEZWNKqX0bdw/I15dakn2a8cmcVlNPolxwRnksnsy83KS0S4pLoJtDIyFt9Eykkvy/RlGWeypa9dyurp7ZYUXg7ut3StbZPOJMptWe6UmvLybfxeN6pSaOR+c8rCT+OBluPdpWpSsqq3ZcH4OfFkz5M5kY0LY60c4wM+zEmrIvsvdtcUbukqlJrP0ZbKninko1rXuaEk6NVxO5Zeo69COKsHJ47Nby+He/xOqcN5zBRSt+zv0ISdRRfx/k5HqXU1Szb0mk/LTObqGvV7lvEXHJyKilUk6k5ZbPbB4r1aciw8h8uqvi1Wxu9xuT7YxglYS4IZsij6rRy7Kt+efvsAAnZ5IAAN7JAAIAAABstlhRi12y5aJbU7Sw9yS5kVOyxUuKSx0+S73UVCjTiutqMBztjj9HTfA8KM7PkaMZSTWfswXYim4oYNNlJt9nZYuMW0iTOmsSzkwMZZJh09kTrVq0cn1NYVpVI3VJJxXeDwaFd/ptQhuUopvDLRCutvt1Ipr8nnu9Ntrlbqa2T+0ZevOfxuEjRszxz60GjUL+k3w8rrBgzY4pp5i0zCUE/JrspeWI/lKSiSYJmSKVW1ssj0RfxWQkmY/k8tt0XTD7Njq1Ixcl+Tywco9lgpyeMSWMfZ5qjy2/spJ4pJx02J8kdY/hGSIJ4J6Nx/QAAhFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAB6NAAAGwAASSgAASDIAAhAAAkpCDYARsyAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACdgHgjJJC5eQSXRsAAJ7GiJ/Y+gB1H/2Q=="

# Page d'accueil
def welcome_page():
    """Page d'accueil sans logo"""
    # Masquer la sidebar
    st.markdown("""
        <style>
        [data-testid="stSidebar"] {
            display: none;
        }
        .welcome-header {
            background: linear-gradient(135deg, #1a4d3e 0%, #2d5f4e 100%);
            padding: 3rem;
            border-radius: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            text-align: center;
        }
        .welcome-title {
            color: white !important;
            font-size: 3em;
            margin: 0;
            font-weight: bold;
        }
        .welcome-subtitle {
            color: #ff6b35;
            font-size: 1.2em;
            margin-top: 1rem;
        }
        .info-section {
            text-align: center;
            margin: 2rem 0;
        }
        </style>
        """, unsafe_allow_html=True)
    
    # Centrer le contenu
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # En-tête avec fond vert
        st.markdown("""
        <div class="welcome-header">
            <h1 class="welcome-title">SAHAM BANK</h1>
            <p class="welcome-subtitle">سهام بنك</p>
            <p style="color: white; font-size: 1em; margin-top: 1rem; font-style: italic;">
                Accélérateur de vos ambitions
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # Titre principal
        st.markdown("""
        <div class="info-section">
            <h2 style="color: #ff6b35;">Application d'Analyse de Données</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Description
        st.markdown("""
        <div class="info-section">
            <p style="color: #6c757d; font-size: 1.1em;">Direction Financière - PFE 2026</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Section modules
        st.markdown("""
        <div class="info-section">
            <p style="color: #1a4d3e; font-size: 1.2em; font-weight: bold;">
                Analyse des bases de données bancaires
            </p>
            <p style="color: #6c757d; font-size: 1.1em;">
                BAM • GPBM • Balance
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # Bouton Commencer
        btn_col1, btn_col2, btn_col3 = st.columns([1, 2, 1])
        with btn_col2:
            if st.button("Commencer", use_container_width=True, type="primary", key="welcome_start"):
                st.session_state.show_welcome = False
                st.rerun()

# Fonction de connexion
def login_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class="login-box">
            <div style="text-align: center; margin-bottom: 2rem;">
                <div style="background: #1a4d3e; padding: 1.5rem; border-radius: 10px; margin-bottom: 1.5rem;">
                    <h1 style="color: white; margin: 0; font-size: 2em;">SAHAM BANK</h1>
                    <div style="color: #ff6b35; font-size: 0.8em; margin-top: 0.5rem;">سهام بنك</div>
                </div>
                <p style="color: #ff6b35; font-size: 1.2em; font-weight: bold;">Application d'Analyse de Données</p>
                <p style="color: #6c757d; font-size: 0.9em;">Direction Financière - PFE 2026</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### Connexion")
        username = st.text_input("Nom d'utilisateur", placeholder="Entrez votre nom")
        password = st.text_input("Mot de passe", type="password", placeholder="Entrez votre mot de passe")
        
        col_a, col_b, col_c = st.columns([1, 2, 1])
        with col_b:
            if st.button("Se Connecter", use_container_width=True):
                if username.lower() in ["hiba", "admin"] and password in ["saham2026", "admin"]:
                    st.session_state.authenticated = True
                    st.session_state.username = username.capitalize()
                    st.rerun()
                else:
                    st.error("Nom d'utilisateur ou mot de passe incorrect")
        
        st.markdown("""
            <div style="margin-top: 2rem; text-align: center; color: #6c757d; font-size: 0.85em;">
                <p>Identifiants de test :</p>
                <p><strong>Utilisateur :</strong> Hiba | <strong>Mot de passe :</strong> saham2026</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Page de sélection du module
def module_selection_page():
    st.markdown(f"""
    <div class="main-header">
        <h1>SAHAM BANK - Analyse de Données</h1>
        <p style="font-size: 1.2em;">Bienvenue, <strong>{st.session_state.username}</strong></p>
        <p style="font-size: 0.9em; opacity: 0.9;">Direction Financière - Projet de Fin d'Études</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.header("Sélectionnez un Module d'Analyse")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="module-card active">
            <h3 style="color: #1a4d3e; margin-top: 2rem;">BAM</h3>
            <p style="color: #6c757d;">Données bancaires</p>
            <p style="color: #6c757d; font-size: 0.9em;">Analyse des dépôts, crédits et guichets</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Accéder au module BAM", use_container_width=True, type="primary"):
            st.session_state.selected_module = "BAM"
            st.rerun()
    
    with col2:
        st.markdown("""
        <div class="module-card">
            <h3 style="color: #6c757d; margin-top: 2rem;">GPBM</h3>
            <p style="color: #6c757d; font-size: 0.9em;">À venir prochainement</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Accéder au module GPBM", use_container_width=True, disabled=True):
            st.info("Module GPBM en développement")
    
    with col3:
        st.markdown("""
        <div class="module-card active">
            <h3 style="color: #1a4d3e; margin-top: 2rem;">Balance</h3>
            <p style="color: #6c757d;">Produits & Charges</p>
            <p style="color: #6c757d; font-size: 0.9em;">Import et analyse balance générale</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Accéder au module Balance", use_container_width=True, type="primary"):
            st.session_state.selected_module = "Balance"
            st.rerun()
    
    st.divider()
    
    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_b:
        if st.button("Déconnexion", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.selected_module = None
            st.rerun()

def get_month_from_filename(filename):
    months_fr = {
        'janvier': 1, 'fevrier': 2, 'mars': 3, 'avril': 4, 'mai': 5, 'juin': 6,
        'juillet': 7, 'aout': 8, 'septembre': 9, 'octobre': 10, 'novembre': 11, 'decembre': 12,
        'jan': 1, 'fev': 2, 'mar': 3, 'avr': 4, 'jun': 6, 'jul': 7, 'aou': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
    }
    
    filename_lower = filename.lower()
    for month_name, month_num in months_fr.items():
        if month_name in filename_lower:
            return month_num
    
    import re
    month_pattern = re.search(r'[_\-\s](\d{1,2})[_\-\s\.]', filename)
    if month_pattern:
        month_num = int(month_pattern.group(1))
        if 1 <= month_num <= 12:
            return month_num
    
    return None

def combine_bam_files(files_data):
    combined_df = pd.DataFrame()
    for file_info in files_data:
        df = file_info['data'].copy()
        df['mois'] = file_info['month']
        combined_df = pd.concat([combined_df, df], ignore_index=True)
    return combined_df

def detect_missing_values(df, data_type):
    report = {
        'data_type': data_type,
        'total_rows': len(df),
        'columns': list(df.columns),
        'missing_details': []
    }
    
    for idx, row in df.iterrows():
        missing_cols = []
        for col in df.columns:
            value = row[col]
            if pd.isna(value) or (isinstance(value, str) and value.strip() == ''):
                missing_cols.append(col)
        
        if missing_cols:
            report['missing_details'].append({
                'row_number': idx + 2,
                'excel_row': idx + 2,
                'missing_columns': missing_cols,
                'data_preview': {col: row[col] for col in df.columns if col not in missing_cols}
            })
    
    report['total_missing_rows'] = len(report['missing_details'])
    report['percentage_complete'] = ((len(df) - len(report['missing_details'])) / len(df) * 100) if len(df) > 0 else 0
    
    return report

def convert_df_to_excel(df, filename):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Data')
    output.seek(0)
    return output

def normalize_bam_columns(df):
    """Normalise les noms de colonnes BAM - version ultra-robuste"""
    df_normalized = df.copy()
    
    # Nettoyer d'abord tous les noms de colonnes
    df_normalized.columns = df_normalized.columns.str.strip()
    
    # Nouvelle stratégie : chercher les colonnes par mot-clé
    new_columns = {}
    
    for col in df_normalized.columns:
        col_lower = col.lower()
        
        # Recherche par mot-clé
        if 'code' in col_lower and 'localit' in col_lower:
            new_columns[col] = 'Code_Localite'
        elif 'localit' in col_lower and 'code' not in col_lower:
            new_columns[col] = 'Localite'
        elif 'nombre' in col_lower and 'guichet' in col_lower:
            new_columns[col] = 'Nombre_Guichets'
        elif 'montant' in col_lower and 'd' in col_lower and 'p' in col_lower:
            # Montant des dépôts
            new_columns[col] = 'Montant_Depots'
        elif 'montant' in col_lower and 'cr' in col_lower:
            # Montant des crédits
            new_columns[col] = 'Montant_Credits'
        elif col_lower == 'mois':
            new_columns[col] = 'mois'
    
    # Renommer
    df_normalized.rename(columns=new_columns, inplace=True)
    
    return df_normalized

def clean_numeric_columns(df):
    """Nettoie les colonnes numériques - version ultra-robuste"""
    df_clean = df.copy()
    numeric_cols = ['Montant_Depots', 'Montant_Credits', 'Nombre_Guichets']
    
    for col in numeric_cols:
        if col in df_clean.columns:
            # Convertir en string
            df_clean[col] = df_clean[col].astype(str)
            
            # Enlever TOUS les types d'espaces (normaux, insécables, tabs, etc.)
            df_clean[col] = df_clean[col].str.replace(r'\s+', '', regex=True)
            
            # Enlever les caractères non-numériques sauf point et virgule
            df_clean[col] = df_clean[col].str.replace(r'[^\d.,]', '', regex=True)
            
            # Remplacer virgule par point pour décimales
            df_clean[col] = df_clean[col].str.replace(',', '.')
            
            # Convertir en numérique (NaN si impossible)
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
            
            # Remplacer NaN par 0
            df_clean[col] = df_clean[col].fillna(0)
    
    return df_clean

def add_direction_regionale(df):
    direction_mapping = {
        'CASABLANCA': 'CASA', 'RABAT': 'CASA', 'SALE': 'CASA', 'MOHAMMEDIA': 'CASA',
        'TEMARA': 'CASA', 'KENITRA': 'CASA', 'SETTAT': 'CASA', 'BERRECHID': 'CASA',
        'FES': 'OUEST', 'MEKNES': 'OUEST', 'TAZA': 'OUEST', 'OUJDA': 'OUEST',
        'BERKANE': 'OUEST', 'NADOR': 'OUEST', 'AL HOCEIMA': 'OUEST',
        'MARRAKECH': 'SUD', 'AGADIR': 'SUD', 'ESSAOUIRA': 'SUD', 'OUARZAZATE': 'SUD',
        'TANGER': 'NORD', 'TETOUAN': 'NORD',
    }
    
    df_with_region = df.copy()
    df_with_region['DirectionRegionale'] = df_with_region['Localite'].apply(
        lambda x: direction_mapping.get(x.upper() if isinstance(x, str) else '', 'OUEST')
    )
    
    return df_with_region

# VISUALISATIONS
def create_powerbi_visualizations(df):
    """Visualisations des données BAM"""
    
    try:
        # IMPORTANT : Normaliser et nettoyer les données
        df = normalize_bam_columns(df)
        df = clean_numeric_columns(df)
        
        # DIAGNOSTIC : Expander pour vérifier les données
        with st.expander("🔍 Diagnostic des Données", expanded=False):
            st.write("**Colonnes du DataFrame :**")
            st.write(df.columns.tolist())
            
            st.write("**Types des colonnes numériques :**")
            if 'Montant_Depots' in df.columns:
                st.write(f"- Montant_Depots : {df['Montant_Depots'].dtype}")
            if 'Montant_Credits' in df.columns:
                st.write(f"- Montant_Credits : {df['Montant_Credits'].dtype}")
            if 'Nombre_Guichets' in df.columns:
                st.write(f"- Nombre_Guichets : {df['Nombre_Guichets'].dtype}")
            
            st.write("**Aperçu des données :**")
            st.dataframe(df.head(10))
            
            st.write("**Totaux calculés :**")
            if 'Montant_Depots' in df.columns:
                st.write(f"- Total Dépôts : {df['Montant_Depots'].sum()/1e6:.2f} Md")
            if 'Montant_Credits' in df.columns:
                st.write(f"- Total Crédits : {df['Montant_Credits'].sum()/1e6:.2f} Md")
            if 'Nombre_Guichets' in df.columns:
                st.write(f"- Total Guichets : {df['Nombre_Guichets'].sum():,.0f}".replace(',', ' '))
        
        # Vérifier que les colonnes nécessaires existent
        required_cols = ['Montant_Depots', 'Montant_Credits', 'Nombre_Guichets', 'Localite']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            st.error(f"Colonnes manquantes : {missing_cols}")
            st.write("Colonnes disponibles :", df.columns.tolist())
            return
        
        st.header("Vue Générale")
        
        # Calculer les totaux
        total_depots = df['Montant_Depots'].sum() / 1e9
        total_credits = df['Montant_Credits'].sum() / 1e9
        total_guichets = df['Nombre_Guichets'].sum() / 1000
        
        # GRANDES MÉTRIQUES
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <p class="metric-value">{total_depots:.0f}Md</p>
                <p class="metric-label">Total Dépôts</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <p class="metric-value">{total_credits:.0f}Md</p>
                <p class="metric-label">Total Crédits</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <p class="metric-value">{total_guichets:.0f}K</p>
                <p class="metric-label">Total Guichets</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # FILTRES
        st.subheader("Filtres")
        
        df_filtered = df.copy()
        
        if 'DirectionRegionale' in df.columns:
            all_regions = ['(Tous)'] + sorted(df['DirectionRegionale'].unique().tolist())
            selected_regions = st.multiselect(
                "Direction Régionale",
                options=all_regions,
                default=['(Tous)']
            )
            
            if '(Tous)' not in selected_regions and selected_regions:
                df_filtered = df[df['DirectionRegionale'].isin(selected_regions)]
        
        st.markdown("---")
        
        # TABLEAU PAR MOIS (seulement si la colonne mois existe)
        if 'mois' in df_filtered.columns:
            st.subheader("Données par Mois")
            
            monthly_summary = df_filtered.groupby('mois').agg({
                'Montant_Credits': 'sum',
                'Montant_Depots': 'sum',
                'Nombre_Guichets': 'sum'
            }).reset_index()
            
            monthly_summary.columns = ['mois', 'Total Credits', 'Depots', 'Total Guichets']
            
            month_names = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
                          'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
            
            monthly_summary['mois'] = monthly_summary['mois'].apply(
                lambda x: month_names[int(x)-1] if 1 <= int(x) <= 12 else str(x)
            )
            
            # Formater les nombres
            monthly_summary['Total Credits'] = monthly_summary['Total Credits'].apply(
                lambda x: f"{x/1e6:.2f} Md"
            )
            monthly_summary['Depots'] = monthly_summary['Depots'].apply(
                lambda x: f"{x/1e6:.2f} Md"
            )
            monthly_summary['Total Guichets'] = monthly_summary['Total Guichets'].apply(
                lambda x: f"{int(x):,}".replace(',', ' ')
            )
            
            st.dataframe(monthly_summary, use_container_width=True, hide_index=True)
            
            st.markdown("---")
        
        # GRAPHIQUES PRINCIPAUX
        col1, col2 = st.columns(2)
        
        with col1:
            # Graphique ligne par mois
            if 'mois' in df_filtered.columns:
                st.subheader("Dépôts et Crédits par mois")
                
                monthly_data = df_filtered.groupby('mois').agg({
                    'Montant_Depots': 'sum',
                    'Montant_Credits': 'sum'
                }).reset_index()
                
                monthly_data['Depots_Md']  = monthly_data['Montant_Depots']  / 1e6
                monthly_data['Credits_Md'] = monthly_data['Montant_Credits'] / 1e6
                monthly_data['mois_nom'] = monthly_data['mois'].apply(lambda x: str(int(x)))
                
                fig_line = go.Figure()
                
                fig_line.add_trace(go.Scatter(
                    x=monthly_data['mois_nom'],
                    y=monthly_data['Depots_Md'],
                    mode='lines+markers',
                    name='Dépôts (Md)',
                    line=dict(color='#1a4d3e', width=3),
                    marker=dict(size=10),
                    hovertemplate='%{x}<br>Dépôts: %{y:.2f} Md<extra></extra>'
                ))
                
                fig_line.add_trace(go.Scatter(
                    x=monthly_data['mois_nom'],
                    y=monthly_data['Credits_Md'],
                    mode='lines+markers',
                    name='Crédits (Md)',
                    line=dict(color='#ff6b35', width=3),
                    marker=dict(size=10),
                    hovertemplate='%{x}<br>Crédits: %{y:.2f} Md<extra></extra>'
                ))
                
                fig_line.update_layout(
                    xaxis_title='',
                    yaxis_title='Montant (Md MAD)',
                    height=350,
                    hovermode='x unified',
                    showlegend=True,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                
                st.plotly_chart(fig_line, use_container_width=True)
            
            # Graphique barres Dépôts par région
            if 'DirectionRegionale' in df_filtered.columns:
                st.subheader("Dépôts par Direction Régionale")
                
                regional_depots = df_filtered.groupby('DirectionRegionale')['Montant_Depots'].sum().reset_index()
                regional_depots['Depots_Md'] = regional_depots['Montant_Depots'] / 1e6
                regional_depots = regional_depots.sort_values('Depots_Md', ascending=False)
                
                fig_bar = px.bar(
                    regional_depots,
                    x='DirectionRegionale',
                    y='Depots_Md',
                    color='Depots_Md',
                    color_continuous_scale='Blues'
                )
                fig_bar.update_traces(hovertemplate='%{x}<br>%{y:.2f} Md<extra></extra>')
                fig_bar.update_layout(
                    xaxis_title='',
                    yaxis_title='Total Dépôts (Md MAD)',
                    height=350,
                    showlegend=False
                )
                
                st.plotly_chart(fig_bar, use_container_width=True)
        
        with col2:
            # Camembert Crédits par région
            if 'DirectionRegionale' in df_filtered.columns:
                st.subheader("Crédits par Direction Régionale")
                
                regional_credits = df_filtered.groupby('DirectionRegionale')['Montant_Credits'].sum().reset_index()
                regional_credits['Credits_Md'] = regional_credits['Montant_Credits'] / 1e6
                
                fig_pie = px.pie(
                    regional_credits,
                    values='Credits_Md',
                    names='DirectionRegionale',
                    color_discrete_sequence=px.colors.sequential.RdBu
                )
                
                fig_pie.update_layout(height=350)
                fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                
                st.plotly_chart(fig_pie, use_container_width=True)
            
            # Graphique barres Guichets par région
            if 'DirectionRegionale' in df_filtered.columns:
                st.subheader("Guichets par Direction Régionale")
                
                regional_guichets = df_filtered.groupby('DirectionRegionale')['Nombre_Guichets'].sum().reset_index()
                regional_guichets = regional_guichets.sort_values('Nombre_Guichets', ascending=False)
                
                fig_guichets = px.bar(
                    regional_guichets,
                    x='DirectionRegionale',
                    y='Nombre_Guichets',
                    color='Nombre_Guichets',
                    color_continuous_scale='Oranges'
                )
                
                fig_guichets.update_layout(
                    xaxis_title='',
                    yaxis_title='Total Guichets',
                    height=350,
                    showlegend=False
                )
                
                st.plotly_chart(fig_guichets, use_container_width=True)
        
        # PAR DIRECTION RÉGIONALE
        if 'DirectionRegionale' in df_filtered.columns and 'mois' in df_filtered.columns:
            st.markdown("---")
            st.header("Par Direction Régionale")
            
            col1, col2 = st.columns(2)
            with col1:
                selected_months = st.multiselect(
                    "Sélectionner les mois",
                    options=sorted(df_filtered['mois'].unique()),
                    default=sorted(df_filtered['mois'].unique()),
                    format_func=lambda x: ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
                                           'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'][int(x)-1]
                )
            
            df_month_filtered = df_filtered[df_filtered['mois'].isin(selected_months)]
            
            st.subheader("Tableau Récapitulatif")
            
            detailed_summary = df_month_filtered.groupby(['DirectionRegionale', 'mois']).agg({
                'Montant_Depots': 'sum',
                'Montant_Credits': 'sum',
                'Nombre_Guichets': 'sum'
            }).reset_index()
            
            detailed_summary.columns = ['DirectionRegionale', 'mois', 'TDepots', 'Total Guichets', 'Total Credits']
            
            month_abbr = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun',
                         'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']
            
            detailed_summary['mois'] = detailed_summary['mois'].apply(
                lambda x: month_abbr[int(x)-1] if 1 <= int(x) <= 12 else str(x)
            )
            
            st.dataframe(detailed_summary, use_container_width=True, hide_index=True)
            
            st.subheader("Comparaisons")
            col1, col2, col3 = st.columns(3)
            
            regional_summary = df_month_filtered.groupby('DirectionRegionale').agg({
                'Montant_Depots': 'sum',
                'Montant_Credits': 'sum',
                'Nombre_Guichets': 'sum'
            }).reset_index()
            
            regional_summary['Depots_Md']  = regional_summary['Montant_Depots']  / 1e6
            regional_summary['Credits_Md'] = regional_summary['Montant_Credits'] / 1e6

            with col1:
                fig1 = px.bar(regional_summary, x='DirectionRegionale', y='Depots_Md',
                             title='Dépôts (Md MAD)', color_discrete_sequence=['#1a4d3e'])
                fig1.update_traces(hovertemplate='%{x}<br>%{y:.2f} Md<extra></extra>')
                fig1.update_layout(height=300, showlegend=False, xaxis_title='', yaxis_title='Md MAD')
                st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                fig2 = px.bar(regional_summary, x='DirectionRegionale', y='Credits_Md',
                             title='Crédits (Md MAD)', color_discrete_sequence=['#ff6b35'])
                fig2.update_traces(hovertemplate='%{x}<br>%{y:.2f} Md<extra></extra>')
                fig2.update_layout(height=300, showlegend=False, xaxis_title='', yaxis_title='Md MAD')
                st.plotly_chart(fig2, use_container_width=True)
            
            with col3:
                fig3 = px.bar(regional_summary, x='DirectionRegionale', y='Nombre_Guichets',
                             title='Guichets', color_discrete_sequence=['#17a2b8'])
                fig3.update_layout(height=300, showlegend=False, xaxis_title='', yaxis_title='')
                st.plotly_chart(fig3, use_container_width=True)
        
        # PAR LOCALITÉ
        st.markdown("---")
        st.header("Par Localité")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader("Dépôts par Localité")
            
            top_localites = df_filtered.groupby('Localite')['Montant_Depots'].sum().reset_index()
            top_localites['Depots_Md'] = top_localites['Montant_Depots'] / 1e6
            top_localites = top_localites.nlargest(15, 'Depots_Md').sort_values('Depots_Md')
            
            fig_loc = px.bar(
                top_localites,
                y='Localite',
                x='Depots_Md',
                orientation='h',
                color='Depots_Md',
                color_continuous_scale='Viridis'
            )
            fig_loc.update_traces(hovertemplate='%{y}<br>%{x:.2f} Md<extra></extra>')
            fig_loc.update_layout(
                height=600,
                showlegend=False,
                xaxis_title='Total Dépôts (Md MAD)',
                yaxis_title=''
            )
            
            st.plotly_chart(fig_loc, use_container_width=True)
        
        with col2:
            st.write("")
            st.write("")
            st.write("")
            
            st.markdown(f"""
            <div class="metric-card" style="margin-bottom: 1rem;">
                <p class="metric-value">{total_depots:.0f}Md</p>
                <p class="metric-label">Total Dépôts</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="metric-card" style="margin-bottom: 1rem;">
                <p class="metric-value">{total_credits:.0f}Md</p>
                <p class="metric-label">Total Crédits</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="metric-card">
                <p class="metric-value">{total_guichets:.0f}K</p>
                <p class="metric-label">Total Guichets</p>
            </div>
            """, unsafe_allow_html=True)
        
        # TABLEAU DÉTAILLÉ
        if 'DirectionRegionale' in df_filtered.columns:
            st.markdown("---")
            st.subheader("Analyse Détaillée")
            
            detailed_table = df_filtered.groupby(['DirectionRegionale', 'Localite']).agg({
                'Montant_Depots': 'sum',
                'Montant_Credits': 'sum',
                'Nombre_Guichets': 'sum'
            }).reset_index()
            
            detailed_table.columns = ['DirectionRegionale', 'Localite', 'Total Dépôts', 'Total Crédits', 'Total Guichets']
            
            total_row = pd.DataFrame([{
                'DirectionRegionale': 'Total',
                'Localite': '',
                'Total Dépôts': detailed_table['Total Dépôts'].sum(),
                'Total Crédits': detailed_table['Total Crédits'].sum(),
                'Total Guichets': detailed_table['Total Guichets'].sum()
            }])
            detailed_table = pd.concat([detailed_table, total_row], ignore_index=True)
            detailed_table['Total Dépôts']  = detailed_table['Total Dépôts'].apply(lambda x: f"{x/1e6:.2f} Md")
            detailed_table['Total Crédits'] = detailed_table['Total Crédits'].apply(lambda x: f"{x/1e6:.2f} Md")
            
            st.dataframe(detailed_table, use_container_width=True, hide_index=True)
    
    except Exception as e:
        st.error(f"Erreur lors de la création des visualisations : {str(e)}")
        st.write("**Colonnes disponibles dans le DataFrame :**")
        st.write(df.columns.tolist())
        st.write("**Aperçu des données :**")
        st.dataframe(df.head())
        st.exception(e)

# ============================================================================
# FONCTIONS POUR VISUALISATIONS SAHAM BANK
# ============================================================================

def normalize_referentiel_columns(df):
    """Normalise les colonnes du référentiel agences"""
    df_normalized = df.copy()
    
    # Nettoyer les noms de colonnes
    df_normalized.columns = df_normalized.columns.str.strip()
    
    # Mapper les variations de noms
    for col in df_normalized.columns:
        col_lower = col.lower()
        
        if 'code' in col_lower and 'agence' in col_lower:
            df_normalized.rename(columns={col: 'Code_Agence'}, inplace=True)
        elif 'code' in col_lower and 'localit' in col_lower:
            df_normalized.rename(columns={col: 'Code_Localite'}, inplace=True)
        elif 'localit' in col_lower and 'code' not in col_lower:
            df_normalized.rename(columns={col: 'Localite'}, inplace=True)
    
    return df_normalized

def normalize_financial_columns(df):
    """Normalise les colonnes des données financières"""
    df_normalized = df.copy()
    
    # Nettoyer les noms de colonnes
    df_normalized.columns = df_normalized.columns.str.strip()
    
    # Mapper les variations de noms
    for col in df_normalized.columns:
        col_lower = col.lower()
        
        if 'p' in col_lower and 'riod' in col_lower:
            df_normalized.rename(columns={col: 'Periode'}, inplace=True)
        elif 'code' in col_lower and 'agence' in col_lower:
            df_normalized.rename(columns={col: 'Code_Agence'}, inplace=True)
        elif 'd' in col_lower and 'p' in col_lower and 't' in col_lower:
            df_normalized.rename(columns={col: 'Depots'}, inplace=True)
        elif 'cr' in col_lower and 'dit' in col_lower:
            df_normalized.rename(columns={col: 'Credits'}, inplace=True)
    
    return df_normalized

def clean_numeric_saham(df, columns):
    """Nettoie les colonnes numériques Saham"""
    df_clean = df.copy()
    
    for col in columns:
        if col in df_clean.columns:
            # Convertir en string
            df_clean[col] = df_clean[col].astype(str)
            # Enlever tous les espaces
            df_clean[col] = df_clean[col].str.replace(r'\s+', '', regex=True)
            # Enlever caractères non-numériques sauf point et virgule
            df_clean[col] = df_clean[col].str.replace(r'[^\d.,]', '', regex=True)
            # Remplacer virgule par point
            df_clean[col] = df_clean[col].str.replace(',', '.')
            # Convertir en numérique
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
            # Remplacer NaN par 0
            df_clean[col] = df_clean[col].fillna(0)
    
    return df_clean

def join_and_aggregate_saham(df_financial, df_referentiel):
    """
    Jointure des données financières avec le référentiel agences
    puis agrégation par localité avec calcul PDM
    """
    # Normaliser les DataFrames
    df_fin = normalize_financial_columns(df_financial.copy())
    df_ref = normalize_referentiel_columns(df_referentiel.copy())
    
    # Nettoyer les colonnes numériques financières
    df_fin = clean_numeric_saham(df_fin, ['Depots', 'Credits'])
    
    # S'assurer que Code_Agence est du même type dans les 2 DataFrames
    df_fin['Code_Agence'] = df_fin['Code_Agence'].astype(str).str.strip()
    df_ref['Code_Agence'] = df_ref['Code_Agence'].astype(str).str.strip()
    
    # ÉTAPE 1 : Jointure
    df_joined = df_fin.merge(
        df_ref[['Code_Agence', 'Localite']], 
        on='Code_Agence', 
        how='left'
    )
    
    # ÉTAPE 2 : Agrégation par Localité et Période
    df_agg = df_joined.groupby(['Periode', 'Localite']).agg({
        'Depots': 'sum',
        'Credits': 'sum'
    }).reset_index()
    
    # ÉTAPE 3 : Calcul PDM (Part De Marché) par Période
    # PDM = (Total Dépôts Localité / Total Global Dépôts) × 100
    
    # Calculer le total global par période
    total_depots_par_periode = df_agg.groupby('Periode')['Depots'].sum().reset_index()
    total_depots_par_periode.columns = ['Periode', 'Total_Global_Depots']
    
    # Joindre avec le DataFrame agrégé
    df_agg = df_agg.merge(total_depots_par_periode, on='Periode')
    
    # Calculer PDM
    df_agg['PDM'] = (df_agg['Depots'] / df_agg['Total_Global_Depots']) * 100
    
    # Supprimer la colonne temporaire
    df_agg = df_agg.drop('Total_Global_Depots', axis=1)
    
    return df_agg

def create_top_visualizations_saham(df):
    """Crée les visualisations Top 25, Top 10, Top 5 pour Saham Bank"""
    
    st.header("📊 Top Localités")
    
    # Filtres en colonnes
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Sélection de la période
        if 'Periode' in df.columns:
            periodes = sorted(df['Periode'].unique())
            periode_selectionnee = st.selectbox(
                "Période",
                options=periodes,
                format_func=lambda x: str(x)
            )
            df_filtered = df[df['Periode'] == periode_selectionnee].copy()
        else:
            df_filtered = df.copy()
    
    with col2:
        # Sélection du critère
        critere = st.selectbox(
            "Critère",
            options=["Dépôts", "Crédits"]
        )
    
    with col3:
        # Sélection du top
        top_choice = st.selectbox(
            "Top",
            options=[25, 10, 5]
        )
    
    st.divider()
    
    # Définir la colonne
    colonne = 'Depots' if critere == "Dépôts" else 'Credits'
    
    # Obtenir le top N
    df_top = df_filtered.nlargest(top_choice, colonne)
    
    # Graphique
    st.subheader(f"Top {top_choice} des Localités par {critere}")
    
    fig = px.bar(
        df_top,
        y='Localite',
        x=colonne,
        orientation='h',
        color=colonne,
        color_continuous_scale='Viridis',
        title=f"Top {top_choice} - {critere}",
        labels={colonne: critere, 'Localite': 'Localité'}
    )
    
    fig.update_layout(
        height=max(400, top_choice * 25),
        yaxis={'categoryorder': 'total ascending'},
        xaxis_title=f"{critere} (Md MAD)",
        yaxis_title='Localité',
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Tableau détaillé
    st.subheader("📋 Détails")
    
    df_display = df_top[['Localite', 'Depots', 'Credits', 'PDM']].copy()
    df_display.columns = ['Localité', 'Dépôts', 'Crédits', 'PDM (%)']
    
    # Ajouter le rang
    df_display.insert(0, 'Rang', range(1, len(df_display) + 1))
    
    # Formater les nombres
    df_display['Dépôts'] = df_display['Dépôts'].apply(lambda x: f"{x:,.0f}".replace(',', ' '))
    df_display['Crédits'] = df_display['Crédits'].apply(lambda x: f"{x:,.0f}".replace(',', ' '))
    df_display['PDM (%)'] = df_display['PDM (%)'].apply(lambda x: f"{x:.2f}%")
    
    st.dataframe(df_display, use_container_width=True, hide_index=True)

def create_pdm_visualizations_saham(df):
    """Visualisations de la Part De Marché pour Saham Bank"""
    
    st.header("📈 Analyse PDM (Part De Marché)")
    
    # Filtrer par période
    if 'Periode' in df.columns:
        periodes = sorted(df['Periode'].unique())
        periode_selectionnee = st.selectbox(
            "Période",
            options=periodes,
            format_func=lambda x: str(x),
            key="pdm_periode"
        )
        
        df_filtered = df[df['Periode'] == periode_selectionnee].copy()
    else:
        df_filtered = df.copy()
    
    st.divider()
    
    # Métriques globales
    col1, col2, col3 = st.columns(3)
    
    total_depots = df_filtered['Depots'].sum()
    total_credits = df_filtered['Credits'].sum()
    nb_localites = len(df_filtered)
    
    with col1:
        st.metric(
            "Total Dépôts", 
            f"{total_depots/1e6:.2f} Md",
            help="Milliards MAD"
        )
    
    with col2:
        st.metric(
            "Total Crédits", 
            f"{total_credits/1e6:.2f} Md",
            help="Milliards MAD"
        )
    
    with col3:
        st.metric(
            "Localités", 
            nb_localites
        )
    
    st.divider()
    
    # Top 10 PDM en camembert
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Top 10 Localités par PDM")
        
        df_top_pdm = df_filtered.nlargest(10, 'PDM')
        
        fig_pdm = px.pie(
            df_top_pdm,
            values='PDM',
            names='Localite',
            title="Distribution de la PDM (Top 10)",
            hole=0.4
        )
        
        fig_pdm.update_traces(
            textposition='inside', 
            textinfo='label+percent',
            hovertemplate='<b>%{label}</b><br>PDM: %{value:.2f}%<extra></extra>'
        )
        
        st.plotly_chart(fig_pdm, use_container_width=True)
    
    with col2:
        st.subheader("Classement PDM")
        
        df_pdm_top = df_filtered.nlargest(10, 'PDM')[['Localite', 'PDM', 'Depots']].copy()
        df_pdm_top.columns = ['Localité', 'PDM (%)', 'Dépôts']
        df_pdm_top.insert(0, 'Rang', range(1, len(df_pdm_top) + 1))
        
        df_pdm_top['PDM (%)'] = df_pdm_top['PDM (%)'].apply(lambda x: f"{x:.2f}%")
        df_pdm_top['Dépôts'] = df_pdm_top['Dépôts'].apply(lambda x: f"{x/1e6:.2f} Md")
        
        st.dataframe(df_pdm_top, use_container_width=True, hide_index=True)
    
    st.divider()
    
    # Tableau PDM complet
    st.subheader("📊 Tableau PDM Complet")
    
    df_pdm_display = df_filtered[['Localite', 'Depots', 'Credits', 'PDM']].copy().sort_values('PDM', ascending=False)
    df_pdm_display.columns = ['Localité', 'Dépôts', 'Crédits', 'PDM (%)']
    
    df_pdm_display.insert(0, 'Rang', range(1, len(df_pdm_display) + 1))
    
    df_pdm_display['Dépôts'] = df_pdm_display['Dépôts'].apply(lambda x: f"{x/1e6:.2f} Md")
    df_pdm_display['Crédits'] = df_pdm_display['Crédits'].apply(lambda x: f"{x/1e6:.2f} Md")
    df_pdm_display['PDM (%)'] = df_pdm_display['PDM (%)'].apply(lambda x: f"{x:.2f}%")
    
    st.dataframe(df_pdm_display, use_container_width=True, hide_index=True, height=400)

def create_dashboard_saham(df_saham, df_bam=None):
    """
    Dashboard Saham Bank COMPLET avec :
    1. Calcul Catégorie : Saham Présent / Absent
    2. Calcul Top : Top 25 localités / Autres  
    3. PDM Saham
    4. Targets Dépôts / Crédits
    5. Evolution (Target - Montant)
    """
    
    st.header("🎯 Dashboard Saham Bank")
    
    st.markdown("""
    **Éléments du Dashboard :**
    - ✅ Calcul Catégorie : Saham Présent / Absent
    - ✅ Calcul Top : Top 25 localités / Autres
    - ✅ PDM Saham
    - ✅ Targets Dépôts / Crédits
    - ✅ Evolution (Target - Montant Dépôts ou crédits Saham)
    """)
    
    # Vérifier données BAM
    if df_bam is not None:
        total_depots_place = df_bam['Montant_Depots'].sum()
        total_credits_place = df_bam['Montant_Credits'].sum()
        villes_bam = set(df_bam['Localite'].unique())
    elif hasattr(st.session_state, 'total_depots_bam') and st.session_state.total_depots_bam is not None:
        total_depots_place = st.session_state.total_depots_bam
        total_credits_place = st.session_state.total_credits_bam
        villes_bam = set()
    else:
        st.warning("⚠️ Données BAM non disponibles. Importez d'abord les données BAM.")
        st.info("Pour utiliser ce dashboard, allez dans 'Import & Traitement' → Onglet 'Import BAM'")
        return
    
    st.divider()
    
    # ==================================================================
    # SAISIE DU TARGET PDM
    # ==================================================================
    
    st.subheader("🎯 Définir le Target PDM")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        target_pdm = st.slider(
            "Target PDM Souhaité (%)",
            min_value=1.0,
            max_value=20.0,
            value=8.0,
            step=0.5,
            help="Pourcentage de part de marché souhaité"
        )
    
    with col2:
        st.metric("Target PDM", f"{target_pdm:.1f}%")
    
    with col3:
        # Option pour afficher en millions
        afficher_millions = True  # Toujours en Milliards (Md)
    
    st.divider()
    
    # ==================================================================
    # FILTRAGE PAR PÉRIODE
    # ==================================================================
    
    if 'Periode' in df_saham.columns:
        periodes = sorted(df_saham['Periode'].unique())
        periode_selectionnee = st.selectbox(
            "📅 Période d'analyse",
            options=periodes,
            format_func=lambda x: str(x)
        )
        df_filtered = df_saham[df_saham['Periode'] == periode_selectionnee].copy()
    else:
        df_filtered = df_saham.copy()
    
    # ==================================================================
    # 1. CALCUL CATÉGORIE : SAHAM PRÉSENT / ABSENT
    # ==================================================================
    
    # Villes Saham Présent
    villes_saham = set(df_filtered['Localite'].unique())
    
    # Villes Saham Absent (dans BAM mais pas dans Saham)
    if len(villes_bam) > 0:
        villes_absentes = villes_bam - villes_saham
        nb_villes_absentes = len(villes_absentes)
    else:
        nb_villes_absentes = 0
        villes_absentes = set()
    
    # Marquer les villes présentes
    df_filtered['Categorie'] = 'Saham Présent'
    
    # ==================================================================
    # 2. CALCUL TOP : TOP 25 / AUTRES
    # ==================================================================
    
    # Trier par dépôts et prendre le Top 25
    df_sorted = df_filtered.sort_values('Depots', ascending=False)
    top_25_villes = df_sorted.head(25)['Localite'].tolist()
    
    df_filtered['Top'] = df_filtered['Localite'].apply(
        lambda x: 'Top 25' if x in top_25_villes else 'Autres'
    )
    
    # ==================================================================
    # 3. PDM SAHAM (TRANCHES)
    # ==================================================================
    
    def get_tranche_pdm(pdm):
        if pdm >= 10:
            return 'Sup >10%'
        elif pdm >= 7:
            return 'Sup 7-10%'
        elif pdm >= 5:
            return 'Inf 5-7%'
        else:
            return 'Inf <5%'
    
    df_filtered['Tranche_PDM'] = df_filtered['PDM'].apply(get_tranche_pdm)
    
    # ==================================================================
    # 4. TARGETS DÉPÔTS / CRÉDITS
    # ==================================================================
    
    # Target basé sur le total marché BAM
    target_depots_global = total_depots_place * (target_pdm / 100)
    target_credits_global = total_credits_place * (target_pdm / 100)
    
    # Pour chaque ville : Target proportionnel au poids dans le marché
    # Simplification : même target PDM pour toutes les villes
    df_filtered['Target_Depots'] = total_depots_place * (target_pdm / 100) / len(df_filtered)
    df_filtered['Target_Credits'] = total_credits_place * (target_pdm / 100) / len(df_filtered)
    
    # ==================================================================
    # 5. EVOLUTION (TARGET - MONTANT)
    # ==================================================================
    
    df_filtered['Evolution_Depots'] = df_filtered['Target_Depots'] - df_filtered['Depots']
    df_filtered['Evolution_Credits'] = df_filtered['Target_Credits'] - df_filtered['Credits']
    
    # ==================================================================
    # MÉTRIQUES GLOBALES
    # ==================================================================
    
    st.subheader("📊 Vue d'Ensemble")
    
    total_depots_saham = df_filtered['Depots'].sum()
    total_credits_saham = df_filtered['Credits'].sum()
    pdm_actuelle_depots = (total_depots_saham / total_depots_place) * 100
    pdm_actuelle_credits = (total_credits_saham / total_credits_place) * 100
    
    # Facteur d'affichage
    facteur = 1e6  # milliers DH ÷ 1 000 000 = Md
    unite = "Md"
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Dépôts Saham",
            f"{total_depots_saham/facteur:,.2f} {unite}",
            help="Total des dépôts Saham Bank"
        )
    
    with col2:
        st.metric(
            "Dépôts Place (BAM)",
            f"{total_depots_place/facteur:,.2f} {unite}",
            help="Total du marché"
        )
    
    with col3:
        st.metric(
            "PDM Actuelle",
            f"{pdm_actuelle_depots:.2f}%",
            delta=f"{target_pdm - pdm_actuelle_depots:.2f}%",
            help="Part de marché actuelle vs target"
        )
    
    with col4:
        gap_global = target_depots_global - total_depots_saham
        st.metric(
            "Gap Global",
            f"{gap_global/facteur:,.2f} {unite}",
            delta_color="inverse",
            help="Montant à combler pour atteindre le target"
        )
    
    st.divider()
    
    # ==================================================================
    
    # ==================================================================
    # DASHBOARD STRUCTURÉ - 5 SECTIONS
    # ==================================================================
    
    st.divider()
    st.title("📊 Dashboard Détaillé")
    
    # Appeler la fonction de dashboard structuré
    create_dashboard_structure_saham(
        df_filtered,
        st.session_state.combined_data_bam if st.session_state.combined_data_bam is not None else None,
        total_depots_place,
        total_credits_place,
        target_pdm,
        afficher_millions
    )
    
    st.divider()
    
    # TABLEAU RÉCAPITULATIF - COMME DANS L'IMAGE
    # ==================================================================
    
    st.subheader("📋 Tableau Récapitulatif")
    
    # Toggle pour choisir entre vue normale et interactive
    col_toggle1, col_toggle2 = st.columns([3, 1])
    
    with col_toggle2:
        mode_interactif = st.checkbox(
            "🔍 Mode Interactif", 
            value=False,
            help="Activez pour voir les détails de calcul de chaque ligne en cliquant dessus"
        )
    
    if mode_interactif:
        # AFFICHER VERSION INTERACTIVE
        tableau_recapitulatif_interactif(
            df_filtered, 
            total_depots_place, 
            total_credits_place, 
            target_pdm, 
            afficher_millions,
            nb_villes_absentes
        )
    else:
        # AFFICHER VERSION NORMALE (tableau statique)
    
        # Créer les lignes du tableau
        tableau_data = []
    
        # TOP 25 avec tranches PDM
        for tranche in ['Sup >10%', 'Sup 7-10%', 'Inf 5-7%', 'Inf <5%']:
            df_ligne = df_filtered[
                (df_filtered['Top'] == 'Top 25') & 
                (df_filtered['Tranche_PDM'] == tranche)
            ]
        
            if len(df_ligne) > 0:
                tableau_data.append({
                    'Catégorie': 'Saham Présent',
                    'Top': 'Top 25',
                    'PDM Saham': tranche,
                    'Nombre de VILLE': len(df_ligne),
                    'Somme DEPOTS SAHAM BANK': df_ligne['Depots'].sum(),
                    'Somme DEPOTS PLACE': total_depots_place,
                    'Somme PDM': (df_ligne['Depots'].sum() / total_depots_place) * 100,
                    'Somme Depots Target': df_ligne['Target_Depots'].sum(),
                    'Evolution': df_ligne['Evolution_Depots'].sum()
                })
    
        # Total Top 25
        df_top25 = df_filtered[df_filtered['Top'] == 'Top 25']
        if len(df_top25) > 0:
            tableau_data.append({
                'Catégorie': 'Total Top 25',
                'Top': '',
                'PDM Saham': 'Autres',
                'Nombre de VILLE': len(df_top25),
                'Somme DEPOTS SAHAM BANK': df_top25['Depots'].sum(),
                'Somme DEPOTS PLACE': total_depots_place,
                'Somme PDM': (df_top25['Depots'].sum() / total_depots_place) * 100,
                'Somme Depots Target': df_top25['Target_Depots'].sum(),
                'Evolution': df_top25['Evolution_Depots'].sum()
            })
    
        # Total Saham Présent (Autres)
        df_autres = df_filtered[df_filtered['Top'] == 'Autres']
        if len(df_autres) > 0:
            tableau_data.append({
                'Catégorie': 'Total Saham Présent',
                'Top': '',
                'PDM Saham': 'Autres',
                'Nombre de VILLE': len(df_filtered),
                'Somme DEPOTS SAHAM BANK': df_filtered['Depots'].sum(),
                'Somme DEPOTS PLACE': total_depots_place,
                'Somme PDM': (df_filtered['Depots'].sum() / total_depots_place) * 100,
                'Somme Depots Target': df_filtered['Target_Depots'].sum(),
                'Evolution': df_filtered['Evolution_Depots'].sum()
            })
    
        # Saham Absent
        if nb_villes_absentes > 0:
            tableau_data.append({
                'Catégorie': 'Total Saham Absent',
                'Top': '',
                'PDM Saham': 'Autres',
                'Nombre de VILLE': nb_villes_absentes,
                'Somme DEPOTS SAHAM BANK': 0,
                'Somme DEPOTS PLACE': total_depots_place,
                'Somme PDM': 0.0,
                'Somme Depots Target': 0,
                'Evolution': 0
            })
    
        # Total Général
        tableau_data.append({
            'Catégorie': 'Total général',
            'Top': '',
            'PDM Saham': '',
            'Nombre de VILLE': len(df_filtered) + nb_villes_absentes,
            'Somme DEPOTS SAHAM BANK': df_filtered['Depots'].sum(),
            'Somme DEPOTS PLACE': total_depots_place,
            'Somme PDM': (df_filtered['Depots'].sum() / total_depots_place) * 100,
            'Somme Depots Target': target_depots_global,
            'Evolution': target_depots_global - df_filtered['Depots'].sum()
        })
    
        # Créer le DataFrame
        df_tableau = pd.DataFrame(tableau_data)
    
        # Formater pour affichage
        df_display = df_tableau.copy()
    
        df_display['Somme DEPOTS SAHAM BANK'] = df_display['Somme DEPOTS SAHAM BANK'].apply(
            lambda x: f"{x/facteur:,.2f}" if afficher_millions else f"{x:,.0f}"
        )
        df_display['Somme DEPOTS PLACE'] = df_display['Somme DEPOTS PLACE'].apply(
            lambda x: f"{x/facteur:,.2f}" if afficher_millions else f"{x:,.0f}"
        )
        df_display['Somme PDM'] = df_display['Somme PDM'].apply(lambda x: f"{x:.1f}%")
        df_display['Somme Depots Target'] = df_display['Somme Depots Target'].apply(
            lambda x: f"{x/facteur:,.2f}" if afficher_millions else f"{x:,.0f}"
        )
        df_display['Evolution'] = df_display['Evolution'].apply(
            lambda x: f"{x/facteur:,.2f}" if afficher_millions else f"{x:,.0f}"
        )
    
        # Afficher le tableau
    st.dataframe(df_display, use_container_width=True, hide_index=True)
    
    # ==================================================================
    # RÉSULTATS ATTENDUS
    # ==================================================================
    
    st.divider()
    st.subheader("✅ Résultats avec vos Données")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📊 Statistiques :**")
        st.write(f"- Villes Saham Présent : **{len(df_filtered)}**")
        st.write(f"- Villes Saham Absent : **{nb_villes_absentes}**")
        st.write(f"- Total Général : **{len(df_filtered) + nb_villes_absentes}**")
        st.write(f"- Villes Top 25 : **{len(df_top25)}**")
    
    with col2:
        st.markdown("**💰 Montants :**")
        st.write(f"- Total Dépôts Saham : **{total_depots_saham/facteur:,.2f} {unite}**")
        st.write(f"- Total Dépôts Place : **{total_depots_place/facteur:,.2f} {unite}**")
        st.write(f"- PDM Actuelle : **{pdm_actuelle_depots:.2f}%**")
        st.write(f"- Target PDM : **{target_pdm:.1f}%**")
    
    # ==================================================================
    # DÉTAILS PAR VILLE
    # ==================================================================
    
    st.divider()
    st.subheader("🏙️ Détails par Ville")
    
    # Préparer l'affichage
    df_detail = df_filtered[[
        'Localite', 'Top', 'Tranche_PDM', 'Depots', 'Credits',
        'PDM', 'Target_Depots', 'Evolution_Depots'
    ]].copy()
    
    df_detail = df_detail.sort_values('Depots', ascending=False)
    
    df_detail.columns = [
        'Ville', 'Catégorie', 'Tranche PDM', 'Dépôts', 'Crédits',
        'PDM (%)', 'Target Dépôts', 'Evolution'
    ]
    
    # Formater
    df_detail['Dépôts'] = df_detail['Dépôts'].apply(
        lambda x: f"{x/facteur:,.2f}" if afficher_millions else f"{x:,.0f}"
    )
    df_detail['Crédits'] = df_detail['Crédits'].apply(
        lambda x: f"{x/facteur:,.2f}" if afficher_millions else f"{x:,.0f}"
    )
    df_detail['PDM (%)'] = df_detail['PDM (%)'].apply(lambda x: f"{x:.2f}%")
    df_detail['Target Dépôts'] = df_detail['Target Dépôts'].apply(
        lambda x: f"{x/facteur:,.2f}" if afficher_millions else f"{x:,.0f}"
    )
    df_detail['Evolution'] = df_detail['Evolution'].apply(
        lambda x: f"{x/facteur:,.2f}" if afficher_millions else f"{x:,.0f}"
    )
    
    st.dataframe(df_detail, use_container_width=True, hide_index=True, height=400)

    
    # ==================================================================
    # VERSION INTERACTIVE - DÉTAILS PAR VILLE
    # ==================================================================
    
    st.divider()
    
    # Reconstruire df_joined pour avoir les détails par agence
    if st.session_state.saham_financial is not None and st.session_state.saham_referentiel is not None:
        
        # Normaliser et joindre
        df_fin_temp = normalize_financial_columns(st.session_state.saham_financial.copy())
        df_ref_temp = normalize_referentiel_columns(st.session_state.saham_referentiel.copy())
        
        df_fin_temp = clean_numeric_saham(df_fin_temp, ['Depots', 'Credits'])
        df_fin_temp['Code_Agence'] = df_fin_temp['Code_Agence'].astype(str).str.strip()
        df_ref_temp['Code_Agence'] = df_ref_temp['Code_Agence'].astype(str).str.strip()
        
        df_joined_details = df_fin_temp.merge(
            df_ref_temp[['Code_Agence', 'Localite']], 
            on='Code_Agence', 
            how='left'
        )
        
        # Filtrer par période si nécessaire
        if 'Periode' in df_joined_details.columns and 'Periode' in df_filtered.columns:
            periode = df_filtered['Periode'].iloc[0]
            df_joined_details = df_joined_details[df_joined_details['Periode'] == periode]
        
        # Appeler la fonction de détails interactifs
        afficher_details_ville_interactive(
            df_filtered, 
            df_joined_details, 
            total_depots_place, 
            total_credits_place, 
            target_pdm, 
            afficher_millions
        )
    else:
        st.warning("Données détaillées non disponibles. Importez les fichiers Saham Bank pour voir les détails par agence.")

    
    # ==================================================================
    # GRAPHIQUES
    # ==================================================================
    
    st.divider()
    st.subheader("📊 Visualisations")
    
    tab1, tab2 = st.tabs(["Répartition par Catégorie", "Top 10 Villes"])
    
    with tab1:
        # Pie chart des catégories
        fig_pie = go.Figure(data=[go.Pie(
            labels=['Top 25', 'Autres', 'Saham Absent'],
            values=[
                len(df_top25),
                len(df_autres),
                nb_villes_absentes
            ],
            hole=0.4
        )])
        
        fig_pie.update_layout(
            title="Répartition des Villes par Catégorie",
            height=400
        )
        
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with tab2:
        # Top 10 villes
        df_top10 = df_filtered.nlargest(10, 'Depots')
        
        fig_bar = px.bar(
            df_top10,
            x='Depots',
            y='Localite',
            orientation='h',
            title="Top 10 Villes par Dépôts",
            labels={'Depots': f'Dépôts ({unite})', 'Localite': 'Ville'}
        )
        
        fig_bar.update_layout(height=500, yaxis={'categoryorder':'total ascending'})
        
        st.plotly_chart(fig_bar, use_container_width=True)

def create_dashboard_structure_saham(df_saham, df_bam, total_depots_bam, total_credits_bam, target_pdm, afficher_millions=True):
    """
    Dashboard structuré avec les 5 sections distinctes :
    1. Calcul Catégorie (Saham Présent / Absent)
    2. Calcul Top (Top 25 / Autres)
    3. PDM Saham
    4. Targets Dépôts / Crédits
    5. Evolution
    """
    
    facteur = 1e6  # milliers DH ÷ 1 000 000 = Md
    unite = "Md"
    
    # Villes BAM
    if df_bam is not None:
        villes_bam = set(df_bam['Localite'].unique())
    else:
        villes_bam = set()
    
    # Villes Saham
    villes_saham = set(df_saham['Localite'].unique())
    villes_absentes = villes_bam - villes_saham if villes_bam else set()
    
    # Top 25
    df_sorted = df_saham.sort_values('Depots', ascending=False)
    top_25_villes = df_sorted.head(25)['Localite'].tolist()
    
    df_saham['Top'] = df_saham['Localite'].apply(
        lambda x: 'Top 25' if x in top_25_villes else 'Autres'
    )
    
    # ==================================================================
    # SECTION 1 : CALCUL CATÉGORIE - SAHAM PRÉSENT / ABSENT
    # ==================================================================
    
    st.header("1️⃣ Calcul Catégorie : Saham Présent / Absent")
    
    col1, col2, col3 = st.columns(3)
    
    # Saham Présent
    nb_saham_present = len(villes_saham)
    depots_saham_present = df_saham['Depots'].sum()
    credits_saham_present = df_saham['Credits'].sum()
    pdm_saham_present = (depots_saham_present / total_depots_bam) * 100 if total_depots_bam > 0 else 0
    
    with col1:
        st.markdown("### ✅ Saham Présent")
        st.metric("Nombre de villes", nb_saham_present)
        st.metric("Dépôts", f"{depots_saham_present/facteur:,.2f} {unite}")
        st.metric("Crédits", f"{credits_saham_present/facteur:,.2f} {unite}")
        st.metric("PDM", f"{pdm_saham_present:.2f}%")
        
        with st.expander("🔍 Voir le calcul"):
            st.code(f"""
Comptage des villes dans Saham :
Nombre = {nb_saham_present}

Total Dépôts :
Somme = {depots_saham_present:,.0f}

PDM = (Dépôts / Total Marché) × 100
PDM = ({depots_saham_present:,.0f} / {total_depots_bam:,.0f}) × 100
PDM = {pdm_saham_present:.2f}%
            """)
    
    # Saham Absent
    nb_saham_absent = len(villes_absentes)
    
    with col2:
        st.markdown("### ❌ Saham Absent")
        st.metric("Nombre de villes", nb_saham_absent)
        st.metric("Dépôts", "0")
        st.metric("Crédits", "0")
        st.metric("PDM", "0%")
        
        if nb_saham_absent > 0:
            with st.expander("📋 Liste des villes absentes"):
                for ville in sorted(villes_absentes):
                    st.write(f"- {ville}")
    
    # Total
    nb_total = nb_saham_present + nb_saham_absent
    
    with col3:
        st.markdown("### 📊 Total Général")
        st.metric("Total villes", nb_total)
        st.metric("Saham Présent", f"{nb_saham_present} ({nb_saham_present/nb_total*100:.1f}%)" if nb_total > 0 else "0")
        st.metric("Saham Absent", f"{nb_saham_absent} ({nb_saham_absent/nb_total*100:.1f}%)" if nb_total > 0 else "0")
    
    st.divider()
    
    # ==================================================================
    # SECTION 2 : CALCUL TOP - TOP 25 / AUTRES
    # ==================================================================
    
    st.header("2️⃣ Calcul Top : Top 25 localités / Autres")
    
    col1, col2, col3 = st.columns(3)
    
    # Top 25
    df_top25 = df_saham[df_saham['Top'] == 'Top 25']
    depots_top25 = df_top25['Depots'].sum()
    credits_top25 = df_top25['Credits'].sum()
    pdm_top25 = (depots_top25 / total_depots_bam) * 100 if total_depots_bam > 0 else 0
    
    with col1:
        st.markdown("### 🏆 Top 25")
        st.metric("Nombre de villes", len(df_top25))
        st.metric("Dépôts", f"{depots_top25/facteur:,.2f} {unite}")
        st.metric("Crédits", f"{credits_top25/facteur:,.2f} {unite}")
        st.metric("PDM", f"{pdm_top25:.2f}%")
        st.metric("% du Total Saham", f"{(depots_top25/depots_saham_present)*100:.1f}%")
        
        with st.expander("🔍 Voir le calcul"):
            st.code(f"""
Top 25 = Les 25 villes avec le plus de dépôts

Tri par dépôts décroissant
Sélection des 25 premières

Dépôts Top 25 = {depots_top25:,.0f}
Dépôts Total Saham = {depots_saham_present:,.0f}

% du Total = ({depots_top25:,.0f} / {depots_saham_present:,.0f}) × 100
% du Total = {(depots_top25/depots_saham_present)*100:.2f}%
            """)
    
    # Autres
    df_autres = df_saham[df_saham['Top'] == 'Autres']
    depots_autres = df_autres['Depots'].sum()
    credits_autres = df_autres['Credits'].sum()
    pdm_autres = (depots_autres / total_depots_bam) * 100 if total_depots_bam > 0 else 0
    
    with col2:
        st.markdown("### 📍 Autres")
        st.metric("Nombre de villes", len(df_autres))
        st.metric("Dépôts", f"{depots_autres/facteur:,.2f} {unite}")
        st.metric("Crédits", f"{credits_autres/facteur:,.2f} {unite}")
        st.metric("PDM", f"{pdm_autres:.2f}%")
        st.metric("% du Total Saham", f"{(depots_autres/depots_saham_present)*100:.1f}%")
    
    # Comparaison
    with col3:
        st.markdown("### ⚖️ Comparaison")
        st.metric("Concentration Top 25", f"{(depots_top25/depots_saham_present)*100:.1f}%")
        st.metric("Reste (Autres)", f"{(depots_autres/depots_saham_present)*100:.1f}%")
        
        # Graphique de répartition
        fig_repartition = go.Figure(data=[go.Pie(
            labels=['Top 25', 'Autres'],
            values=[depots_top25, depots_autres],
            hole=0.4
        )])
        fig_repartition.update_layout(height=250, margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig_repartition, use_container_width=True)
    
    st.divider()
    
    # ==================================================================
    # SECTION 3 : PDM SAHAM
    # ==================================================================
    
    st.header("3️⃣ PDM Saham")
    
    st.markdown("### Part De Marché par Tranche")
    
    # Définir les tranches
    def get_tranche_pdm(pdm):
        if pdm >= 10:
            return 'Sup >10%'
        elif pdm >= 7:
            return 'Sup 7-10%'
        elif pdm >= 5:
            return 'Inf 5-7%'
        else:
            return 'Inf <5%'
    
    df_saham['Tranche_PDM'] = df_saham['PDM'].apply(get_tranche_pdm)
    
    # Calculer par tranche
    tranches_data = []
    for tranche in ['Sup >10%', 'Sup 7-10%', 'Inf 5-7%', 'Inf <5%']:
        df_tranche = df_saham[df_saham['Tranche_PDM'] == tranche]
        if len(df_tranche) > 0:
            tranches_data.append({
                'Tranche': tranche,
                'Nb Villes': len(df_tranche),
                'Dépôts': df_tranche['Depots'].sum(),
                'Crédits': df_tranche['Credits'].sum(),
                'PDM Moyenne': df_tranche['PDM'].mean()
            })
    
    # Afficher en colonnes
    cols = st.columns(len(tranches_data))
    
    for idx, tranche_info in enumerate(tranches_data):
        with cols[idx]:
            st.markdown(f"### {tranche_info['Tranche']}")
            st.metric("Villes", tranche_info['Nb Villes'])
            st.metric("Dépôts", f"{tranche_info['Dépôts']/facteur:,.2f} {unite}")
            st.metric("PDM Moy.", f"{tranche_info['PDM Moyenne']:.2f}%")
            
            with st.expander("📋 Villes"):
                villes_tranche = df_saham[df_saham['Tranche_PDM'] == tranche_info['Tranche']]['Localite'].tolist()
                for ville in sorted(villes_tranche):
                    st.write(f"- {ville}")
    
    st.divider()
    
    # ==================================================================
    # SECTION 4 : TARGETS DÉPÔTS / CRÉDITS
    # ==================================================================
    
    st.header("4️⃣ Targets Dépôts / Crédits")
    
    st.markdown(f"### Target PDM Défini : **{target_pdm:.1f}%**")
    
    # Calculer les targets
    target_depots_global = total_depots_bam * (target_pdm / 100)
    target_credits_global = total_credits_bam * (target_pdm / 100)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🎯 Target Dépôts")
        st.metric("Target Global", f"{target_depots_global/facteur:,.2f} {unite}")
        st.metric("Réalisé", f"{depots_saham_present/facteur:,.2f} {unite}")
        st.metric("Taux Réalisation", f"{(depots_saham_present/target_depots_global)*100:.1f}%")
        
        with st.expander("🔍 Calcul du Target"):
            st.code(f"""
Target Dépôts = Total Marché × Target PDM

Target = {total_depots_bam:,.0f} × {target_pdm}%

Target = {target_depots_global:,.0f}

Réalisé = {depots_saham_present:,.0f}

Taux = (Réalisé / Target) × 100
Taux = ({depots_saham_present:,.0f} / {target_depots_global:,.0f}) × 100
Taux = {(depots_saham_present/target_depots_global)*100:.2f}%
            """)
    
    with col2:
        st.markdown("### 🎯 Target Crédits")
        st.metric("Target Global", f"{target_credits_global/facteur:,.2f} {unite}")
        st.metric("Réalisé", f"{credits_saham_present/facteur:,.2f} {unite}")
        st.metric("Taux Réalisation", f"{(credits_saham_present/target_credits_global)*100:.1f}%")
        
        with st.expander("🔍 Calcul du Target"):
            st.code(f"""
Target Crédits = Total Marché × Target PDM

Target = {total_credits_bam:,.0f} × {target_pdm}%

Target = {target_credits_global:,.0f}

Réalisé = {credits_saham_present:,.0f}

Taux = (Réalisé / Target) × 100
Taux = {(credits_saham_present/target_credits_global)*100:.2f}%
            """)
    
    with col3:
        st.markdown("### 📊 Visualisation")
        
        # Graphique Target vs Réalisé
        fig_target = go.Figure()
        
        fig_target.add_trace(go.Bar(
            name='Target',
            x=['Dépôts', 'Crédits'],
            y=[target_depots_global, target_credits_global],
            marker_color='orange'
        ))
        
        fig_target.add_trace(go.Bar(
            name='Réalisé',
            x=['Dépôts', 'Crédits'],
            y=[depots_saham_present, credits_saham_present],
            marker_color='lightblue'
        ))
        
        fig_target.update_layout(
            barmode='group',
            height=300,
            margin=dict(t=20, b=20, l=20, r=20),
            yaxis_title=f"Montant ({unite})"
        )
        
        st.plotly_chart(fig_target, use_container_width=True)
    
    st.divider()
    
    # ==================================================================
    # SECTION 5 : EVOLUTION (TARGET - MONTANT)
    # ==================================================================
    
    st.header("5️⃣ Evolution (Target - Montant Dépôts ou Crédits Saham)")
    
    # Calculer les évolutions
    evolution_depots = target_depots_global - depots_saham_present
    evolution_credits = target_credits_global - credits_saham_present
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📉 Évolution Dépôts")
        
        if evolution_depots > 0:
            st.error(f"**Gap à combler : +{evolution_depots/facteur:,.2f} {unite}**")
            st.write(f"Il vous manque **{evolution_depots/facteur:,.2f} {unite}** pour atteindre le target.")
        else:
            st.success(f"**Target dépassé : {abs(evolution_depots)/facteur:,.2f} {unite}**")
            st.write(f"Vous avez dépassé le target de **{abs(evolution_depots)/facteur:,.2f} {unite}**.")
        
        st.metric("Target", f"{target_depots_global/facteur:,.2f} {unite}")
        st.metric("Réalisé", f"{depots_saham_present/facteur:,.2f} {unite}")
        st.metric("Écart", f"{evolution_depots/facteur:,.2f} {unite}", 
                 delta_color="inverse" if evolution_depots > 0 else "normal")
        
        with st.expander("🔍 Calcul de l'Évolution"):
            st.code(f"""
Évolution = Target - Réalisé

Évolution = {target_depots_global:,.0f} - {depots_saham_present:,.0f}

Évolution = {evolution_depots:,.0f}

Statut : {"À COMBLER" if evolution_depots > 0 else "TARGET DÉPASSÉ ✅"}
            """)
    
    with col2:
        st.markdown("### 📉 Évolution Crédits")
        
        if evolution_credits > 0:
            st.error(f"**Gap à combler : +{evolution_credits/facteur:,.2f} {unite}**")
            st.write(f"Il vous manque **{evolution_credits/facteur:,.2f} {unite}** pour atteindre le target.")
        else:
            st.success(f"**Target dépassé : {abs(evolution_credits)/facteur:,.2f} {unite}**")
            st.write(f"Vous avez dépassé le target de **{abs(evolution_credits)/facteur:,.2f} {unite}**.")
        
        st.metric("Target", f"{target_credits_global/facteur:,.2f} {unite}")
        st.metric("Réalisé", f"{credits_saham_present/facteur:,.2f} {unite}")
        st.metric("Écart", f"{evolution_credits/facteur:,.2f} {unite}",
                 delta_color="inverse" if evolution_credits > 0 else "normal")
        
        with st.expander("🔍 Calcul de l'Évolution"):
            st.code(f"""
Évolution = Target - Réalisé

Évolution = {target_credits_global:,.0f} - {credits_saham_present:,.0f}

Évolution = {evolution_credits:,.0f}

Statut : {"À COMBLER" if evolution_credits > 0 else "TARGET DÉPASSÉ ✅"}
            """)
    
    # Graphique d'évolution
    st.markdown("### 📊 Visualisation des Gaps")
    
    fig_evolution = go.Figure()
    
    fig_evolution.add_trace(go.Bar(
        name='Gap Dépôts',
        x=['Dépôts'],
        y=[evolution_depots],
        marker_color='red' if evolution_depots > 0 else 'green'
    ))
    
    fig_evolution.add_trace(go.Bar(
        name='Gap Crédits',
        x=['Crédits'],
        y=[evolution_credits],
        marker_color='red' if evolution_credits > 0 else 'green'
    ))
    
    fig_evolution.update_layout(
        height=400,
        yaxis_title=f"Gap ({unite})",
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_evolution, use_container_width=True)


def tableau_recapitulatif_interactif(df_filtered, total_depots_place, total_credits_place, target_pdm, afficher_millions=True, nb_villes_absentes=0):
    """
    Tableau récapitulatif INTERACTIF avec détails de calcul cliquables
    """
    
    st.subheader("📋 Tableau Récapitulatif - Interactif")
    
    st.info("👆 Cliquez sur une ligne pour voir le DÉTAIL des calculs de cette catégorie")
    
    facteur = 1e6  # milliers DH ÷ 1 000 000 = Md
    unite = "Md"
    
    # Trier et prendre Top 25
    df_sorted = df_filtered.sort_values('Depots', ascending=False)
    top_25_villes = df_sorted.head(25)['Localite'].tolist()
    
    df_filtered['Top'] = df_filtered['Localite'].apply(
        lambda x: 'Top 25' if x in top_25_villes else 'Autres'
    )
    
    # Fonction pour tranche PDM
    def get_tranche_pdm(pdm):
        if pdm >= 10:
            return 'Sup >10%'
        elif pdm >= 7:
            return 'Sup 7-10%'
        elif pdm >= 5:
            return 'Inf 5-7%'
        else:
            return 'Inf <5%'
    
    df_filtered['Tranche_PDM'] = df_filtered['PDM'].apply(get_tranche_pdm)
    
    # ==================================================================
    # CRÉER LES CATÉGORIES INTERACTIVES
    # ==================================================================
    
    categories = []
    
    # TOP 25 avec tranches PDM
    for tranche in ['Sup >10%', 'Sup 7-10%', 'Inf 5-7%', 'Inf <5%']:
        df_ligne = df_filtered[
            (df_filtered['Top'] == 'Top 25') & 
            (df_filtered['Tranche_PDM'] == tranche)
        ]
        
        if len(df_ligne) > 0:
            depots_total = df_ligne['Depots'].sum()
            credits_total = df_ligne['Credits'].sum()
            pdm_total = (depots_total / total_depots_place) * 100
            target_total = total_depots_place * (target_pdm / 100) * (len(df_ligne) / len(df_filtered))
            evolution = target_total - depots_total
            
            categories.append({
                'label': f"Saham Présent | Top 25 | {tranche}",
                'categorie': 'Saham Présent',
                'top': 'Top 25',
                'tranche': tranche,
                'nb_villes': len(df_ligne),
                'depots': depots_total,
                'credits': credits_total,
                'depots_place': total_depots_place,
                'pdm': pdm_total,
                'target': target_total,
                'evolution': evolution,
                'villes': df_ligne['Localite'].tolist()
            })
    
    # Total Top 25
    df_top25 = df_filtered[df_filtered['Top'] == 'Top 25']
    if len(df_top25) > 0:
        depots_total = df_top25['Depots'].sum()
        credits_total = df_top25['Credits'].sum()
        pdm_total = (depots_total / total_depots_place) * 100
        target_total = total_depots_place * (target_pdm / 100) * (len(df_top25) / len(df_filtered))
        evolution = target_total - depots_total
        
        categories.append({
            'label': "Total Top 25",
            'categorie': 'Total Top 25',
            'top': '',
            'tranche': 'Autres',
            'nb_villes': len(df_top25),
            'depots': depots_total,
            'credits': credits_total,
            'depots_place': total_depots_place,
            'pdm': pdm_total,
            'target': target_total,
            'evolution': evolution,
            'villes': df_top25['Localite'].tolist()
        })
    
    # Total Saham Présent
    depots_total = df_filtered['Depots'].sum()
    credits_total = df_filtered['Credits'].sum()
    pdm_total = (depots_total / total_depots_place) * 100
    target_total = total_depots_place * (target_pdm / 100)
    evolution = target_total - depots_total
    
    categories.append({
        'label': "Total Saham Présent",
        'categorie': 'Total Saham Présent',
        'top': '',
        'tranche': 'Autres',
        'nb_villes': len(df_filtered),
        'depots': depots_total,
        'credits': credits_total,
        'depots_place': total_depots_place,
        'pdm': pdm_total,
        'target': target_total,
        'evolution': evolution,
        'villes': df_filtered['Localite'].tolist()
    })
    
    # Saham Absent
    if nb_villes_absentes > 0:
        categories.append({
            'label': "Total Saham Absent",
            'categorie': 'Total Saham Absent',
            'top': '',
            'tranche': 'Autres',
            'nb_villes': nb_villes_absentes,
            'depots': 0,
            'credits': 0,
            'depots_place': total_depots_place,
            'pdm': 0.0,
            'target': 0,
            'evolution': 0,
            'villes': []
        })
    
    # Total Général
    categories.append({
        'label': "Total Général",
        'categorie': 'Total Général',
        'top': '',
        'tranche': '',
        'nb_villes': len(df_filtered) + nb_villes_absentes,
        'depots': df_filtered['Depots'].sum(),
        'credits': df_filtered['Credits'].sum(),
        'depots_place': total_depots_place,
        'pdm': (df_filtered['Depots'].sum() / total_depots_place) * 100,
        'target': target_total,
        'evolution': evolution,
        'villes': df_filtered['Localite'].tolist()
    })
    
    # ==================================================================
    # AFFICHER CHAQUE CATÉGORIE COMME EXPANDER CLIQUABLE
    # ==================================================================
    
    for cat in categories:
        
        # Titre de l'expander avec résumé
        titre = f"📊 {cat['label']} — {cat['nb_villes']} villes | Dépôts: {cat['depots']/facteur:,.2f} {unite} | PDM: {cat['pdm']:.2f}%"
        
        with st.expander(titre):
            
            st.markdown(f"### {cat['label']}")
            
            # ==================================================================
            # DÉTAILS DE CALCUL - 5 COLONNES
            # ==================================================================
            
            col1, col2, col3, col4, col5 = st.columns(5)
            
            # COLONNE 1 : NOMBRE DE VILLES
            with col1:
                st.markdown("#### 🏙️ Villes")
                st.metric("Nombre", cat['nb_villes'])
                
                st.markdown("**Calcul :**")
                st.code(f"""
Comptage des villes dans 
cette catégorie

Résultat = {cat['nb_villes']}
                """)
                
                if len(cat['villes']) > 0 and cat['nb_villes'] <= 10:
                    st.markdown("**Liste :**")
                    for ville in cat['villes']:
                        st.write(f"- {ville}")
            
            # COLONNE 2 : DÉPÔTS SAHAM
            with col2:
                st.markdown("#### 💰 Dépôts Saham")
                st.metric("Total", f"{cat['depots']/facteur:,.2f} {unite}")
                
                st.markdown("**Calcul :**")
                st.code(f"""
Somme des dépôts de toutes 
les villes de cette catégorie

Nb villes = {cat['nb_villes']}

Total = {cat['depots']:,.0f}
                """)
            
            # COLONNE 3 : PDM
            with col3:
                st.markdown("#### 📊 PDM (%)")
                st.metric("PDM", f"{cat['pdm']:.2f}%")
                
                st.markdown("**Calcul :**")
                st.code(f"""
PDM = (Dépôts Catégorie / 
       Total Marché) × 100

PDM = ({cat['depots']:,.0f} / 
       {cat['depots_place']:,.0f}) 
       × 100

PDM = {cat['pdm']:.4f}%
                """)
            
            # COLONNE 4 : TARGET DÉPÔTS
            with col4:
                st.markdown("#### 🎯 Target")
                st.metric("Target", f"{cat['target']/facteur:,.2f} {unite}")
                
                st.markdown("**Calcul :**")
                st.code(f"""
Target = Total Marché × 
         Target PDM × 
         (Villes catégorie / 
          Total villes)

Target = {total_depots_place:,.0f} 
         × {target_pdm}% × 
         ({cat['nb_villes']} / 
          {len(df_filtered)})

Target = {cat['target']:,.0f}
                """)
            
            # COLONNE 5 : ÉVOLUTION
            with col5:
                st.markdown("#### 📈 Évolution")
                
                if cat['evolution'] > 0:
                    st.metric("Gap", f"+{cat['evolution']/facteur:,.2f} {unite}", delta_color="inverse")
                    statut = "À COMBLER"
                else:
                    st.metric("Dépassement", f"{abs(cat['evolution'])/facteur:,.2f} {unite}", delta_color="normal")
                    statut = "TARGET DÉPASSÉ ✅"
                
                st.markdown("**Calcul :**")
                st.code(f"""
Évolution = Target - Réalisé

Évolution = {cat['target']:,.0f} - 
            {cat['depots']:,.0f}

Évolution = {cat['evolution']:,.0f}

Statut : {statut}
                """)
            
            # ==================================================================
            # RÉSUMÉ FINAL
            # ==================================================================
            
            st.divider()
            st.markdown("### 📋 Résumé de cette Catégorie")
            
            resume_col1, resume_col2, resume_col3, resume_col4 = st.columns(4)
            
            with resume_col1:
                st.write(f"**Catégorie :** {cat['categorie']}")
                st.write(f"**Top :** {cat['top'] if cat['top'] else 'N/A'}")
            
            with resume_col2:
                st.write(f"**PDM Tranche :** {cat['tranche']}")
                st.write(f"**Nb Villes :** {cat['nb_villes']}")
            
            with resume_col3:
                st.write(f"**Dépôts :** {cat['depots']/facteur:,.2f} {unite}")
                st.write(f"**PDM :** {cat['pdm']:.2f}%")
            
            with resume_col4:
                st.write(f"**Target :** {cat['target']/facteur:,.2f} {unite}")
                if cat['evolution'] > 0:
                    st.write(f"**Gap :** +{cat['evolution']/facteur:,.2f} {unite}")
                else:
                    st.write(f"**Dépassement :** {abs(cat['evolution'])/facteur:,.2f} {unite}")


def afficher_details_ville_interactive(df_saham, df_joined, total_depots_place, total_credits_place, target_pdm, afficher_millions=True):
    """
    Tableau détaillé interactif avec possibilité de voir le détail des calculs
    """
    
    st.subheader("🏙️ Détails par Ville - Interactif")
    
    st.info("👆 Cliquez sur une ville pour voir le détail des calculs et la provenance des montants")
    
    facteur = 1e6  # milliers DH ÷ 1 000 000 = Md
    unite = "Md"
    
    # Trier par dépôts
    df_sorted = df_saham.sort_values('Depots', ascending=False).reset_index(drop=True)
    
    # Pour chaque ville, créer un expander
    for idx, row in df_sorted.iterrows():
        ville = row['Localite']
        depots = row['Depots']
        credits = row['Credits']
        pdm = row['PDM']
        
        # Créer un expander pour chaque ville
        with st.expander(f"🏙️ {idx+1}. {ville} - Dépôts: {depots/facteur:,.2f} {unite} | PDM: {pdm:.2f}%"):
            
            # Récupérer les agences de cette ville
            agences_ville = df_joined[df_joined['Localite'] == ville]
            
            # Créer 3 colonnes pour les 3 types de détails
            col1, col2, col3 = st.columns(3)
            
            # ===== COLONNE 1 : DÉTAILS DÉPÔTS =====
            with col1:
                st.markdown("### 💰 Dépôts")
                st.metric("Total", f"{depots/facteur:,.2f} {unite}")
                
                st.markdown("**Provenance :**")
                st.markdown(f"*{len(agences_ville)} agence(s)*")
                
                # Tableau des agences
                if len(agences_ville) > 0:
                    agences_detail = agences_ville[['Code Agence', 'Depots']].copy()
                    agences_detail['Depots'] = agences_detail['Depots'].apply(
                        lambda x: f"{x/facteur:,.2f} {unite}"
                    )
                    agences_detail.columns = ['Agence', 'Dépôts']
                    
                    st.dataframe(agences_detail, hide_index=True, use_container_width=True)
                    
                    # Vérification du total
                    total_calcule = agences_ville['Depots'].sum()
                    st.success(f"✅ Total vérifié : {total_calcule/facteur:,.2f} {unite}")
            
            # ===== COLONNE 2 : DÉTAILS CRÉDITS =====
            with col2:
                st.markdown("### 💳 Crédits")
                st.metric("Total", f"{credits/facteur:,.2f} {unite}")
                
                st.markdown("**Provenance :**")
                st.markdown(f"*{len(agences_ville)} agence(s)*")
                
                # Tableau des agences
                if len(agences_ville) > 0:
                    agences_detail_credits = agences_ville[['Code Agence', 'Crédits']].copy()
                    agences_detail_credits['Crédits'] = agences_detail_credits['Crédits'].apply(
                        lambda x: f"{x/facteur:,.2f} {unite}"
                    )
                    agences_detail_credits.columns = ['Agence', 'Crédits']
                    
                    st.dataframe(agences_detail_credits, hide_index=True, use_container_width=True)
                    
                    # Vérification du total
                    total_calcule_credits = agences_ville['Crédits'].sum()
                    st.success(f"✅ Total vérifié : {total_calcule_credits/facteur:,.2f} {unite}")
            
            # ===== COLONNE 3 : DÉTAILS PDM ET TARGET =====
            with col3:
                st.markdown("### 📊 Calculs")
                
                # PDM
                st.markdown("**Part de Marché (PDM) :**")
                st.code(f"""
PDM = (Dépôts Ville / Total Marché) × 100

PDM = ({depots:,.0f} / {total_depots_place:,.0f}) × 100

PDM = {pdm:.4f}%
                """)
                
                st.markdown("---")
                
                # Target
                target_depots = total_depots_place * (target_pdm / 100) / len(df_saham)
                evolution = target_depots - depots
                
                st.markdown("**Target Dépôts :**")
                st.code(f"""
Target = Total Marché × Target PDM / Nb Villes

Target = {total_depots_place:,.0f} × {target_pdm}% / {len(df_saham)}

Target = {target_depots:,.2f}
                """)
                
                st.markdown("---")
                
                st.markdown("**Évolution :**")
                if evolution > 0:
                    st.error(f"Gap à combler : +{evolution/facteur:,.2f} {unite}")
                else:
                    st.success(f"Target dépassé : {evolution/facteur:,.2f} {unite}")
            
            # ===== RÉSUMÉ =====
            st.divider()
            st.markdown("### 📋 Résumé")
            
            resume_col1, resume_col2, resume_col3, resume_col4 = st.columns(4)
            
            with resume_col1:
                st.metric("Agences", len(agences_ville))
            
            with resume_col2:
                st.metric("Dépôts", f"{depots/facteur:,.2f} {unite}")
            
            with resume_col3:
                st.metric("PDM", f"{pdm:.2f}%")
            
            with resume_col4:
                if evolution > 0:
                    st.metric("Gap", f"+{evolution/facteur:,.2f} {unite}", delta_color="inverse")
                else:
                    st.metric("Dépassement", f"{abs(evolution)/facteur:,.2f} {unite}", delta_color="normal")







def viz_categorie_saham_pro(df_saham, df_bam, total_depots_bam, total_credits_bam):
    """
    ONGLET 1 : Calcul Catégorie - Version Professionnelle
    """
    
    st.header("Calcul Catégorie : Saham Présent / Absent")
    
    # Villes
    if df_bam is not None:
        villes_bam = set(df_bam['Localite'].unique())
    else:
        villes_bam = set()
    
    villes_saham = set(df_saham['Localite'].unique())
    villes_absentes = villes_bam - villes_saham if villes_bam else set()
    
    # Calculer les métriques
    nb_saham_present = len(villes_saham)
    depots_saham_present = df_saham['Depots'].sum()
    credits_saham_present = df_saham['Credits'].sum()
    pdm_saham_present = (depots_saham_present / total_depots_bam) * 100 if total_depots_bam > 0 else 0
    
    nb_saham_absent = len(villes_absentes)
    nb_total = nb_saham_present + nb_saham_absent
    
    # Affichage en 3 colonnes
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Saham Présent")
        st.metric("Nombre de villes", nb_saham_present)
        st.metric("Dépôts (Md)", f"{depots_saham_present/1e6:,.2f}")
        st.metric("Crédits (Md)", f"{credits_saham_present/1e6:,.2f}")
        st.metric("PDM", f"{pdm_saham_present:.2f}%")
        
        with st.expander("Voir le détail du calcul"):
            st.write("**Nombre de villes :**")
            st.code(f"Villes Saham = {nb_saham_present}")
            
            st.write("**Total Dépôts :**")
            st.code(f"Dépôts = {depots_saham_present:,.0f}")
            
            st.write("**PDM :**")
            st.code(f"""
PDM = (Dépôts / Total Marché) × 100
PDM = ({depots_saham_present:,.0f} / {total_depots_bam:,.0f}) × 100
PDM = {pdm_saham_present:.2f}%
            """)
    
    with col2:
        st.subheader("Saham Absent")
        st.metric("Nombre de villes", nb_saham_absent)
        st.metric("Dépôts (Md)", "0.00")
        st.metric("Crédits (Md)", "0.00")
        st.metric("PDM", "0.00%")
        
        if nb_saham_absent > 0:
            with st.expander("Liste des villes absentes"):
                for ville in sorted(villes_absentes):
                    st.write(f"- {ville}")
    
    with col3:
        st.subheader("Total Général")
        st.metric("Total villes", nb_total)
        
        pct_present = (nb_saham_present/nb_total*100) if nb_total > 0 else 0
        pct_absent = (nb_saham_absent/nb_total*100) if nb_total > 0 else 0
        
        st.write(f"**Saham Présent :** {nb_saham_present} ({pct_present:.1f}%)")
        st.write(f"**Saham Absent :** {nb_saham_absent} ({pct_absent:.1f}%)")
        
        # Graphique
        fig = go.Figure(data=[go.Pie(
            labels=['Saham Présent', 'Saham Absent'],
            values=[nb_saham_present, nb_saham_absent],
            hole=0.4,
            marker_colors=['#1f77b4', '#ff7f0e']
        )])
        fig.update_layout(
            height=300, 
            margin=dict(t=20, b=20, l=20, r=20),
            showlegend=True
        )
        st.plotly_chart(fig, use_container_width=True)


def viz_top_saham_pro(df_saham, total_depots_bam):
    """
    ONGLET 2 : Calcul Top avec filtre Top 25/10/5
    """
    
    st.header("Calcul Top : Top N localités / Autres")
    
    # FILTRE : Top 25, 10 ou 5
    col_filter, col_space = st.columns([1, 3])
    with col_filter:
        top_n = st.selectbox(
            "Sélectionner le Top",
            options=[25, 10, 5],
            index=0,
            key="top_n_selector"
        )
    
    st.divider()
    
    # Calculer Top N
    df_sorted = df_saham.sort_values('Depots', ascending=False)
    top_n_villes = df_sorted.head(top_n)['Localite'].tolist()
    
    df_saham['Top'] = df_saham['Localite'].apply(
        lambda x: f'Top {top_n}' if x in top_n_villes else 'Autres'
    )
    
    df_top = df_saham[df_saham['Top'] == f'Top {top_n}']
    df_autres = df_saham[df_saham['Top'] == 'Autres']
    
    depots_saham_total = df_saham['Depots'].sum()
    depots_top = df_top['Depots'].sum()
    depots_autres = df_autres['Depots'].sum()
    credits_top = df_top['Credits'].sum()
    credits_autres = df_autres['Credits'].sum()
    pdm_top = (depots_top / total_depots_bam) * 100 if total_depots_bam > 0 else 0
    pdm_autres = (depots_autres / total_depots_bam) * 100 if total_depots_bam > 0 else 0
    
    # Affichage en 3 colonnes
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader(f"Top {top_n}")
        st.metric("Nombre de villes", len(df_top))
        st.metric("Dépôts (Md)", f"{depots_top/1e6:,.2f}")
        st.metric("Crédits (Md)", f"{credits_top/1e6:,.2f}")
        st.metric("PDM", f"{pdm_top:.2f}%")
        st.metric("% du Total Saham", f"{(depots_top/depots_saham_total)*100:.1f}%")
        
        with st.expander("Voir le détail du calcul"):
            st.write(f"**Top {top_n} :** Les {top_n} villes avec le plus de dépôts")
            st.code(f"""
Dépôts Top {top_n} = {depots_top:,.0f}
Total Saham = {depots_saham_total:,.0f}

% du Total = ({depots_top:,.0f} / {depots_saham_total:,.0f}) × 100
% du Total = {(depots_top/depots_saham_total)*100:.2f}%
            """)
        
        # Liste des villes du Top N
        with st.expander(f"Liste des {top_n} villes"):
            for idx, ville in enumerate(top_n_villes, 1):
                depots_ville = df_saham[df_saham['Localite'] == ville]['Depots'].values[0]
                st.write(f"{idx}. {ville} : {depots_ville/1e6:.2f} Md")
    
    with col2:
        st.subheader("Autres")
        st.metric("Nombre de villes", len(df_autres))
        st.metric("Dépôts (Md)", f"{depots_autres/1e6:,.2f}")
        st.metric("Crédits (Md)", f"{credits_autres/1e6:,.2f}")
        st.metric("PDM", f"{pdm_autres:.2f}%")
        st.metric("% du Total Saham", f"{(depots_autres/depots_saham_total)*100:.1f}%")
    
    with col3:
        st.subheader("Comparaison")
        
        pct_top = (depots_top/depots_saham_total)*100
        pct_autres = (depots_autres/depots_saham_total)*100
        
        st.write(f"**Concentration Top {top_n} :** {pct_top:.1f}%")
        st.write(f"**Reste (Autres) :** {pct_autres:.1f}%")
        
        # Graphique
        fig = go.Figure(data=[go.Pie(
            labels=[f'Top {top_n}', 'Autres'],
            values=[depots_top, depots_autres],
            hole=0.4,
            marker_colors=['#2ca02c', '#d62728']
        )])
        fig.update_layout(
            height=300,
            margin=dict(t=20, b=20, l=20, r=20),
            showlegend=True
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Graphique détaillé du Top N
    st.subheader(f"Détail du Top {top_n} par Dépôts")
    
    df_top_sorted = df_top.sort_values('Depots', ascending=True)
    
    fig_bar = px.bar(
        df_top_sorted,
        x='Depots',
        y='Localite',
        orientation='h',
        title=f"Top {top_n} des villes par Dépôts",
        labels={'Depots': 'Dépôts (MAD)', 'Localite': 'Ville'},
        color='Depots',
        color_continuous_scale='Blues'
    )
    
    fig_bar.update_layout(height=max(400, top_n * 30))
    st.plotly_chart(fig_bar, use_container_width=True)


def viz_pdm_saham_pro(df_saham):
    """
    ONGLET 3 : PDM Saham avec filtre par tranche (comme dans l'image)
    """
    
    st.header("Part De Marché par Tranche")
    
    # Définir les tranches
    def get_tranche_pdm(pdm):
        if pdm >= 10:
            return 'Sup >10%'
        elif pdm >= 7:
            return 'Sup 7-10%'
        elif pdm >= 5:
            return 'Inf 5-7%'
        else:
            return 'Inf <5%'
    
    df_saham['Tranche_PDM'] = df_saham['PDM'].apply(get_tranche_pdm)
    
    # FILTRE : Sélection de la tranche
    tranches_disponibles = df_saham['Tranche_PDM'].value_counts().index.tolist()
    
    tranche_selectionnee = st.selectbox(
        "Sélectionner une tranche PDM",
        options=['Toutes'] + sorted(tranches_disponibles, reverse=True),
        index=0
    )
    
    st.divider()
    
    # Si "Toutes", afficher le résumé en colonnes (comme dans l'image)
    if tranche_selectionnee == 'Toutes':
        st.subheader("Part De Marché par Tranche")
        
        # Calculer les données pour chaque tranche
        tranches_order = ['Sup >10%', 'Sup 7-10%', 'Inf 5-7%', 'Inf <5%']
        tranches_data = []
        
        for tranche in tranches_order:
            df_tranche = df_saham[df_saham['Tranche_PDM'] == tranche]
            if len(df_tranche) > 0:
                tranches_data.append({
                    'Tranche': tranche,
                    'Nb Villes': len(df_tranche),
                    'Dépôts': df_tranche['Depots'].sum(),
                    'Crédits': df_tranche['Credits'].sum(),
                    'PDM Moyenne': df_tranche['PDM'].mean(),
                    'Villes': df_tranche['Localite'].tolist()
                })
        
        # Afficher en colonnes (comme dans l'image)
        if len(tranches_data) > 0:
            cols = st.columns(len(tranches_data))
            
            for idx, tranche_info in enumerate(tranches_data):
                with cols[idx]:
                    # Titre de la tranche
                    st.markdown(f"### {tranche_info['Tranche']}")
                    
                    # Villes
                    st.write("**Villes**")
                    st.markdown(f"<h2 style='text-align: center; margin: 0;'>{tranche_info['Nb Villes']}</h2>", 
                               unsafe_allow_html=True)
                    
                    st.write("")
                    
                    # Dépôts
                    st.write("**Dépôts**")
                    st.markdown(f"<h3 style='text-align: center; margin: 0;'>{tranche_info['Dépôts']/1e6:.2f} M</h3>", 
                               unsafe_allow_html=True)
                    
                    st.write("")
                    
                    # PDM Moy.
                    st.write("**PDM Moy.**")
                    st.markdown(f"<h3 style='text-align: center; margin: 0;'>{tranche_info['PDM Moyenne']:.2f}%</h3>", 
                               unsafe_allow_html=True)
                    
                    st.write("")
                    
                    # Bouton pour voir les villes
                    with st.expander("Villes"):
                        for ville in sorted(tranche_info['Villes']):
                            pdm_ville = df_saham[df_saham['Localite'] == ville]['PDM'].values[0]
                            st.write(f"- {ville} ({pdm_ville:.2f}%)")
    
    else:
        # Afficher les détails d'une tranche spécifique
        df_tranche = df_saham[df_saham['Tranche_PDM'] == tranche_selectionnee]
        
        st.subheader(f"Détail : {tranche_selectionnee}")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Nombre de villes", len(df_tranche))
        
        with col2:
            st.metric("Total Dépôts (Md)", f"{df_tranche['Depots'].sum()/1e6:,.2f}")
        
        with col3:
            st.metric("PDM Moyenne", f"{df_tranche['PDM'].mean():.2f}%")
        
        st.divider()
        
        # Tableau détaillé
        st.subheader("Liste des villes")
        
        df_display = df_tranche[['Localite', 'Depots', 'Credits', 'PDM']].copy()
        df_display = df_display.sort_values('Depots', ascending=False)
        df_display['Depots'] = df_display['Depots'].apply(lambda x: f"{x/1e6:.2f} Md")
        df_display['Credits'] = df_display['Credits'].apply(lambda x: f"{x/1e6:.2f} Md")
        df_display['PDM'] = df_display['PDM'].apply(lambda x: f"{x:.2f}%")
        df_display.columns = ['Ville', 'Dépôts', 'Crédits', 'PDM']
        
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        # Graphique
        st.divider()
        st.subheader("Visualisation")
        
        df_chart = df_tranche.sort_values('Depots', ascending=True)
        
        fig = px.bar(
            df_chart,
            x='Depots',
            y='Localite',
            orientation='h',
            title=f"Villes dans la tranche {tranche_selectionnee}",
            labels={'Depots': 'Dépôts (MAD)', 'Localite': 'Ville'},
            color='PDM',
            color_continuous_scale='Viridis'
        )
        
        fig.update_layout(height=max(400, len(df_tranche) * 25))
        st.plotly_chart(fig, use_container_width=True)


def viz_targets_saham_pro(df_saham, total_depots_bam, total_credits_bam, target_pdm):
    """
    ONGLET 4 : Targets Dépôts / Crédits - Version Professionnelle
    """
    
    st.header("Targets Dépôts / Crédits")
    
    st.write(f"**Target PDM Défini :** {target_pdm:.1f}%")
    
    st.divider()
    
    # Calculer les targets
    depots_saham = df_saham['Depots'].sum()
    credits_saham = df_saham['Credits'].sum()
    
    target_depots_global = total_depots_bam * (target_pdm / 100)
    target_credits_global = total_credits_bam * (target_pdm / 100)
    
    # 3 colonnes
    col1, col2, col3 = st.columns([1, 1, 1.2])
    
    with col1:
        st.subheader("Target Dépôts")
        st.metric("Target Global (Md)", f"{target_depots_global/1e6:,.2f}")
        st.metric("Réalisé (Md)", f"{depots_saham/1e6:,.2f}")
        
        taux_real_depots = (depots_saham/target_depots_global)*100
        st.metric("Taux Réalisation", f"{taux_real_depots:.1f}%")
        
        st.write("")
        
        with st.expander("Détail du calcul"):
            st.write("**Formule :**")
            st.code("Target = Total Marché × Target PDM")
            
            st.write("**Calcul :**")
            st.code(f"""
Target = {total_depots_bam:,.0f} × {target_pdm}%
Target = {target_depots_global:,.0f}

Réalisé = {depots_saham:,.0f}

Taux = (Réalisé / Target) × 100
Taux = {taux_real_depots:.2f}%
            """)
    
    with col2:
        st.subheader("Target Crédits")
        st.metric("Target Global (Md)", f"{target_credits_global/1e6:,.2f}")
        st.metric("Réalisé (Md)", f"{credits_saham/1e6:,.2f}")
        
        taux_real_credits = (credits_saham/target_credits_global)*100
        st.metric("Taux Réalisation", f"{taux_real_credits:.1f}%")
        
        st.write("")
        
        with st.expander("Détail du calcul"):
            st.write("**Formule :**")
            st.code("Target = Total Marché × Target PDM")
            
            st.write("**Calcul :**")
            st.code(f"""
Target = {total_credits_bam:,.0f} × {target_pdm}%
Target = {target_credits_global:,.0f}

Réalisé = {credits_saham:,.0f}

Taux = (Réalisé / Target) × 100
Taux = {taux_real_credits:.2f}%
            """)
    
    with col3:
        st.subheader("Visualisation")
        
        # Graphique Target vs Réalisé
        fig_target = go.Figure()
        
        fig_target.add_trace(go.Bar(
            name='Target',
            x=['Dépôts', 'Crédits'],
            y=[target_depots_global/1e6, target_credits_global/1e6],
            marker_color='#ff7f0e',
            text=[f"{target_depots_global/1e6:.2f} Md", f"{target_credits_global/1e6:.2f} Md"],
            textposition='outside'
        ))
        
        fig_target.add_trace(go.Bar(
            name='Réalisé',
            x=['Dépôts', 'Crédits'],
            y=[depots_saham/1e6, credits_saham/1e6],
            marker_color='#1f77b4',
            text=[f"{depots_saham/1e6:.2f} Md", f"{credits_saham/1e6:.2f} Md"],
            textposition='outside'
        ))
        
        fig_target.update_layout(
            barmode='group',
            height=400,
            yaxis_title="Montant (Md MAD)",
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig_target, use_container_width=True)


def viz_evolution_saham_pro(df_saham, total_depots_bam, total_credits_bam, target_pdm):
    """
    ONGLET 5 : Evolution - Version Professionnelle
    """
    
    st.header("Evolution (Target - Montant Dépôts ou Crédits Saham)")
    
    # Calculer
    depots_saham = df_saham['Depots'].sum()
    credits_saham = df_saham['Credits'].sum()
    
    target_depots = total_depots_bam * (target_pdm / 100)
    target_credits = total_credits_bam * (target_pdm / 100)
    
    evolution_depots = target_depots - depots_saham
    evolution_credits = target_credits - credits_saham
    
    # 2 colonnes
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Évolution Dépôts")
        
        if evolution_depots > 0:
            st.error(f"**Gap à combler : +{evolution_depots/1e6:.2f} Md**")
            st.write(f"Il vous manque **{evolution_depots/1e6:,.2f} M** pour atteindre le target.")
        else:
            st.success(f"**Target dépassé : {abs(evolution_depots)/1e6:.2f} Md**")
            st.write(f"Vous avez dépassé le target de **{abs(evolution_depots)/1e6:,.2f} M**.")
        
        st.write("")
        
        st.metric("Target (Md)", f"{target_depots/1e6:,.2f}")
        st.metric("Réalisé (Md)", f"{depots_saham/1e6:,.2f}")
        
        delta_color = "inverse" if evolution_depots > 0 else "normal"
        st.metric("Écart (Md)", f"{evolution_depots/1e6:,.2f}", delta_color=delta_color)
        
        st.write("")
        
        with st.expander("Détail du calcul"):
            st.write("**Formule :**")
            st.code("Évolution = Target - Réalisé")
            
            st.write("**Calcul :**")
            statut = "À COMBLER" if evolution_depots > 0 else "TARGET DÉPASSÉ"
            st.code(f"""
Évolution = {target_depots:,.0f} - {depots_saham:,.0f}
Évolution = {evolution_depots:,.0f}

Statut : {statut}
            """)
    
    with col2:
        st.subheader("Évolution Crédits")
        
        if evolution_credits > 0:
            st.error(f"**Gap à combler : +{evolution_credits/1e6:.2f} Md**")
            st.write(f"Il vous manque **{evolution_credits/1e6:,.2f} M** pour atteindre le target.")
        else:
            st.success(f"**Target dépassé : {abs(evolution_credits)/1e6:.2f} Md**")
            st.write(f"Vous avez dépassé le target de **{abs(evolution_credits)/1e6:,.2f} M**.")
        
        st.write("")
        
        st.metric("Target (Md)", f"{target_credits/1e6:,.2f}")
        st.metric("Réalisé (Md)", f"{credits_saham/1e6:,.2f}")
        
        delta_color = "inverse" if evolution_credits > 0 else "normal"
        st.metric("Écart (Md)", f"{evolution_credits/1e6:,.2f}", delta_color=delta_color)
        
        st.write("")
        
        with st.expander("Détail du calcul"):
            st.write("**Formule :**")
            st.code("Évolution = Target - Réalisé")
            
            st.write("**Calcul :**")
            statut = "À COMBLER" if evolution_credits > 0 else "TARGET DÉPASSÉ"
            st.code(f"""
Évolution = {target_credits:,.0f} - {credits_saham:,.0f}
Évolution = {evolution_credits:,.0f}

Statut : {statut}
            """)
    
    st.divider()
    
    # Graphique
    st.subheader("Visualisation des Gaps")
    
    fig_evolution = go.Figure()
    
    colors = [
        '#d62728' if evolution_depots > 0 else '#2ca02c',
        '#d62728' if evolution_credits > 0 else '#2ca02c'
    ]
    
    fig_evolution.add_trace(go.Bar(
        x=['Dépôts', 'Crédits'],
        y=[evolution_depots/1e6, evolution_credits/1e6],
        marker_color=colors,
        text=[f"{evolution_depots/1e6:+.2f} Md", f"{evolution_credits/1e6:+.2f} Md"],
        textposition='outside',
        showlegend=False
    ))
    
    fig_evolution.update_layout(
        height=400,
        yaxis_title="Gap (Md MAD)",
        xaxis_title=""
    )
    
    # Ligne à 0
    fig_evolution.add_hline(y=0, line_dash="dash", line_color="gray", line_width=1)
    
    st.plotly_chart(fig_evolution, use_container_width=True)
    
    # Légende
    col_leg1, col_leg2 = st.columns(2)
    with col_leg1:
        st.caption("Rouge : Gap à combler (positif)")
    with col_leg2:
        st.caption("Vert : Target dépassé (négatif)")


def create_saham_visualizations():
    """Page principale Visualisations Saham Bank"""
    
    st.header("Visualisations Saham Bank")
    
    st.markdown("""
    Cette page permet d'analyser les données Saham Bank par **localité** avec calcul de la **PDM** (Part De Marché).
    
    **Vous devez fournir 2 fichiers Excel :**
    1. **Référentiel agences** (Code Agence, Code Localité, Localité)
    2. **Données financières** (Période, Code Agence, Dépôts, Crédits)
    """)
    
    st.divider()
    
    # Upload des fichiers
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("1️⃣ Référentiel Agences")
        ref_file = st.file_uploader(
            "Fichier Excel",
            type=['xlsx', 'xls'],
            key="ref_file",
            help="Colonnes attendues : Code Agence, Code Localité, Localité"
        )
        
        if ref_file:
            try:
                df_ref = pd.read_excel(ref_file)
                st.success(f"✅ {len(df_ref)} agences chargées")
                st.session_state.saham_referentiel = df_ref
                
                with st.expander("Aperçu du référentiel"):
                    st.dataframe(df_ref.head(10))
            except Exception as e:
                st.error(f"Erreur : {str(e)}")
    
    with col2:
        st.subheader("2️⃣ Données Financières")
        fin_file = st.file_uploader(
            "Fichier Excel",
            type=['xlsx', 'xls'],
            key="fin_file",
            help="Colonnes attendues : Période, Code Agence, Dépôts, Crédits"
        )
        
        if fin_file:
            try:
                df_fin = pd.read_excel(fin_file)
                st.success(f"✅ {len(df_fin)} lignes chargées")
                st.session_state.saham_financial = df_fin
                
                with st.expander("Aperçu des données"):
                    st.dataframe(df_fin.head(10))
            except Exception as e:
                st.error(f"Erreur : {str(e)}")
    
    st.divider()
    
    # Bouton de traitement
    if st.session_state.saham_referentiel is not None and st.session_state.saham_financial is not None:
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔄 Traiter et Agréger", type="primary", use_container_width=True):
                with st.spinner("Jointure et agrégation en cours..."):
                    try:
                        # Jointure et agrégation
                        df_agg = join_and_aggregate_saham(
                            st.session_state.saham_financial,
                            st.session_state.saham_referentiel
                        )
                        
                        st.session_state.saham_aggregated = df_agg
                        
                        st.success(f"✅ Données agrégées : {len(df_agg)} localités")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Erreur lors du traitement : {str(e)}")
                        st.exception(e)
    
    # Afficher les visualisations si données traitées
    if st.session_state.saham_aggregated is not None:
        
        st.divider()
        st.success("✅ Données prêtes pour l'analyse")
        
        # Onglets pour les 5 visualisations
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Catégorie", 
            "Top", 
            "PDM", 
            "Targets", 
            "Evolution"
        ])
        
        # Récupérer les totaux BAM
        if st.session_state.combined_data_bam is not None:
            total_depots_bam = st.session_state.total_depots_bam
            total_credits_bam = st.session_state.total_credits_bam
            df_bam = st.session_state.combined_data_bam
        else:
            total_depots_bam = 11_497_995_536  # Valeur par défaut
            total_credits_bam = 11_250_000_000  # Valeur par défaut
            df_bam = None
        
        # Target PDM (peut être ajusté avec un slider global)
        target_pdm = st.sidebar.slider("🎯 Target PDM (%)", 1.0, 20.0, 8.0, 0.5)
        
        with tab1:
            viz_categorie_saham_pro(
                st.session_state.saham_aggregated, 
                df_bam,
                total_depots_bam,
                total_credits_bam
            )
        
        with tab2:
            viz_top_saham_pro(st.session_state.saham_aggregated, total_depots_bam)
        
        with tab3:
            viz_pdm_saham_pro(st.session_state.saham_aggregated)
        
        with tab4:
            viz_targets_saham_pro(
                st.session_state.saham_aggregated,
                total_depots_bam,
                total_credits_bam,
                target_pdm
            )
        
        with tab5:
            viz_evolution_saham_pro(
                st.session_state.saham_aggregated,
                total_depots_bam,
                total_credits_bam,
                target_pdm
            )
    
    else:
        if st.session_state.saham_referentiel is None or st.session_state.saham_financial is None:
            st.info("👆 Veuillez charger les 2 fichiers Excel ci-dessus")

# ============================================================================
# MODULE BAM
# ============================================================================

# Module BAM
def import_bam_multi_annees():
    """
    Interface d'import BAM avec gestion multi-années (2016-2025)
    Permet d'importer des données mensuelles pour chaque année et de tout combiner
    """
    
    st.subheader("📊 Import BAM Multi-Années (2016-2025)")
    
    # =========================================================================
    # CHOIX DU MODE D'IMPORT
    # =========================================================================
    
    mode_import = st.radio(
        "Choisissez le mode d'import",
        ["📂 Import mensuel (fichiers séparés)", "⚡ Import fichier combiné (rapide)"],
        horizontal=True,
        help="Import mensuel : uploader mois par mois | Import combiné : uploader un seul fichier Excel déjà combiné"
    )
    
    st.divider()
    
    # =========================================================================
    # MODE 1 : IMPORT FICHIER COMBINÉ (RAPIDE)
    # =========================================================================
    
    if mode_import == "⚡ Import fichier combiné (rapide)":
        st.markdown("""
        <div class="info-box">
            <h4>⚡ Import Rapide</h4>
            <p>Uploadez directement un fichier Excel qui contient déjà toutes les données BAM combinées.</p>
            <p><strong>Format attendu :</strong></p>
            <ul>
                <li>Colonnes : <code>Annee</code>, <code>mois</code>, <code>Code</code>, <code>Localite</code>, <code>Nombre_Guichets</code>, <code>Montant_Depots</code>, <code>Montant_Credits</code></li>
                <li>Exemple : résultat d'un export précédent de cette application</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        fichier_combine = st.file_uploader(
            "📂 Sélectionnez votre fichier Excel combiné",
            type=['xlsx', 'xls'],
            key="fichier_bam_combine"
        )
        
        if fichier_combine:
            try:
                with st.spinner("⏳ Chargement du fichier..."):
                    df_combine = pd.read_excel(fichier_combine)
                    
                    # Normaliser et nettoyer
                    df_combine = normalize_bam_columns(df_combine)
                    df_combine = clean_numeric_columns(df_combine)
                    
                    # Vérifier les colonnes essentielles
                    required_cols = ['Annee', 'mois', 'Localite', 'Montant_Depots', 'Montant_Credits']
                    missing_cols = [col for col in required_cols if col not in df_combine.columns]
                    
                    if missing_cols:
                        st.error(f"❌ Colonnes manquantes : {missing_cols}")
                        st.info("Colonnes présentes : " + ", ".join(df_combine.columns.tolist()))
                        return
                    
                    # Ajouter Direction_Regionale si absente
                    if 'Direction_Regionale' not in df_combine.columns:
                        df_combine = add_direction_regionale(df_combine)
                    
                    # Stocker dans session_state
                    st.session_state.combined_data_bam = df_combine
                    
                    st.success(f"✅ Fichier chargé avec succès : **{len(df_combine):,}** lignes")
                    
                    # Résumé
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Années", df_combine['Annee'].nunique())
                    with col2:
                        nb_mois = df_combine.groupby('Annee')['mois'].nunique().sum()
                        st.metric("Mois (total)", nb_mois)
                    with col3:
                        st.metric("Localités", df_combine['Localite'].nunique())
                    with col4:
                        total_depots = df_combine['Montant_Depots'].sum() / 1e6
                        st.metric("Dépôts totaux", f"{total_depots:.0f} Mrd")
                    
                    # Aperçu
                    with st.expander("🔍 Aperçu des données", expanded=False):
                        st.dataframe(df_combine.head(20), use_container_width=True)
                        
                        # Résumé par année
                        st.write("**Résumé par année :**")
                        summary = df_combine.groupby('Annee').agg({
                            'mois': 'nunique',
                            'Localite': 'nunique',
                            'Montant_Depots': 'sum',
                            'Montant_Credits': 'sum'
                        }).reset_index()
                        summary.columns = ['Année', 'Nb Mois', 'Localités', 'Dépôts', 'Crédits']
                        summary['Dépôts'] = summary['Dépôts'].apply(lambda x: f"{x/1e6:.2f} Mrd")
                        summary['Crédits'] = summary['Crédits'].apply(lambda x: f"{x/1e6:.2f} Mrd")
                        st.dataframe(summary, use_container_width=True, hide_index=True)
                    
                    st.info("💡 Les données sont maintenant chargées. Allez sur **'Visualisations BAM'** pour les analyser.")
                    
            except Exception as e:
                st.error(f"❌ Erreur lors du chargement : {str(e)}")
                st.exception(e)
        
        return  # Sortir de la fonction ici pour le mode combiné
    
    # =========================================================================
    # MODE 2 : IMPORT MENSUEL (FICHIERS SÉPARÉS)
    # =========================================================================
    
    st.markdown("""
    <div class="info-box">
        <h4>📋 Instructions - Import Mensuel</h4>
        <ul>
            <li><strong>Étape 1 :</strong> Sélectionnez une ou plusieurs années (2016-2025)</li>
            <li><strong>Étape 2 :</strong> Pour chaque année, uploadez les fichiers mensuels disponibles</li>
            <li><strong>Étape 3 :</strong> Combinez les mois de chaque année</li>
            <li><strong>Étape 4 :</strong> Combinez toutes les années ensemble</li>
            <li><strong>Étape 5 :</strong> Téléchargez le fichier combiné final</li>
            <li>⚠️ Les mois manquants seront ignorés automatiquement</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # =========================================================================
    # INITIALISATION SESSION STATE
    # =========================================================================
    
    if 'bam_years_data' not in st.session_state:
        st.session_state.bam_years_data = {}  # {année: {data, nb_mois, mois_list}}
    
    if 'bam_final_combined' not in st.session_state:
        st.session_state.bam_final_combined = None
    
    # =========================================================================
    # ÉTAPE 1 : SÉLECTION DES ANNÉES
    # =========================================================================
    
    st.markdown("### 1️⃣ Sélection des Années")
    
    annees_disponibles = list(range(2016, 2026))  # 2016 à 2025
    
    annees_selectionnees = st.multiselect(
        "Choisissez les années à importer",
        options=annees_disponibles,
        default=[2024, 2025] if not st.session_state.bam_years_data else list(st.session_state.bam_years_data.keys()),
        key="select_annees_bam",
        help="Vous pouvez sélectionner plusieurs années"
    )
    
    if not annees_selectionnees:
        st.warning("⚠️ Veuillez sélectionner au moins une année pour continuer")
        return
    
    st.info(f"✅ {len(annees_selectionnees)} année(s) sélectionnée(s): {', '.join(map(str, sorted(annees_selectionnees)))}")
    
    st.divider()
    
    # =========================================================================
    # ÉTAPE 2 : IMPORT MENSUEL PAR ANNÉE
    # =========================================================================
    
    st.markdown("### 2️⃣ Import des Données Mensuelles")
    st.write("Dépliez chaque année pour uploader les fichiers mensuels")
    
    for annee in sorted(annees_selectionnees):
        
        # Déterminer si l'expander doit être ouvert par défaut
        is_expanded = (annee == max(annees_selectionnees) and annee not in st.session_state.bam_years_data)
        
        with st.expander(f"📅 **Année {annee}**", expanded=is_expanded):
            
            # Afficher le statut si déjà combiné
            if annee in st.session_state.bam_years_data:
                year_info = st.session_state.bam_years_data[annee]
                
                st.success(f"✅ Année {annee} déjà combinée")
                
                col_info1, col_info2, col_info3 = st.columns(3)
                
                with col_info1:
                    st.metric("Mois importés", year_info['nb_mois'])
                
                with col_info2:
                    st.metric("Total lignes", f"{len(year_info['data']):,}")
                
                with col_info3:
                    mois_names = [['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jui', 
                                  'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc'][m-1] 
                                 for m in sorted(year_info['mois_list'])]
                    st.write(f"**Mois:** {', '.join(mois_names)}")
                
                # Bouton pour recombiner
                if st.button(f"🔄 Recombiner {annee}", key=f"recombine_{annee}"):
                    del st.session_state.bam_years_data[annee]
                    st.rerun()
                
                st.divider()
            
            # Upload pour cette année
            st.write(f"**📂 Fichiers Excel BAM pour l'année {annee}**")
            
            uploaded_files_year = st.file_uploader(
                f"Sélectionnez un ou plusieurs fichiers mensuels pour {annee}",
                type=['xlsx', 'xls'],
                accept_multiple_files=True,
                key=f'upload_bam_{annee}',
                help="Sélectionnez plusieurs fichiers avec Ctrl+Clic"
            )
            
            if uploaded_files_year:
                
                st.write(f"**{len(uploaded_files_year)} fichier(s) uploadé(s)**")
                
                fichiers_pour_annee = []
                
                for idx, uploaded_file in enumerate(uploaded_files_year):
                    try:
                        # Lire le fichier
                        df = pd.read_excel(uploaded_file)
                        
                        # Détecter le mois automatiquement
                        detected_month = get_month_from_filename(uploaded_file.name)
                        
                        # Affichage en colonnes
                        col_file, col_month, col_lines = st.columns([3, 2, 1])
                        
                        with col_file:
                            st.write(f"📄 {uploaded_file.name}")
                        
                        with col_month:
                            mois_selectionne = st.selectbox(
                                "Mois",
                                options=list(range(1, 13)),
                                index=(detected_month - 1) if detected_month else 0,
                                format_func=lambda x: ['Janvier', 'Février', 'Mars', 'Avril', 
                                                       'Mai', 'Juin', 'Juillet', 'Août', 
                                                       'Septembre', 'Octobre', 'Novembre', 'Décembre'][x-1],
                                key=f"mois_{annee}_{idx}_{uploaded_file.name}"
                            )
                        
                        with col_lines:
                            st.metric("Lignes", len(df))
                        
                        # Stocker les infos
                        fichiers_pour_annee.append({
                            'filename': uploaded_file.name,
                            'data': df,
                            'month': mois_selectionne,
                            'year': annee
                        })
                    
                    except Exception as e:
                        st.error(f"❌ Erreur lors de la lecture de {uploaded_file.name}: {str(e)}")
                
                # Bouton pour combiner les mois de cette année
                if fichiers_pour_annee:
                    st.divider()
                    
                    col_btn_left, col_btn_center, col_btn_right = st.columns([1, 2, 1])
                    
                    with col_btn_center:
                        if st.button(
                            f"✨ Combiner les {len(fichiers_pour_annee)} mois de {annee}",
                            type="primary",
                            use_container_width=True,
                            key=f"btn_combine_{annee}"
                        ):
                            with st.spinner(f"⏳ Combinaison des mois de {annee} en cours..."):
                                try:
                                    # Combiner les fichiers
                                    df_combined = combine_bam_files(fichiers_pour_annee)
                                    
                                    # Normaliser les colonnes
                                    df_combined = normalize_bam_columns(df_combined)
                                    
                                    # Nettoyer les colonnes numériques
                                    df_combined = clean_numeric_columns(df_combined)
                                    
                                    # Ajouter Direction Régionale
                                    df_combined = add_direction_regionale(df_combined)
                                    
                                    # Ajouter colonne année
                                    df_combined['Annee'] = annee
                                    
                                    # Stocker dans session state
                                    st.session_state.bam_years_data[annee] = {
                                        'data': df_combined,
                                        'nb_mois': len(fichiers_pour_annee),
                                        'mois_list': [f['month'] for f in fichiers_pour_annee]
                                    }
                                    
                                    st.success(f"✅ {len(fichiers_pour_annee)} mois combinés pour l'année {annee} !")
                                    st.rerun()
                                
                                except Exception as e:
                                    st.error(f"❌ Erreur lors de la combinaison de {annee}: {str(e)}")
                                    st.exception(e)
    
    st.divider()
    
    # =========================================================================
    # ÉTAPE 3 : COMBINAISON FINALE DE TOUTES LES ANNÉES
    # =========================================================================
    
    st.markdown("### 3️⃣ Combinaison Finale de Toutes les Années")
    
    nb_annees_combinees = len(st.session_state.bam_years_data)
    
    if nb_annees_combinees == 0:
        st.info("ℹ️ Aucune année n'a encore été combinée. Combinez d'abord les mois de chaque année ci-dessus.")
    
    else:
        st.write(f"**{nb_annees_combinees} année(s) prête(s) à être combinée(s):**")
        
        # Tableau récapitulatif
        recap_data = []
        for annee in sorted(st.session_state.bam_years_data.keys()):
            info = st.session_state.bam_years_data[annee]
            mois_names = [['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jui', 
                          'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc'][m-1] 
                         for m in sorted(info['mois_list'])]
            
            recap_data.append({
                'Année': annee,
                'Mois importés': info['nb_mois'],
                'Total lignes': f"{len(info['data']):,}",
                'Mois': ', '.join(mois_names)
            })
        
        df_recap = pd.DataFrame(recap_data)
        st.dataframe(df_recap, use_container_width=True, hide_index=True)
        
        st.divider()
        
        col_final_left, col_final_center, col_final_right = st.columns([1, 2, 1])
        
        with col_final_center:
            if st.button(
                f"🔗 Combiner les {nb_annees_combinees} Année(s)",
                type="primary",
                use_container_width=True,
                key="btn_combine_all_years"
            ):
                with st.spinner("⏳ Combinaison de toutes les années en cours..."):
                    try:
                        # Combiner toutes les années
                        all_dfs = []
                        
                        for annee in sorted(st.session_state.bam_years_data.keys()):
                            df_year = st.session_state.bam_years_data[annee]['data'].copy()
                            all_dfs.append(df_year)
                        
                        # Concaténer toutes les dataframes
                        df_final = pd.concat(all_dfs, ignore_index=True)
                        
                        # Stocker le résultat final
                        st.session_state.bam_final_combined = df_final
                        st.session_state.combined_data_bam = df_final  # Pour compatibilité
                        st.session_state.processing_done = True
                        
                        # Calculer les totaux globaux
                        st.session_state.total_depots_bam = df_final['Montant_Depots'].sum()
                        st.session_state.total_credits_bam = df_final['Montant_Credits'].sum()
                        
                        st.success(f"✅ Combinaison réussie ! {nb_annees_combinees} année(s) combinée(s)")
                        st.rerun()
                    
                    except Exception as e:
                        st.error(f"❌ Erreur lors de la combinaison finale: {str(e)}")
                        st.exception(e)
    
    # =========================================================================
    # ÉTAPE 4 : RÉSULTATS FINAUX ET TÉLÉCHARGEMENT
    # =========================================================================
    
    if st.session_state.bam_final_combined is not None:
        st.divider()
        
        st.markdown("### 4️⃣ Résultats Finaux")
        
        df_final = st.session_state.bam_final_combined
        
        # Métriques globales
        col_m1, col_m2 = st.columns(2)
        
        with col_m1:
            st.metric("📊 Total Lignes", f"{len(df_final):,}")
        
        with col_m2:
            nb_annees = df_final['Annee'].nunique() if 'Annee' in df_final.columns else 0
            st.metric("📅 Années", nb_annees)
        
        st.divider()
        
        # Aperçu des données
        st.write("**📋 Aperçu des données combinées (10 premières lignes)**")
        st.dataframe(df_final.head(10), use_container_width=True)
        
        st.divider()
        
        # Bouton de téléchargement
        st.markdown("### 5️⃣ Téléchargement")
        
        col_dl_left, col_dl_center, col_dl_right = st.columns([1, 2, 1])
        
        with col_dl_center:
            # Préparer le fichier Excel
            output = BytesIO()
            
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_final.to_excel(writer, index=False, sheet_name='BAM_Combined')
            
            excel_data = output.getvalue()
            
            # Nom du fichier avec timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"BAM_Combined_{timestamp}.xlsx"
            
            # Bouton de téléchargement
            st.download_button(
                label="📥 Télécharger le Fichier Combiné (Excel)",
                data=excel_data,
                file_name=filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                help=f"Fichier: {filename}"
            )
        
        st.success("✅ Données prêtes pour l'analyse ! Vous pouvez maintenant accéder aux visualisations.")
        
        # Info sur l'utilisation
        st.info("💡 **Prochaines étapes:** Allez dans 'Visualisations BAM' ou importez les données Saham Bank pour calculer les PDM.")


def visualisations_bam_avancees():
    """
    Visualisations BAM - DERNIER MOIS UNIQUEMENT + GRAPHIQUES COMPLETS
    """
    
    st.header("📊 Visualisations BAM")
    
    if st.session_state.combined_data_bam is None:
        st.warning("⚠️ Veuillez d'abord importer des données BAM")
        return
    
    df_all = st.session_state.combined_data_bam.copy()
    
    if 'Annee' not in df_all.columns or 'mois' not in df_all.columns:
        st.error("❌ Colonnes 'Annee' et 'mois' nécessaires")
        return
    
    # =========================================================================
    # FONCTION POUR OBTENIR LE DERNIER MOIS DE CHAQUE ANNÉE
    # =========================================================================
    
    def get_dernier_mois_par_annee(df):
        """Retourne uniquement le dernier mois de chaque année"""
        result = []
        for annee in df['Annee'].unique():
            df_y = df[df['Annee'] == annee]
            mois_max = df_y['mois'].max()
            df_dernier = df_y[df_y['mois'] == mois_max].copy()
            result.append(df_dernier)
        return pd.concat(result, ignore_index=True)
    
    df_derniers_mois = get_dernier_mois_par_annee(df_all)
    
    st.info("⚠️ **MÉTHODOLOGIE** : Toutes les analyses utilisent UNIQUEMENT le dernier mois de chaque année (JAMAIS de somme)")
    
    st.divider()
    
    # =========================================================================
    # ONGLETS
    # =========================================================================
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Répartition par Année",
        "🔍 Exploration Détaillée", 
        "📈 Évolution par Année",
        "🏙️ Top Localités"
    ])
    
    # =========================================================================
    # TAB 1 : RÉPARTITION PAR ANNÉE
    # =========================================================================
    
    with tab1:
        st.subheader("Répartition par Année")
        
        st.info("💡 Chaque année est évaluée par son DERNIER MOIS uniquement")
        
        # Tableau
        data_tableau = []
        
        for annee in sorted(df_derniers_mois['Annee'].unique()):
            df_y = df_derniers_mois[df_derniers_mois['Annee'] == annee]
            
            mois_num = df_y['mois'].iloc[0] if len(df_y) > 0 else 0
            mois_noms = ['Jan','Fév','Mar','Avr','Mai','Jun','Jul','Aoû','Sep','Oct','Nov','Déc']
            nom_mois = mois_noms[int(mois_num)-1] if 1 <= mois_num <= 12 else str(mois_num)
            
            nb_lignes = len(df_y)
            total_depots = df_y['Montant_Depots'].sum()
            total_credits = df_y['Montant_Credits'].sum()
            
            data_tableau.append({
                'Année': annee,
                'Dernier Mois': nom_mois,
                'Nb Lignes': nb_lignes,
                'Total Dépôts': f"{total_depots/1e6:.2f} Md",
                'Total Crédits': f"{total_credits/1e6:.2f} Md"
            })
        
        df_tableau = pd.DataFrame(data_tableau)
        st.dataframe(df_tableau, use_container_width=True, hide_index=True)
        
        st.divider()
        
        # NOUVEAU : Graphiques côte à côte
        col_g1, col_g2 = st.columns(2)
        
        df_graph = df_derniers_mois.groupby('Annee').agg({
            'Montant_Depots': 'sum',
            'Montant_Credits': 'sum'
        }).reset_index().sort_values('Annee')
        
        # Graphique Dépôts
        with col_g1:
            st.write("**💰 Évolution Dépôts (Dernier Mois)**")
            
            fig_d = go.Figure()
            fig_d.add_trace(go.Scatter(
                x=df_graph['Annee'],
                y=df_graph['Montant_Depots']/1e6,
                mode='lines+markers',
                fill='tozeroy',
                line=dict(width=3, color='#1f77b4'),
                marker=dict(size=10),
                name='Dépôts'
            ))
            
            fig_d.update_layout(
                height=400,
                yaxis_title="Dépôts (Md MAD)",
                xaxis_title="Année",
                showlegend=False
            )
            
            st.plotly_chart(fig_d, use_container_width=True)
        
        # Graphique Crédits
        with col_g2:
            st.write("**💳 Évolution Crédits (Dernier Mois)**")
            
            fig_c = go.Figure()
            fig_c.add_trace(go.Scatter(
                x=df_graph['Annee'],
                y=df_graph['Montant_Credits']/1e6,
                mode='lines+markers',
                fill='tozeroy',
                line=dict(width=3, color='#ff7f0e'),
                marker=dict(size=10),
                name='Crédits'
            ))
            
            fig_c.update_layout(
                height=400,
                yaxis_title="Crédits (Md MAD)",
                xaxis_title="Année",
                showlegend=False
            )
            
            st.plotly_chart(fig_c, use_container_width=True)
    
    # =========================================================================
    # TAB 2 : EXPLORATION DÉTAILLÉE
    # =========================================================================
    
    with tab2:
        st.subheader("Exploration Détaillée")
        
        col_sel1, col_sel2 = st.columns(2)
        
        # Sélection année
        with col_sel1:
            annees_dispo = sorted(df_all['Annee'].unique())
            annee_select = st.selectbox(
                "📅 Sélectionnez une année",
                options=annees_dispo,
                key="annee_explore"
            )
        
        df_annee = df_all[df_all['Annee'] == annee_select]
        
        # Sélection mois
        with col_sel2:
            mois_dispo = sorted(df_annee['mois'].unique())
            mois_noms = ['Jan','Fév','Mar','Avr','Mai','Jun','Jul','Aoû','Sep','Oct','Nov','Déc']
            
            mois_select = st.selectbox(
                "📆 Sélectionnez un mois",
                options=mois_dispo,
                format_func=lambda x: mois_noms[int(x)-1] if 1 <= x <= 12 else str(x),
                key="mois_explore"
            )
        
        df_mois = df_annee[df_annee['mois'] == mois_select]
        
        st.divider()
        
        # Métriques du mois sélectionné
        st.write(f"**📊 {mois_noms[int(mois_select)-1] if 1 <= mois_select <= 12 else mois_select} {annee_select}**")
        
        col_m1, col_m2, col_m3 = st.columns(3)
        
        total_depots_mois = df_mois['Montant_Depots'].sum()
        total_credits_mois = df_mois['Montant_Credits'].sum()
        nb_localites = df_mois['Localite'].nunique()
        
        with col_m1:
            st.metric("Dépôts", f"{total_depots_mois/1e6:.2f} Md")
        with col_m2:
            st.metric("Crédits", f"{total_credits_mois/1e6:.2f} Md")
        with col_m3:
            st.metric("Localités", nb_localites)
        
        st.divider()
        
        # NOUVEAU : Graphiques Dépôts et Crédits par Mois de l'année
        st.write(f"**📈 Évolution Mensuelle en {annee_select}**")
        
        # Grouper par mois
        df_mois_year = df_annee.groupby('mois').agg({
            'Montant_Depots': 'sum',
            'Montant_Credits': 'sum'
        }).reset_index().sort_values('mois')
        
        df_mois_year['Mois_Nom'] = df_mois_year['mois'].apply(
            lambda x: mois_noms[int(x)-1] if 1 <= x <= 12 else str(x)
        )
        
        col_graph1, col_graph2 = st.columns(2)
        
        # Graphique Dépôts par Mois
        with col_graph1:
            st.write("**💰 Dépôts par Mois**")
            
            fig_dm = go.Figure()
            fig_dm.add_trace(go.Scatter(
                x=df_mois_year['Mois_Nom'],
                y=df_mois_year['Montant_Depots']/1e6,  # milliers÷1e6=Md
                mode='lines+markers',
                line=dict(width=3, color='#1f77b4'),
                marker=dict(size=10),
                fill='tozeroy',
                fillcolor='rgba(31, 119, 180, 0.2)'
            ))
            
            fig_dm.update_layout(
                height=400,
                yaxis_title="Dépôts (Md MAD)",
                xaxis_title="Mois",
                showlegend=False
            )
            
            st.plotly_chart(fig_dm, use_container_width=True)
        
        # Graphique Crédits par Mois
        with col_graph2:
            st.write("**💳 Crédits par Mois**")
            
            fig_cm = go.Figure()
            fig_cm.add_trace(go.Scatter(
                x=df_mois_year['Mois_Nom'],
                y=df_mois_year['Montant_Credits']/1e6,
                mode='lines+markers',
                line=dict(width=3, color='#ff7f0e'),
                marker=dict(size=10),
                fill='tozeroy',
                fillcolor='rgba(255, 127, 14, 0.2)'
            ))
            
            fig_cm.update_layout(
                height=400,
                yaxis_title="Crédits (Md MAD)",
                xaxis_title="Mois",
                showlegend=False
            )
            
            st.plotly_chart(fig_cm, use_container_width=True)
        
        st.divider()
        
        # Filtre par région
        if 'Direction_Regionale' in df_mois.columns:
            st.write("**🗺️ Exploration par Région**")
            
            regions_dispo = sorted(df_mois['Direction_Regionale'].unique())
            
            region_select = st.selectbox(
                "Sélectionnez une région",
                options=['Toutes'] + regions_dispo,
                key="region_explore"
            )
            
            if region_select != 'Toutes':
                df_region = df_mois[df_mois['Direction_Regionale'] == region_select]
                
                st.write(f"**📍 Région : {region_select}**")
                
                col_r1, col_r2, col_r3 = st.columns(3)
                
                depots_region = df_region['Montant_Depots'].sum()
                credits_region = df_region['Montant_Credits'].sum()
                nb_villes_region = df_region['Localite'].nunique()
                
                with col_r1:
                    st.metric("Dépôts Région", f"{depots_region/1e6:.2f} Md")
                with col_r2:
                    st.metric("Crédits Région", f"{credits_region/1e6:.2f} Md")
                with col_r3:
                    st.metric("Localités", nb_villes_region)
                
                st.divider()
                
                st.write(f"**🏙️ Localités de {region_select}**")
                
                df_loc_region = df_region.groupby('Localite').agg({
                    'Montant_Depots': 'sum',
                    'Montant_Credits': 'sum'
                }).reset_index().sort_values('Montant_Depots', ascending=False)
                
                # NOUVEAU : Graphiques Dépôts ET Crédits par localité
                col_loc1, col_loc2 = st.columns(2)
                
                df_loc_region['Depots_Md']  = df_loc_region['Montant_Depots']  / 1e6
                df_loc_region['Credits_Md'] = df_loc_region['Montant_Credits'] / 1e6

                with col_loc1:
                    st.write("**Dépôts par Localité (Md MAD)**")
                    fig_ld = px.bar(
                        df_loc_region.sort_values('Depots_Md', ascending=True),
                        x='Depots_Md',
                        y='Localite',
                        orientation='h',
                        color='Depots_Md',
                        color_continuous_scale='Blues'
                    )
                    fig_ld.update_traces(hovertemplate='%{y}<br>%{x:.2f} Md<extra></extra>')
                    fig_ld.update_layout(height=max(400, len(df_loc_region)*30), showlegend=False, xaxis_title='Md MAD')
                    st.plotly_chart(fig_ld, use_container_width=True)
                
                with col_loc2:
                    st.write("**Crédits par Localité (Md MAD)**")
                    fig_lc = px.bar(
                        df_loc_region.sort_values('Credits_Md', ascending=True),
                        x='Credits_Md',
                        y='Localite',
                        orientation='h',
                        color='Credits_Md',
                        color_continuous_scale='Oranges'
                    )
                    fig_lc.update_traces(hovertemplate='%{y}<br>%{x:.2f} Md<extra></extra>')
                    fig_lc.update_layout(height=max(400, len(df_loc_region)*30), showlegend=False, xaxis_title='Md MAD')
                    st.plotly_chart(fig_lc, use_container_width=True)
                
                # Tableau
                df_loc_display = df_loc_region.copy()
                df_loc_display['Dépôts'] = df_loc_display['Montant_Depots'].apply(lambda x: f"{x/1e6:.2f} Md")
                df_loc_display['Crédits'] = df_loc_display['Montant_Credits'].apply(lambda x: f"{x/1e6:.2f} Md")
                df_loc_display = df_loc_display[['Localite', 'Dépôts', 'Crédits']]
                
                st.dataframe(df_loc_display, use_container_width=True, hide_index=True)
        else:
            st.warning("Colonne 'Direction_Regionale' non disponible")
    
    # =========================================================================
    # TAB 3 : ÉVOLUTION PAR ANNÉE
    # =========================================================================
    
    with tab3:
        st.subheader("Évolution par Année")
        
        st.info("💡 Chaque point représente le DERNIER MOIS de l'année")
        
        df_evol = df_derniers_mois.groupby('Annee').agg({
            'Montant_Depots': 'sum',
            'Montant_Credits': 'sum',
            'mois': 'first'
        }).reset_index().sort_values('Annee')
        
        df_evol['Var_Depots_%'] = df_evol['Montant_Depots'].pct_change() * 100
        df_evol['Var_Credits_%'] = df_evol['Montant_Credits'].pct_change() * 100
        
        # Graphiques évolution
        col_ev1, col_ev2 = st.columns(2)
        
        with col_ev1:
            st.write("**💰 Évolution Dépôts**")
            
            fig1 = go.Figure()
            fig1.add_trace(go.Scatter(
                x=df_evol['Annee'],
                y=df_evol['Montant_Depots']/1e6,
                mode='lines+markers',
                fill='tozeroy',
                line=dict(width=4, color='#1f77b4'),
                marker=dict(size=12),
                text=[f"Mois {int(m)}" for m in df_evol['mois']],
                hovertemplate='<b>%{x}</b><br>Dépôts: %{y:.2f} Md<br>%{text}<extra></extra>'
            ))
            
            fig1.update_layout(height=400, yaxis_title="Md MAD", showlegend=False)
            st.plotly_chart(fig1, use_container_width=True)
        
        with col_ev2:
            st.write("**💳 Évolution Crédits**")
            
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(
                x=df_evol['Annee'],
                y=df_evol['Montant_Credits']/1e6,
                mode='lines+markers',
                fill='tozeroy',
                line=dict(width=4, color='#ff7f0e'),
                marker=dict(size=12),
                text=[f"Mois {int(m)}" for m in df_evol['mois']],
                hovertemplate='<b>%{x}</b><br>Crédits: %{y:.2f} Md<br>%{text}<extra></extra>'
            ))
            
            fig2.update_layout(height=400, yaxis_title="Md MAD", showlegend=False)
            st.plotly_chart(fig2, use_container_width=True)
        
        st.divider()
        
        # Taux de croissance
        st.write("**📈 Taux de Croissance Annuel**")
        
        df_var = df_evol[df_evol['Var_Depots_%'].notna()].copy()
        
        if len(df_var) > 0:
            fig3 = go.Figure()
            
            fig3.add_trace(go.Bar(
                x=df_var['Annee'],
                y=df_var['Var_Depots_%'],
                name='Dépôts',
                marker_color='#1f77b4'
            ))
            
            fig3.add_trace(go.Bar(
                x=df_var['Annee'],
                y=df_var['Var_Credits_%'],
                name='Crédits',
                marker_color='#ff7f0e'
            ))
            
            fig3.update_layout(barmode='group', height=400, yaxis_title="Variation (%)")
            st.plotly_chart(fig3, use_container_width=True)
        
        st.divider()
        
        # Comparaison 2 périodes
        st.write("**🔄 Comparaison entre 2 Périodes**")
        
        st.info("Sélectionnez 2 périodes (Année + Mois)")
        
        col_p1, col_p2 = st.columns(2)
        
        mois_noms = ['Jan','Fév','Mar','Avr','Mai','Jun','Jul','Aoû','Sep','Oct','Nov','Déc']
        
        with col_p1:
            st.write("**Période 1**")
            col_a1, col_m1 = st.columns(2)
            with col_a1:
                annee_p1 = st.selectbox("Année", options=sorted(df_all['Annee'].unique()), key="annee_p1")
            df_a1 = df_all[df_all['Annee'] == annee_p1]
            with col_m1:
                mois_p1 = st.selectbox(
                    "Mois",
                    options=sorted(df_a1['mois'].unique()),
                    format_func=lambda x: mois_noms[int(x)-1] if 1 <= x <= 12 else str(x),
                    key="mois_p1"
                )
        
        with col_p2:
            st.write("**Période 2**")
            col_a2, col_m2 = st.columns(2)
            with col_a2:
                annee_p2 = st.selectbox(
                    "Année",
                    options=sorted(df_all['Annee'].unique()),
                    index=min(len(sorted(df_all['Annee'].unique()))-1, 1),
                    key="annee_p2"
                )
            df_a2 = df_all[df_all['Annee'] == annee_p2]
            with col_m2:
                mois_p2 = st.selectbox(
                    "Mois",
                    options=sorted(df_a2['mois'].unique()),
                    format_func=lambda x: mois_noms[int(x)-1] if 1 <= x <= 12 else str(x),
                    key="mois_p2"
                )
        
        if st.button("Calculer le Taux de Croissance", type="primary", use_container_width=True):
            
            df_per1 = df_all[(df_all['Annee'] == annee_p1) & (df_all['mois'] == mois_p1)]
            d1 = df_per1['Montant_Depots'].sum()
            c1 = df_per1['Montant_Credits'].sum()
            
            df_per2 = df_all[(df_all['Annee'] == annee_p2) & (df_all['mois'] == mois_p2)]
            d2 = df_per2['Montant_Depots'].sum()
            c2 = df_per2['Montant_Credits'].sum()
            
            taux_d = ((d2 - d1) / d1 * 100) if d1 > 0 else 0
            taux_c = ((c2 - c1) / c1 * 100) if c1 > 0 else 0
            
            st.divider()
            
            nom_p1 = f"{mois_noms[int(mois_p1)-1] if 1 <= mois_p1 <= 12 else mois_p1} {annee_p1}"
            nom_p2 = f"{mois_noms[int(mois_p2)-1] if 1 <= mois_p2 <= 12 else mois_p2} {annee_p2}"
            
            st.write(f"**Résultat : {nom_p1} → {nom_p2}**")
            
            col_r1, col_r2, col_r3, col_r4 = st.columns(4)
            
            with col_r1:
                st.metric("Dépôts P1", f"{d1/1e6:.2f} Md")
            with col_r2:
                st.metric("Dépôts P2", f"{d2/1e6:.2f} Md", f"{taux_d:+.2f}%")
            with col_r3:
                st.metric("Crédits P1", f"{c1/1e6:.2f} Md")
            with col_r4:
                st.metric("Crédits P2", f"{c2/1e6:.2f} Md", f"{taux_c:+.2f}%")
            
            st.divider()
            
            fig_comp = go.Figure()
            
            fig_comp.add_trace(go.Bar(
                x=['Dépôts', 'Crédits'],
                y=[d1/1e6, c1/1e6],
                name=nom_p1,
                marker_color='#1f77b4'
            ))
            
            fig_comp.add_trace(go.Bar(
                x=['Dépôts', 'Crédits'],
                y=[d2/1e6, c2/1e6],
                name=nom_p2,
                marker_color='#ff7f0e'
            ))
            
            fig_comp.update_layout(
                barmode='group',
                height=400,
                yaxis_title="Montant (Md MAD)",
                title=f"Comparaison {nom_p1} vs {nom_p2}"
            )
            
            st.plotly_chart(fig_comp, use_container_width=True)
            
            # =========================================================
            # ANALYSE DÉTAILLÉE PAR LOCALITÉ
            # =========================================================
            
            st.divider()
            
            st.write("**📊 Analyse Détaillée : Contribution des Localités à la Croissance**")
            
            # Grouper par localité pour chaque période
            df_loc_p1 = df_per1.groupby('Localite').agg({
                'Montant_Depots': 'sum',
                'Montant_Credits': 'sum'
            }).reset_index()
            
            df_loc_p2 = df_per2.groupby('Localite').agg({
                'Montant_Depots': 'sum',
                'Montant_Credits': 'sum'
            }).reset_index()
            
            # Fusionner les deux périodes
            df_compare_loc = df_loc_p1.merge(
                df_loc_p2,
                on='Localite',
                how='outer',
                suffixes=('_P1', '_P2')
            ).fillna(0)
            
            # Calculer les variations
            df_compare_loc['Variation_Depots'] = df_compare_loc['Montant_Depots_P2'] - df_compare_loc['Montant_Depots_P1']
            df_compare_loc['Variation_Credits'] = df_compare_loc['Montant_Credits_P2'] - df_compare_loc['Montant_Credits_P1']
            
            # Calculer la contribution en % de chaque localité
            variation_totale_depots = d2 - d1
            variation_totale_credits = c2 - c1
            
            if variation_totale_depots != 0:
                df_compare_loc['Contribution_Depots_%'] = (df_compare_loc['Variation_Depots'] / variation_totale_depots * 100)
            else:
                df_compare_loc['Contribution_Depots_%'] = 0
            
            if variation_totale_credits != 0:
                df_compare_loc['Contribution_Credits_%'] = (df_compare_loc['Variation_Credits'] / variation_totale_credits * 100)
            else:
                df_compare_loc['Contribution_Credits_%'] = 0
            
            # Trier par contribution aux dépôts
            df_compare_loc = df_compare_loc.sort_values('Contribution_Depots_%', ascending=False)
            
            # Afficher les top contributeurs
            st.write(f"**🔝 Top 10 Localités Contribuant à la Croissance**")
            
            df_top_contrib = df_compare_loc.head(10).copy()
            
            # Préparer l'affichage
            df_display = pd.DataFrame({
                'Localité': df_top_contrib['Localite'],
                'Variation Dépôts (Md)': df_top_contrib['Variation_Depots'].apply(lambda x: f"{x/1e6:.2f}"),
                'Contribution Dépôts (%)': df_top_contrib['Contribution_Depots_%'].apply(lambda x: f"{x:.2f}%"),
                'Variation Crédits (Md)': df_top_contrib['Variation_Credits'].apply(lambda x: f"{x/1e6:.2f}"),
                'Contribution Crédits (%)': df_top_contrib['Contribution_Credits_%'].apply(lambda x: f"{x:.2f}%")
            })
            
            st.dataframe(df_display, use_container_width=True, hide_index=True)
            
            st.divider()
            
            # Graphiques de contribution
            col_contrib1, col_contrib2 = st.columns(2)
            
            with col_contrib1:
                st.write("**💰 Contribution aux Dépôts**")
                
                fig_contrib_d = px.bar(
                    df_top_contrib,
                    x='Contribution_Depots_%',
                    y='Localite',
                    orientation='h',
                    color='Contribution_Depots_%',
                    color_continuous_scale='RdYlGn',
                    labels={'Contribution_Depots_%': 'Contribution (%)', 'Localite': 'Localité'}
                )
                
                fig_contrib_d.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig_contrib_d, use_container_width=True)
            
            with col_contrib2:
                st.write("**💳 Contribution aux Crédits**")
                
                fig_contrib_c = px.bar(
                    df_top_contrib,
                    x='Contribution_Credits_%',
                    y='Localite',
                    orientation='h',
                    color='Contribution_Credits_%',
                    color_continuous_scale='RdYlGn',
                    labels={'Contribution_Credits_%': 'Contribution (%)', 'Localite': 'Localité'}
                )
                
                fig_contrib_c.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig_contrib_c, use_container_width=True)
            
            st.divider()
            
            # Résumé de l'analyse
            st.write("**📋 Résumé de l'Analyse**")
            
            top_localite_depots = df_top_contrib.iloc[0]['Localite'] if len(df_top_contrib) > 0 else "N/A"
            top_contrib_depots = df_top_contrib.iloc[0]['Contribution_Depots_%'] if len(df_top_contrib) > 0 else 0
            
            top_localite_credits = df_compare_loc.sort_values('Contribution_Credits_%', ascending=False).iloc[0]['Localite'] if len(df_compare_loc) > 0 else "N/A"
            top_contrib_credits = df_compare_loc.sort_values('Contribution_Credits_%', ascending=False).iloc[0]['Contribution_Credits_%'] if len(df_compare_loc) > 0 else 0
            
            st.info(f"""
            **Dépôts :**
            - Taux de croissance global : **{taux_d:+.2f}%**
            - Principale contributrice : **{top_localite_depots}** ({top_contrib_depots:.2f}% de la variation)
            
            **Crédits :**
            - Taux de croissance global : **{taux_c:+.2f}%**
            - Principale contributrice : **{top_localite_credits}** ({top_contrib_credits:.2f}% de la variation)
            """)
    
    
    # =========================================================================
    # TAB 4 : TOP LOCALITÉS
    # =========================================================================
    
    with tab4:
        st.subheader("Top Localités")
        
        st.info("💡 Basé sur les DERNIERS MOIS des années sélectionnées")
        
        annees_dispo_top = sorted(df_derniers_mois['Annee'].unique())
        annees_select_top = st.multiselect(
            "Sélectionnez les années",
            options=annees_dispo_top,
            default=annees_dispo_top,
            key="annees_top"
        )
        
        if not annees_select_top:
            st.warning("Sélectionnez au moins une année")
            return
        
        df_top_filtered = df_derniers_mois[df_derniers_mois['Annee'].isin(annees_select_top)]
        
        top_n = st.slider("Nombre de localités dans le Top", 5, 50, 10, key="topn_slider")
        
        st.divider()
        
        df_loc = df_top_filtered.groupby('Localite').agg({
            'Montant_Depots': 'sum',
            'Montant_Credits': 'sum'
        }).reset_index().sort_values('Montant_Depots', ascending=False)
        
        df_top = df_loc.head(top_n)
        df_reste = df_loc.iloc[top_n:]
        
        col_t1, col_t2 = st.columns(2)
        
        with col_t1:
            st.write(f"**Top {top_n}**")
            d_top = df_top['Montant_Depots'].sum()
            c_top = df_top['Montant_Credits'].sum()
            st.metric("Dépôts", f"{d_top/1e6:.2f} Md")
            st.metric("Crédits", f"{c_top/1e6:.2f} Md")
        
        with col_t2:
            st.write(f"**Reste ({len(df_reste)} localités)**")
            d_reste = df_reste['Montant_Depots'].sum()
            c_reste = df_reste['Montant_Credits'].sum()
            st.metric("Dépôts", f"{d_reste/1e6:.2f} Md")
            st.metric("Crédits", f"{c_reste/1e6:.2f} Md")
        
        st.divider()
        
        # NOUVEAU : Graphiques Dépôts ET Crédits Top N
        st.write(f"**📊 Top {top_n} Localités**")
        
        col_top1, col_top2 = st.columns(2)
        
        with col_top1:
            st.write("**💰 Par Dépôts**")
            fig_td = px.bar(
                df_top.sort_values('Montant_Depots', ascending=True),
                x='Montant_Depots',
                y='Localite',
                orientation='h',
                color='Montant_Depots',
                color_continuous_scale='Blues'
            )
            fig_td.update_layout(height=max(400, top_n*25), showlegend=False)
            st.plotly_chart(fig_td, use_container_width=True)
        
        with col_top2:
            st.write("**💳 Par Crédits**")
            fig_tc = px.bar(
                df_top.sort_values('Montant_Credits', ascending=True),
                x='Montant_Credits',
                y='Localite',
                orientation='h',
                color='Montant_Credits',
                color_continuous_scale='Oranges'
            )
            fig_tc.update_layout(height=max(400, top_n*25), showlegend=False)
            st.plotly_chart(fig_tc, use_container_width=True)
        
        st.divider()
        
        # Graphique Top vs Reste
        st.write("**📊 Top vs Reste**")
        
        fig_vs = go.Figure()
        
        fig_vs.add_trace(go.Bar(
            x=['Dépôts', 'Crédits'],
            y=[d_top/1e6, c_top/1e6],
            name=f'Top {top_n}',
            marker_color='#1f77b4'
        ))
        
        fig_vs.add_trace(go.Bar(
            x=['Dépôts', 'Crédits'],
            y=[d_reste/1e6, c_reste/1e6],
            name=f'Reste ({len(df_reste)})',
            marker_color='#ff7f0e'
        ))
        
        fig_vs.update_layout(barmode='group', height=400, yaxis_title="Montant (Md MAD)")
        st.plotly_chart(fig_vs, use_container_width=True)



# ============================================================================
# MODULE BALANCE - TRAITEMENT FICHIERS TXT CHARGES/PRODUITS
# ============================================================================

import re
from datetime import datetime

def parse_balance_txt(txt_content, type_document="Produits"):
    """
    Parser CORRIGÉ pour fichiers Balance SGMB
    
    LOGIQUE CORRECTE :
    Les comptes détaillés (000 XXXXX) appartiennent au TOP_ACCOUNT qui vient APRÈS eux.
    
    Exemple :
    | 000 0570102  |INT DEBIT...|0,00|4 211,40|...    ← Compte
    |   7023       |- INT.S/... |0,00|4 211,40|...    ← TOP_ACCOUNT pour le compte au-dessus
    | 000 0570550  |INTERETS ...|0,00|15 683,77|...   ← Nouveau compte
    |   7101       |INTERETS ...|0,00|131 787,35|...  ← TOP_ACCOUNT pour les comptes au-dessus
    """
    
    # Nettoyer le contenu
    lines = txt_content.replace('\r', '').split('\n')
    
    data = []
    current_agence_id = None
    current_agence_desc = None
    
    # NOUVEAU : Buffer pour stocker les comptes en attente d'un TOP_ACCOUNT
    pending_comptes = []
    
    for line in lines:
        # ─────────────────────────────────────────────────────────────────
        # 1. Détecter l'agence
        # ─────────────────────────────────────────────────────────────────
        if 'AGENCE' in line and ':' in line:
            match = re.search(r'AGENCE\s*:\s*(\d+)\s+(.+)', line)
            if match:
                current_agence_id = match.group(1).strip()
                current_agence_desc = match.group(2).strip()
                # Réinitialiser le buffer pour une nouvelle agence
                pending_comptes = []
                continue
        
        # ─────────────────────────────────────────────────────────────────
        # 2. Ignorer les lignes non-données
        # ─────────────────────────────────────────────────────────────────
        if '*---' in line or '+---' in line:
            continue
        if 'No DU COMPTE' in line or 'INTITULE DU COMPTE' in line or 'SOLDES' in line:
            continue
        if not line.strip() or len(line.strip()) < 10:
            continue
        if 'TOTAL' in line and 'GENERAL' in line:
            continue
        
        # ─────────────────────────────────────────────────────────────────
        # 3. Parser les lignes avec des pipes |...|
        # ─────────────────────────────────────────────────────────────────
        if '|' in line:
            parts = line.split('|')
            
            if len(parts) < 5:
                continue
            
            try:
                compte = parts[1].strip()
                intitule = parts[2].strip()
                debit = parts[3].strip()
                credit = parts[4].strip() if len(parts) > 4 else "0,00"
            except:
                continue
            
            # ─────────────────────────────────────────────────────────────
            # 4. Identifier le type de ligne
            # ─────────────────────────────────────────────────────────────
            
            # Ligne TOP_ACCOUNT : juste des chiffres (ex: "7023" ou "  7023  ")
            if re.match(r'^\s*\d{4}\s*$', compte):
                top_account = compte.strip()
                top_account_desc = intitule
                
                # NOUVEAU : Assigner ce TOP_ACCOUNT à tous les comptes en attente
                for pending_compte in pending_comptes:
                    pending_compte['TOP_ACCOUNT'] = top_account
                    pending_compte['TOP_ACCOUNT_DESC'] = top_account_desc
                    data.append(pending_compte)
                
                # Vider le buffer
                pending_comptes = []
                continue
            
            # Ligne COMPTE détaillé : commence par "000 " (ex: "000 0570102")
            if re.match(r'^\s*000\s+\d+', compte):
                compte_num = re.sub(r'^\s*000\s+', '', compte).strip()
                
                # Convertir les montants
                try:
                    debit_clean = debit.replace(' ', '').replace(',', '.')
                    credit_clean = credit.replace(' ', '').replace(',', '.')
                    
                    debit_val = float(debit_clean) if debit_clean and debit_clean != '0.00' else 0
                    credit_val = float(credit_clean) if credit_clean and credit_clean != '0.00' else 0
                    
                    if type_document == "Produits":
                        montant = credit_val - debit_val
                    else:
                        montant = debit_val - credit_val
                    
                except Exception as e:
                    montant = 0
                
                # NOUVEAU : Ajouter au buffer (sans TOP_ACCOUNT pour l'instant)
                pending_comptes.append({
                    'ID_AGENCI': current_agence_id,
                    'DESC_AGENCE': current_agence_desc,
                    'ID_ACCOUNT': compte_num,
                    'DESC_ACCOUNT': intitule,
                    'Montants': montant,
                    'TOP_ACCOUNT': None,  # Sera rempli plus tard
                    'TOP_ACCOUNT_DESC': None,  # Sera rempli plus tard
                    'Type': type_document
                })
    
    # NOUVEAU : À la fin, s'il reste des comptes sans TOP_ACCOUNT, les ajouter quand même
    for pending_compte in pending_comptes:
        if pending_compte['TOP_ACCOUNT'] is None:
            pending_compte['TOP_ACCOUNT'] = ''
            pending_compte['TOP_ACCOUNT_DESC'] = ''
        data.append(pending_compte)
    
    # Créer DataFrame
    df = pd.DataFrame(data)
    
    # Nettoyer et convertir
    if len(df) > 0:
        df['Montants'] = pd.to_numeric(df['Montants'], errors='coerce').fillna(0)
        df['ID_AGENCI'] = df['ID_AGENCI'].astype(str)
        df['ID_ACCOUNT'] = df['ID_ACCOUNT'].astype(str)
        df['TOP_ACCOUNT'] = df['TOP_ACCOUNT'].fillna('').astype(str)
    
    print(f"✅ Parser v3 : {len(df)} lignes extraites")
    print(f"   Agences uniques : {df['ID_AGENCI'].nunique() if len(df) > 0 else 0}")
    print(f"   Comptes uniques : {df['ID_ACCOUNT'].nunique() if len(df) > 0 else 0}")
    
    return df


def convert_balance_to_excel(df, filename="Balance_Export.xlsx"):
    """
    Convertit le DataFrame en fichier Excel téléchargeable.
    """
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Balance')
    
    return output.getvalue()


def visualisations_balance(df_produits, df_charges):
    """
    Crée les visualisations pour le module Balance.
    """
    
    st.header("📊 Analyse Balance - Produits & Charges")
    
    # Combiner les deux DataFrames
    df_all = pd.concat([df_produits, df_charges], ignore_index=True)
    
    if len(df_all) == 0:
        st.warning("⚠️ Aucune donnée à visualiser")
        return
    
    # =========================================================================
    # MÉTRIQUES GLOBALES
    # =========================================================================
    
    total_produits = df_produits['Montants'].sum()
    total_charges = df_charges['Montants'].sum()
    resultat_net = total_produits - total_charges
    marge_nette = (resultat_net / total_produits * 100) if total_produits > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💰 Total Produits", f"{total_produits/1e6:.2f} Mrd DH")
    
    with col2:
        st.metric("💸 Total Charges", f"{total_charges/1e6:.2f} Mrd DH")
    
    with col3:
        delta_color = "normal" if resultat_net >= 0 else "inverse"
        st.metric("📈 Résultat Net", f"{resultat_net/1e6:.2f} Mrd DH", delta_color=delta_color)
    
    with col4:
        st.metric("📊 Marge Nette", f"{marge_nette:.2f}%")
    
    st.divider()
    
    # =========================================================================
    # ONGLETS
    # =========================================================================
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Vue Globale",
        "🏦 Analyse par Agence",
        "🎯 Analyse par Compte",
        "📋 Données Détaillées"
    ])
    
    # ─────────────────────────────────────────────────────────────────────────
    # TAB 1 : VUE GLOBALE
    # ─────────────────────────────────────────────────────────────────────────
    
    with tab1:
        st.subheader("Vue d'Ensemble")
        
        # Graphique Produits vs Charges
        col_g1, col_g2 = st.columns(2)
        
        with col_g1:
            st.write("**💰 Produits vs Charges**")
            
            fig_pvc = go.Figure()
            
            fig_pvc.add_trace(go.Bar(
                x=['Produits', 'Charges'],
                y=[total_produits/1e6, total_charges/1e6],
                marker_color=['#2ecc71', '#e74c3c'],
                text=[f"{total_produits/1e6:.2f} Mrd", f"{total_charges/1e6:.2f} Mrd"],
                textposition='outside'
            ))
            
            fig_pvc.update_layout(
                height=400,
                yaxis_title="Montant (Mrd DH)",
                showlegend=False
            )
            
            st.plotly_chart(fig_pvc, use_container_width=True)
        
        with col_g2:
            st.write("**📈 Résultat Net**")
            
            fig_res = go.Figure()
            
            fig_res.add_trace(go.Indicator(
                mode="gauge+number+delta",
                value=resultat_net/1e6,
                title={'text': "Résultat Net (Mrd DH)"},
                delta={'reference': 0},
                gauge={
                    'axis': {'range': [None, total_produits/1e6]},
                    'bar': {'color': "darkgreen" if resultat_net > 0 else "darkred"},
                    'steps': [
                        {'range': [0, total_produits/1e6 * 0.3], 'color': "lightgray"},
                        {'range': [total_produits/1e6 * 0.3, total_produits/1e6 * 0.7], 'color': "gray"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 0
                    }
                }
            ))
            
            fig_res.update_layout(height=400)
            
            st.plotly_chart(fig_res, use_container_width=True)
        
        st.divider()
        
        # Top 10 Comptes Produits et Charges
        st.write("**🔝 Top 10 Comptes**")
        
        col_t1, col_t2 = st.columns(2)
        
        with col_t1:
            st.write("**💰 Top 10 Produits**")
            
            top_produits = df_produits.nlargest(10, 'Montants')[['DESC_ACCOUNT', 'Montants']].copy()
            top_produits['Montants_Mrd'] = top_produits['Montants'] / 1e6
            
            fig_tp = px.bar(
                top_produits.sort_values('Montants_Mrd', ascending=True),
                x='Montants_Mrd',
                y='DESC_ACCOUNT',
                orientation='h',
                color='Montants_Mrd',
                color_continuous_scale='Greens'
            )
            fig_tp.update_traces(hovertemplate='%{y}<br>%{x:.2f} Mrd<extra></extra>')
            fig_tp.update_layout(height=400, showlegend=False, xaxis_title='Montant (Mrd DH)', yaxis_title='')
            
            st.plotly_chart(fig_tp, use_container_width=True)
        
        with col_t2:
            st.write("**💸 Top 10 Charges**")
            
            top_charges = df_charges.nlargest(10, 'Montants')[['DESC_ACCOUNT', 'Montants']].copy()
            top_charges['Montants_Mrd'] = top_charges['Montants'] / 1e6
            
            fig_tc = px.bar(
                top_charges.sort_values('Montants_Mrd', ascending=True),
                x='Montants_Mrd',
                y='DESC_ACCOUNT',
                orientation='h',
                color='Montants_Mrd',
                color_continuous_scale='Reds'
            )
            fig_tc.update_traces(hovertemplate='%{y}<br>%{x:.2f} Mrd<extra></extra>')
            fig_tc.update_layout(height=400, showlegend=False, xaxis_title='Montant (Mrd DH)', yaxis_title='')
            
            st.plotly_chart(fig_tc, use_container_width=True)
    
    # =========================================================================
    # TAB 2 : ANALYSE PAR AGENCE - VERSION AMÉLIORÉE
    # =========================================================================

    with tab2:
        st.subheader("Analyse par Agence")
    
        # Agrégation par agence
        agence_produits = df_produits.groupby(['ID_AGENCI', 'DESC_AGENCE'])['Montants'].sum().reset_index()
        agence_produits.columns = ['ID_AGENCI', 'DESC_AGENCE', 'Produits']
    
        agence_charges = df_charges.groupby(['ID_AGENCI', 'DESC_AGENCE'])['Montants'].sum().reset_index()
        agence_charges.columns = ['ID_AGENCI', 'DESC_AGENCE', 'Charges']
    
        agence_summary = agence_produits.merge(agence_charges, on=['ID_AGENCI', 'DESC_AGENCE'], how='outer').fillna(0)
        agence_summary['Resultat_Net'] = agence_summary['Produits'] - agence_summary['Charges']
        agence_summary['Marge_%'] = (agence_summary['Resultat_Net'] / agence_summary['Produits'] * 100).replace([float('inf'), -float('inf')], 0).fillna(0)
        agence_summary = agence_summary.sort_values('Resultat_Net', ascending=False)
    
    # ─────────────────────────────────────────────────────────────────────
    # MÉTRIQUES GLOBALES
    # ─────────────────────────────────────────────────────────────────────
    
    st.info(f"📊 **{len(agence_summary)} agences** au total")
    
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    
    with col_m1:
        st.metric("Total Produits", f"{agence_summary['Produits'].sum()/1e6:.2f} Mrd")
    with col_m2:
        st.metric("Total Charges", f"{agence_summary['Charges'].sum()/1e6:.2f} Mrd")
    with col_m3:
        st.metric("Résultat Net Total", f"{agence_summary['Resultat_Net'].sum()/1e6:.2f} Mrd")
    with col_m4:
        marge_globale = (agence_summary['Resultat_Net'].sum() / agence_summary['Produits'].sum() * 100)
        st.metric("Marge Globale", f"{marge_globale:.2f}%")
    
    st.divider()
    
    # ─────────────────────────────────────────────────────────────────────
    # OPTIONS DE VISUALISATION
    # ─────────────────────────────────────────────────────────────────────
    
    col_opt1, col_opt2 = st.columns(2)
    
    with col_opt1:
        critere_tri = st.selectbox(
            "Trier par",
            ["Résultat Net", "Produits", "Charges", "Marge %"],
            key="tri_agence"
        )
    
    with col_opt2:
        nb_agences = st.slider(
            "Nombre d'agences à afficher",
            min_value=10,
            max_value=min(100, len(agence_summary)),
            value=20,
            step=5,
            key="nb_agences"
        )
    
    # Mapper le critère de tri
    critere_map = {
        "Résultat Net": "Resultat_Net",
        "Produits": "Produits",
        "Charges": "Charges",
        "Marge %": "Marge_%"
    }
    
    # Trier et sélectionner top N
    agence_top = agence_summary.sort_values(critere_map[critere_tri], ascending=False).head(nb_agences)
    
    st.divider()
    
    # ─────────────────────────────────────────────────────────────────────
    # GRAPHIQUE 1 : BARRES GROUPÉES (TOP N)
    # ─────────────────────────────────────────────────────────────────────
    
    st.write(f"**📊 Top {nb_agences} Agences par {critere_tri}**")
    
    fig_agence = go.Figure()
    
    # Trier pour l'affichage (ascending pour avoir le plus grand en haut)
    agence_plot = agence_top.sort_values(critere_map[critere_tri], ascending=True)
    
    fig_agence.add_trace(go.Bar(
        name='Produits',
        y=agence_plot['DESC_AGENCE'],
        x=agence_plot['Produits']/1e6,
        orientation='h',
        marker_color='#2ecc71',
        hovertemplate='<b>%{y}</b><br>Produits: %{x:.2f} Mrd<extra></extra>'
    ))
    
    fig_agence.add_trace(go.Bar(
        name='Charges',
        y=agence_plot['DESC_AGENCE'],
        x=agence_plot['Charges']/1e6,
        orientation='h',
        marker_color='#e74c3c',
        hovertemplate='<b>%{y}</b><br>Charges: %{x:.2f} Mrd<extra></extra>'
    ))
    
    fig_agence.add_trace(go.Scatter(
        name='Résultat Net',
        y=agence_plot['DESC_AGENCE'],
        x=agence_plot['Resultat_Net']/1e6,
        mode='markers',
        marker=dict(size=10, color='#3498db', symbol='diamond'),
        hovertemplate='<b>%{y}</b><br>Résultat Net: %{x:.2f} Mrd<extra></extra>'
    ))
    
    fig_agence.update_layout(
        barmode='group',
        height=max(500, nb_agences * 25),
        xaxis_title='Montant (Mrd DH)',
        yaxis_title='',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig_agence, use_container_width=True)
    
    st.divider()
    
    # ─────────────────────────────────────────────────────────────────────
    # GRAPHIQUE 2 : TREEMAP (VISION GLOBALE)
    # ─────────────────────────────────────────────────────────────────────
    
    st.write("**🗺️ Vision Globale - Treemap des Produits (Top 30)**")
    
    agence_treemap = agence_summary.nlargest(30, 'Produits')
    
    fig_tree = px.treemap(
        agence_treemap,
        path=['DESC_AGENCE'],
        values='Produits',
        color='Marge_%',
        color_continuous_scale='RdYlGn',
        color_continuous_midpoint=0,
        hover_data={'Produits': ':,.0f', 'Charges': ':,.0f', 'Resultat_Net': ':,.0f', 'Marge_%': ':.2f'}
    )
    
    fig_tree.update_traces(
        textposition='middle center',
        textfont_size=12,
        hovertemplate='<b>%{label}</b><br>Produits: %{value:,.0f} DH<br>Marge: %{color:.2f}%<extra></extra>'
    )
    
    fig_tree.update_layout(height=600)
    
    st.plotly_chart(fig_tree, use_container_width=True)
    
    st.divider()
    
    # ─────────────────────────────────────────────────────────────────────
    # GRAPHIQUE 3 : MARGE PAR AGENCE
    # ─────────────────────────────────────────────────────────────────────
    
    st.write(f"**📈 Marge Nette par Agence (Top {nb_agences})**")
    
    # Filtrer les agences avec produits > 0 pour éviter les marges infinies
    agence_marge = agence_top[agence_top['Produits'] > 0].sort_values('Marge_%', ascending=True)
    
    fig_marge = px.bar(
        agence_marge,
        y='DESC_AGENCE',
        x='Marge_%',
        orientation='h',
        color='Marge_%',
        color_continuous_scale='RdYlGn',
        color_continuous_midpoint=0,
        text='Marge_%'
    )
    
    fig_marge.update_traces(
        texttemplate='%{text:.1f}%',
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Marge: %{x:.2f}%<extra></extra>'
    )
    
    fig_marge.update_layout(
        height=max(500, len(agence_marge) * 25),
        xaxis_title='Marge Nette (%)',
        yaxis_title='',
        showlegend=False
    )
    
    st.plotly_chart(fig_marge, use_container_width=True)
    
    st.divider()
    
    # ─────────────────────────────────────────────────────────────────────
    # TABLEAU RÉCAPITULATIF COMPLET
    # ─────────────────────────────────────────────────────────────────────
    
    st.write("**📋 Tableau Récapitulatif - Toutes les Agences**")
    
    # Filtres pour le tableau
    col_f1, col_f2 = st.columns(2)
    
    with col_f1:
        filtre_nom = st.text_input(
            "🔍 Rechercher une agence",
            placeholder="Tapez le nom de l'agence...",
            key="filtre_agence_nom"
        )
    
    with col_f2:
        filtre_min_produits = st.number_input(
            "Produits minimum (Millions DH)",
            min_value=0.0,
            value=0.0,
            step=1.0,
            key="filtre_min_prod"
        )
    
    # Appliquer les filtres
    agence_filtered = agence_summary.copy()
    
    if filtre_nom:
        agence_filtered = agence_filtered[
            agence_filtered['DESC_AGENCE'].str.contains(filtre_nom, case=False, na=False)
        ]
    
    if filtre_min_produits > 0:
        agence_filtered = agence_filtered[agence_filtered['Produits'] >= filtre_min_produits * 1e6]
    
    # Affichage
    st.write(f"**{len(agence_filtered)} agences** affichées (sur {len(agence_summary)} total)")
    
    agence_display = agence_filtered.copy()
    agence_display['Produits'] = agence_display['Produits'].apply(lambda x: f"{x/1e6:.2f} Mrd")
    agence_display['Charges'] = agence_display['Charges'].apply(lambda x: f"{x/1e6:.2f} Mrd")
    agence_display['Resultat_Net'] = agence_display['Resultat_Net'].apply(lambda x: f"{x/1e6:.2f} Mrd")
    agence_display['Marge_%'] = agence_display['Marge_%'].apply(lambda x: f"{x:.2f}%")
    agence_display = agence_display[['DESC_AGENCE', 'Produits', 'Charges', 'Resultat_Net', 'Marge_%']]
    agence_display.columns = ['Agence', 'Produits', 'Charges', 'Résultat Net', 'Marge (%)']
    
    st.dataframe(agence_display, use_container_width=True, hide_index=True, height=400)
    
    # Export
    st.divider()
    
    excel_agence = convert_balance_to_excel(agence_filtered)
    st.download_button(
        label="📥 Télécharger tableau des agences (Excel)",
        data=excel_agence,
        file_name=f"Balance_Agences_{datetime.now().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # ─────────────────────────────────────────────────────────────────────────
    # TAB 3 : ANALYSE PAR COMPTE (TOP_ACCOUNT)
    # ─────────────────────────────────────────────────────────────────────────
    
    with tab3:
        st.subheader("Analyse par Catégorie de Compte (TOP_ACCOUNT)")
        
        # Filtre Type
        type_analyse = st.radio(
            "Type d'analyse",
            ["Produits", "Charges", "Les deux"],
            horizontal=True
        )
        
        if type_analyse == "Produits":
            df_analyse = df_produits
        elif type_analyse == "Charges":
            df_analyse = df_charges
        else:
            df_analyse = df_all
        
        # Agrégation par TOP_ACCOUNT
        top_summary = df_analyse.groupby(['TOP_ACCOUNT', 'TOP_ACCOUNT_DESC', 'Type'])['Montants'].sum().reset_index()
        top_summary = top_summary.sort_values('Montants', ascending=False)
        
        # Graphique
        st.write(f"**📊 Répartition par Catégorie de Compte**")
        
        fig_top = px.bar(
            top_summary.head(15).sort_values('Montants', ascending=True),
            x='Montants',
            y='TOP_ACCOUNT_DESC',
            orientation='h',
            color='Type',
            color_discrete_map={'Produits': '#2ecc71', 'Charges': '#e74c3c'}
        )
        fig_top.update_traces(hovertemplate='%{y}<br>%{x:,.0f} DH<extra></extra>')
        fig_top.update_layout(height=500, xaxis_title='Montant (DH)', yaxis_title='')
        
        st.plotly_chart(fig_top, use_container_width=True)
        
        st.divider()
        
        # Tableau
        st.write("**📋 Détail par TOP_ACCOUNT**")
        
        top_display = top_summary.copy()
        top_display['Montants'] = top_display['Montants'].apply(lambda x: f"{x/1e6:.2f} Mrd")
        top_display = top_display[['TOP_ACCOUNT', 'TOP_ACCOUNT_DESC', 'Type', 'Montants']]
        top_display.columns = ['Code', 'Description', 'Type', 'Montant']
        
        st.dataframe(top_display, use_container_width=True, hide_index=True)
    
    # ─────────────────────────────────────────────────────────────────────────
    # TAB 4 : DONNÉES DÉTAILLÉES
    # ─────────────────────────────────────────────────────────────────────────
    
    with tab4:
        st.subheader("Données Détaillées")
        
        # Filtres
        col_f1, col_f2, col_f3 = st.columns(3)
        
        with col_f1:
            type_filtre = st.selectbox(
                "Type",
                ["Tous", "Produits", "Charges"]
            )
        
        with col_f2:
            agences_list = ['Toutes'] + sorted(df_all['DESC_AGENCE'].unique().tolist())
            agence_filtre = st.selectbox(
                "Agence",
                agences_list
            )
        
        with col_f3:
            top_list = ['Tous'] + sorted(df_all['TOP_ACCOUNT'].dropna().unique().tolist())
            top_filtre = st.selectbox(
                "TOP_ACCOUNT",
                top_list
            )
        
        # Appliquer les filtres
        df_filtered = df_all.copy()
        
        if type_filtre != "Tous":
            df_filtered = df_filtered[df_filtered['Type'] == type_filtre]
        
        if agence_filtre != "Toutes":
            df_filtered = df_filtered[df_filtered['DESC_AGENCE'] == agence_filtre]
        
        if top_filtre != "Tous":
            df_filtered = df_filtered[df_filtered['TOP_ACCOUNT'] == top_filtre]
        
        # Afficher
        st.write(f"**{len(df_filtered):,} lignes**".replace(',', ' '))
        
        df_display = df_filtered.copy()
        df_display['Montants'] = df_display['Montants'].apply(lambda x: f"{x:,.2f} DH".replace(',', ' '))
        df_display = df_display[['ID_AGENCI', 'DESC_AGENCE', 'ID_ACCOUNT', 'DESC_ACCOUNT', 
                                  'Montants', 'TOP_ACCOUNT', 'TOP_ACCOUNT_DESC', 'Type']]
        df_display.columns = ['ID Agence', 'Agence', 'ID Compte', 'Description Compte', 
                               'Montant', 'TOP_ACCOUNT', 'Catégorie', 'Type']
        
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        # Export
        st.divider()
        
        excel_data = convert_balance_to_excel(df_filtered)
        
        st.download_button(
            label="📥 Télécharger les données filtrées (Excel)",
            data=excel_data,
            file_name=f"Balance_Filtree_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )


def balance_module():
    """
    Module principal Balance - Import et Analyse Produits/Charges
    """
    
    st.markdown(f"""
    <div class="main-header">
        <h1>📊 Module Balance</h1>
        <p style='font-size: 1.2em; margin-top: 1rem;'>
            Traitement automatique des fichiers Balance (Produits & Charges)
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # =========================================================================
    # ONGLETS PRINCIPAUX
    # =========================================================================
    
    tab1, tab2 = st.tabs([
        "📂 Import Balance",
        "📊 Visualisations"
    ])
    
    # ─────────────────────────────────────────────────────────────────────────
    # TAB 1 : IMPORT
    # ─────────────────────────────────────────────────────────────────────────
    
    with tab1:
        st.subheader("📂 Import Fichiers Balance")
        
        st.markdown("""
        <div class="info-box">
            <h4>📋 Instructions</h4>
            <ul>
                <li>Uploadez deux fichiers TXT : un pour les <strong>Produits</strong> et un pour les <strong>Charges</strong></li>
                <li>Format attendu : Balance Générale SGMB (format standard)</li>
                <li>Les fichiers seront automatiquement parsés et convertis en Excel</li>
                <li>Les visualisations seront disponibles dans l'onglet suivant</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        col1, col2 = st.columns(2)
        
        # ─────────────────────────────────────────────────────────────────────
        # UPLOAD PRODUITS
        # ─────────────────────────────────────────────────────────────────────
        
        with col1:
            st.markdown("### 💰 Fichier Produits")
            
            fichier_produits = st.file_uploader(
                "Sélectionnez le fichier TXT des Produits",
                type=['txt'],
                key="fichier_produits"
            )
            
            if fichier_produits:
                try:
                    with st.spinner("⏳ Traitement du fichier Produits..."):
                        # Lire le contenu
                        content = fichier_produits.read().decode('utf-8', errors='ignore')
                        
                        # Parser
                        df_produits = parse_balance_txt(content, type_document="Produits")
                        
                        st.success(f"✅ **{len(df_produits):,} lignes** extraites".replace(',', ' '))
                        
                        # Stocker dans session_state
                        st.session_state.balance_produits = df_produits
                        
                        # Métriques
                        total_produits = df_produits['Montants'].sum()
                        nb_agences = df_produits['ID_AGENCI'].nunique()
                        nb_comptes = df_produits['ID_ACCOUNT'].nunique()
                        
                        col_m1, col_m2, col_m3 = st.columns(3)
                        with col_m1:
                            st.metric("Total", f"{total_produits/1e6:.2f} Mrd")
                        with col_m2:
                            st.metric("Agences", nb_agences)
                        with col_m3:
                            st.metric("Comptes", nb_comptes)
                        
                        # Aperçu
                        with st.expander("🔍 Aperçu des données", expanded=False):
                            st.dataframe(df_produits.head(20), use_container_width=True)
                        
                        # Export Excel
                        excel_produits = convert_balance_to_excel(df_produits, "Produits.xlsx")
                        st.download_button(
                            label="📥 Télécharger Excel Produits",
                            data=excel_produits,
                            file_name=f"Balance_Produits_{datetime.now().strftime('%Y%m%d')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                        
                except Exception as e:
                    st.error(f"❌ Erreur lors du traitement : {str(e)}")
                    st.exception(e)
        
        # ─────────────────────────────────────────────────────────────────────
        # UPLOAD CHARGES
        # ─────────────────────────────────────────────────────────────────────
        
        with col2:
            st.markdown("### 💸 Fichier Charges")
            
            fichier_charges = st.file_uploader(
                "Sélectionnez le fichier TXT des Charges",
                type=['txt'],
                key="fichier_charges"
            )
            
            if fichier_charges:
                try:
                    with st.spinner("⏳ Traitement du fichier Charges..."):
                        # Lire le contenu
                        content = fichier_charges.read().decode('utf-8', errors='ignore')
                        
                        # Parser
                        df_charges = parse_balance_txt(content, type_document="Charges")
                        
                        st.success(f"✅ **{len(df_charges):,} lignes** extraites".replace(',', ' '))
                        
                        # Stocker dans session_state
                        st.session_state.balance_charges = df_charges
                        
                        # Métriques
                        total_charges = df_charges['Montants'].sum()
                        nb_agences = df_charges['ID_AGENCI'].nunique()
                        nb_comptes = df_charges['ID_ACCOUNT'].nunique()
                        
                        col_m1, col_m2, col_m3 = st.columns(3)
                        with col_m1:
                            st.metric("Total", f"{total_charges/1e6:.2f} Mrd")
                        with col_m2:
                            st.metric("Agences", nb_agences)
                        with col_m3:
                            st.metric("Comptes", nb_comptes)
                        
                        # Aperçu
                        with st.expander("🔍 Aperçu des données", expanded=False):
                            st.dataframe(df_charges.head(20), use_container_width=True)
                        
                        # Export Excel
                        excel_charges = convert_balance_to_excel(df_charges, "Charges.xlsx")
                        st.download_button(
                            label="📥 Télécharger Excel Charges",
                            data=excel_charges,
                            file_name=f"Balance_Charges_{datetime.now().strftime('%Y%m%d')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                        
                except Exception as e:
                    st.error(f"❌ Erreur lors du traitement : {str(e)}")
                    st.exception(e)
    
    # ─────────────────────────────────────────────────────────────────────────
    # TAB 2 : VISUALISATIONS
    # ─────────────────────────────────────────────────────────────────────────
    
    with tab2:
        if 'balance_produits' not in st.session_state or 'balance_charges' not in st.session_state:
            st.warning("⚠️ Veuillez d'abord importer les fichiers Produits et Charges dans l'onglet **Import Balance**")
        else:
            df_produits = st.session_state.balance_produits
            df_charges = st.session_state.balance_charges
            
            visualisations_balance(df_produits, df_charges)




def bam_module():
    st.markdown(f"""
    <div class="main-header">
        <h1>SAHAM BANK - Module BAM</h1>
        <p style="font-size: 1.2em;">Bienvenue, <strong>{st.session_state.username}</strong></p>
        <p style="font-size: 0.9em; opacity: 0.9;">Analyse des Données Bancaires</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation
    page = st.sidebar.radio(
        "Navigation",
        ["Import & Traitement", "Visualisations BAM", "Visualisations Saham Bank", "À propos"]
    )
    
    st.sidebar.divider()
    if st.session_state.uploaded_files_bam:
        st.sidebar.metric("Fichiers", len(st.session_state.uploaded_files_bam))
    if st.session_state.combined_data_bam is not None:
        st.sidebar.metric("Lignes", len(st.session_state.combined_data_bam))
    
    st.sidebar.divider()
    if st.sidebar.button("Retour au Menu Principal"):
        st.session_state.selected_module = None
        st.rerun()
    
# NOUVELLE PAGE IMPORT & TRAITEMENT AVEC 2 ONGLETS
# À intégrer dans app_saham_final.py

    if page == "Import & Traitement":
        st.header("Import & Traitement des Données")
        
        # ONGLETS POUR SÉPARER BAM ET SAHAM BANK
        tab1, tab2 = st.tabs(["📊 Import BAM", "🏦 Import Saham Bank"])
        
        # =====================================================================
        # =====================================================================
        # ONGLET 1 : IMPORT BAM MULTI-ANNÉES
        # =====================================================================
        with tab1:
            import_bam_multi_annees()
        
        # ONGLET 2 : IMPORT SAHAM BANK
        # =====================================================================
        with tab2:
            st.subheader("Importation des Données Saham Bank")
            
            st.markdown("""
            <div class="info-box">
                <h4>Instructions</h4>
                <ul>
                    <li><strong>Fichier 1 :</strong> Référentiel agences (Code Agence, Code Localité, Localité)</li>
                    <li><strong>Fichier 2 :</strong> Données financières (Période, Code Agence, Dépôts, Crédits)</li>
                    <li>La PDM sera calculée en utilisant les totaux BAM comme référence nationale</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            # Upload des fichiers
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 1️⃣ Référentiel Agences")
                ref_file = st.file_uploader(
                    "Fichier Excel",
                    type=['xlsx', 'xls'],
                    key="ref_file_tab",
                    help="Colonnes attendues : Code Agence, Code Localité, Localité"
                )
                
                if ref_file:
                    try:
                        df_ref = pd.read_excel(ref_file)
                        st.success(f"✅ {len(df_ref)} agences chargées")
                        st.session_state.saham_referentiel = df_ref
                        
                        with st.expander("Aperçu du référentiel"):
                            st.dataframe(df_ref.head(10))
                    except Exception as e:
                        st.error(f"Erreur : {str(e)}")
            
            with col2:
                st.markdown("### 2️⃣ Données Financières")
                fin_file = st.file_uploader(
                    "Fichier Excel",
                    type=['xlsx', 'xls'],
                    key="fin_file_tab",
                    help="Colonnes attendues : Période, Code Agence, Dépôts, Crédits"
                )
                
                if fin_file:
                    try:
                        df_fin = pd.read_excel(fin_file)
                        st.success(f"✅ {len(df_fin)} lignes chargées")
                        st.session_state.saham_financial = df_fin
                        
                        with st.expander("Aperçu des données"):
                            st.dataframe(df_fin.head(10))
                    except Exception as e:
                        st.error(f"Erreur : {str(e)}")
            
            st.divider()
            
            # Bouton de traitement
            if st.session_state.saham_referentiel is not None and st.session_state.saham_financial is not None:
                
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    if st.button("🔄 Traiter et Agréger Saham Bank", type="primary", use_container_width=True, key="traiter_saham"):
                        with st.spinner("Jointure et agrégation en cours..."):
                            try:
                                # Jointure et agrégation
                                df_agg = join_and_aggregate_saham(
                                    st.session_state.saham_financial,
                                    st.session_state.saham_referentiel
                                )
                                
                                # Recalculer PDM avec totaux BAM si disponibles
                                if hasattr(st.session_state, 'total_depots_bam') and st.session_state.total_depots_bam is not None:
                                    st.info("📊 Utilisation des totaux BAM pour calculer la PDM")
                                    # PDM = (Dépôts Localité Saham / Total Dépôts BAM) × 100
                                    df_agg['PDM'] = (df_agg['Depots'] / st.session_state.total_depots_bam) * 100
                                else:
                                    st.warning("⚠️ Totaux BAM non disponibles. PDM calculée sur base Saham uniquement.")
                                
                                st.session_state.saham_aggregated = df_agg
                                
                                st.success(f"✅ Données agrégées : {len(df_agg)} localités")
                                st.rerun()
                                
                            except Exception as e:
                                st.error(f"Erreur lors du traitement : {str(e)}")
                                st.exception(e)
            
            # Afficher les résultats Saham
            if st.session_state.saham_aggregated is not None:
                
                st.divider()
                st.success("✅ Données Saham Bank prêtes")
                
                df_saham = st.session_state.saham_aggregated
                
                # Métriques
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    total_depots_saham = df_saham['Depots'].sum()
                    st.metric("Total Dépôts Saham", f"{total_depots_saham/1e6:.2f} Md")
                
                with col2:
                    total_credits_saham = df_saham['Credits'].sum()
                    st.metric("Total Crédits Saham", f"{total_credits_saham/1e6:.2f} Md")
                
                with col3:
                    pdm_globale = df_saham['PDM'].sum()
                    st.metric("PDM Globale", f"{pdm_globale:.2f}%")
                
                with col4:
                    nb_localites = df_saham['Localite'].nunique()
                    st.metric("Localités", nb_localites)
                
                # Aperçu
                st.divider()
                st.subheader("Aperçu des Données Agrégées")
                st.dataframe(df_saham.head(20), use_container_width=True)
            
            else:
                if st.session_state.saham_referentiel is None or st.session_state.saham_financial is None:
                    st.info("👆 Veuillez charger les 2 fichiers Excel ci-dessus")
    
    # PAGE VISUALISATIONS BAM
    elif page == "Visualisations BAM":
        if st.session_state.combined_data_bam is not None:
            visualisations_bam_avancees()
        else:
            st.warning("Veuillez d'abord importer et traiter des données BAM")
    
    # PAGE VISUALISATIONS SAHAM BANK
    elif page == "Visualisations Saham Bank":
        create_saham_visualizations()
    
    # PAGE À PROPOS
    elif page == "À propos":
        st.header("À propos")
        st.markdown("""
        ### SAHAM BANK - Module BAM
        
        **Projet de Fin d'Études - 2026**
        
        #### Fonctionnalités :
        - Import multiple de fichiers Excel
        - Combinaison automatique avec mois
        - Détection des valeurs manquantes
        - Visualisations interactives
        - Analyses par Direction Régionale et Localité
        
        **Direction Financière de Saham Bank**  
        *Version 3.0 - Février 2026*
        """)

def main():
    # État 1 : Page d'accueil (sans logo)
    if st.session_state.show_welcome:
        welcome_page()
    # État 2 : Page de connexion
    elif not st.session_state.authenticated:
        login_page()
    # État 3 : Sélection du module
    elif st.session_state.selected_module is None:
        module_selection_page()
    # État 4 : Module BAM
    elif st.session_state.selected_module == "BAM":
        bam_module()
    # État 5 : Module Balance
    elif st.session_state.selected_module == "Balance":
        balance_module()

if __name__ == "__main__":
    main()
