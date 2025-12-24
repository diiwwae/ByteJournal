import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from api_client import APIClient
from utils import (
    format_datetime, 
    format_date, 
    validate_username, 
    validate_password,
    validate_article_title,
    validate_article_body,
    validate_comment_content,
    truncate_text
)

# Page configuration
st.set_page_config(
    page_title="ByteJournal - Web Demonstrator",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize API Client
if "api_client" not in st.session_state:
    st.session_state.api_client = APIClient()

if "user" not in st.session_state:
    st.session_state.user = None

if "page" not in st.session_state:
    st.session_state.page = "home"

# Sidebar navigation
def sidebar():
    st.sidebar.title("ByteJournal 📝")
    
    if st.session_state.user:
        st.sidebar.success(f"Вы вошли как: **{st.session_state.user['username']}**")
        if st.sidebar.button("Выйти"):
            st.session_state.api_client.clear_token()
            st.session_state.user = None
            st.session_state.page = "home"
            st.rerun()
    else:
        st.sidebar.info("Вы не авторизованы")
        if st.sidebar.button("Войти / Регистрация"):
            st.session_state.page = "auth"
            st.rerun()

    st.sidebar.divider()
    
    pages = {
        "home": "🏠 Главная",
        "articles": "📰 Статьи",
        "stats": "📊 Статистика",
    }
    
    if st.session_state.user:
        pages["create_article"] = "✍️ Написать статью"

    for page_id, page_name in pages.items():
        if st.sidebar.button(page_name, use_container_width=True):
            st.session_state.page = page_id
            st.rerun()

def show_auth():
    st.title("Авторизация / Регистрация")
    
    tab1, tab2 = st.tabs(["Вход", "Регистрация"])
    
    with tab1:
        with st.form("login_form"):
            username = st.text_input("Имя пользователя")
            password = st.text_input("Пароль", type="password")
            submit = st.form_submit_button("Войти")
            
            if submit:
                is_valid_u, err_u = validate_username(username)
                is_valid_p, err_p = validate_password(password)
                
                if not is_valid_u:
                    st.error(err_u)
                elif not is_valid_p:
                    st.error(err_p)
                else:
                    try:
                        result = st.session_state.api_client.login(username, password)
                        st.session_state.user = st.session_state.api_client.get_current_user()
                        st.success("Успешный вход!")
                        st.session_state.page = "home"
                        st.rerun()
                    except Exception as e:
                        st.error(f"Ошибка: {str(e)}")

    with tab2:
        with st.form("register_form"):
            username = st.text_input("Имя пользователя")
            password = st.text_input("Пароль", type="password")
            confirm_password = st.text_input("Подтвердите пароль", type="password")
            submit = st.form_submit_button("Зарегистрироваться")
            
            if submit:
                if password != confirm_password:
                    st.error("Пароли не совпадают")
                else:
                    is_valid_u, err_u = validate_username(username)
                    is_valid_p, err_p = validate_password(password)
                    
                    if not is_valid_u:
                        st.error(err_u)
                    elif not is_valid_p:
                        st.error(err_p)
                    else:
                        try:
                            st.session_state.api_client.register(username, password)
                            st.success("Регистрация успешна! Теперь вы можете войти.")
                        except Exception as e:
                            st.error(f"Ошибка: {str(e)}")

def show_home():
    st.title("Добро пожаловать в ByteJournal!")
    st.markdown("""
    Это демонстрационное приложение для платформы микроблогинга.
    
    Здесь вы можете:
    - Читать интересные статьи
    - Комментировать и ставить лайки
    - Просматривать статистику популярности
    - Публиковать свой контент (после регистрации)
    """)
    
    st.divider()
    st.subheader("Последние статьи")
    
    try:
        response = st.session_state.api_client.list_articles(limit=5)
        articles = response.get("articles", [])
        if articles:
            for art in articles:
                with st.container():
                    st.subheader(art['title'])
                    st.write(f"Автор: {art.get('author_username', 'Неизвестен')} | {format_datetime(art['created_at'])}")
                    st.write(truncate_text(art['body'], 150))
                    if st.button("Читать далее...", key=f"btn_{art['id']}"):
                        st.session_state.selected_article_id = art['id']
                        st.session_state.page = "article_view"
                        st.rerun()
                    st.divider()
        else:
            st.info("Статей пока нет.")
    except Exception as e:
        st.error(f"Ошибка при загрузке статей: {str(e)}")

def show_articles():
    st.title("Все статьи")
    
    try:
        response = st.session_state.api_client.list_articles(limit=50)
        articles = response.get("articles", [])
        if articles:
            for art in articles:
                with st.expander(f"{art['title']} (от {art.get('author_username', 'Неизвестен')})"):
                    st.write(f"Опубликовано: {format_datetime(art['created_at'])}")
                    st.write(truncate_text(art['body'], 300))
                    if st.button("Открыть полностью", key=f"all_btn_{art['id']}"):
                        st.session_state.selected_article_id = art['id']
                        st.session_state.page = "article_view"
                        st.rerun()
        else:
            st.info("Статей пока нет.")
    except Exception as e:
        st.error(f"Ошибка при загрузке статей: {str(e)}")

def show_article_view():
    article_id = st.session_state.get("selected_article_id")
    if not article_id:
        st.session_state.page = "articles"
        st.rerun()
        
    try:
        article = st.session_state.api_client.get_article(article_id)
        stats = st.session_state.api_client.get_article_stats(article_id)
        
        st.title(article['title'])
        st.write(f"**Автор:** {article.get('author_username', 'Неизвестен')} | **Дата:** {format_datetime(article['created_at'])}")
        
        st.divider()
        st.markdown(article['body'])
        st.divider()
        
        # Actions and Stats
        col1, col2 = st.columns([1, 2])
        with col1:
            likes_count = stats.get('likes_count', 0)
            is_liked = stats.get('is_liked', False)
            btn_label = f"❤️ {likes_count} Лайков" if not is_liked else f"💖 {likes_count} Вы лайкнули"
            if st.button(btn_label):
                if st.session_state.user:
                    try:
                        st.session_state.api_client.toggle_like(article_id)
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))
                else:
                    st.warning("Войдите, чтобы ставить лайки")
        
        with col2:
            st.write(f"💬 Комментариев: {stats.get('comments_count', 0)}")

        # Comments
        st.subheader("Комментарии")
        
        if st.session_state.user:
            with st.form("comment_form"):
                content = st.text_area("Оставить комментарий", height=100)
                submit = st.form_submit_button("Отправить")
                if submit:
                    is_valid, err = validate_comment_content(content)
                    if is_valid:
                        try:
                            st.session_state.api_client.create_comment(article_id, content)
                            st.success("Комментарий добавлен!")
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))
                    else:
                        st.error(err)
        
        comments_resp = st.session_state.api_client.get_article_comments(article_id)
        comments = comments_resp.get("comments", [])
        
        if comments:
            for comment in comments:
                with st.container():
                    st.write(f"**{comment.get('username', 'Неизвестен')}** ({format_datetime(comment['created_at'])})")
                    st.write(comment['content'])
                    st.divider()
        else:
            st.info("Комментариев пока нет.")
            
    except Exception as e:
        st.error(f"Ошибка при загрузке статьи: {str(e)}")
        if st.button("Назад к списку"):
            st.session_state.page = "articles"
            st.rerun()

def show_create_article():
    if not st.session_state.user:
        st.warning("Только авторизованные пользователи могут создавать статьи.")
        if st.button("Перейти к входу"):
            st.session_state.page = "auth"
            st.rerun()
        return

    st.title("Создание новой статьи")
    
    with st.form("create_article_form"):
        title = st.text_input("Заголовок")
        body = st.text_area("Текст статьи", height=300)
        submit = st.form_submit_button("Опубликовать")
        
        if submit:
            is_valid_t, err_t = validate_article_title(title)
            is_valid_b, err_b = validate_article_body(body)
            
            if not is_valid_t:
                st.error(err_t)
            elif not is_valid_b:
                st.error(err_b)
            else:
                try:
                    result = st.session_state.api_client.create_article(title, body)
                    st.success("Статья успешно опубликована!")
                    st.session_state.selected_article_id = result['id']
                    st.session_state.page = "article_view"
                    st.rerun()
                except Exception as e:
                    st.error(f"Ошибка: {str(e)}")

def show_stats():
    st.title("Статистика платформы")
    
    try:
        # Author stats
        authors_resp = st.session_state.api_client.get_author_stats()
        authors = authors_resp.get("authors", [])
        if authors:
            st.subheader("Топ авторов по количеству статей")
            df_authors = pd.DataFrame(authors)
            fig_authors = px.bar(
                df_authors, 
                x="author_username", 
                y="total_articles",
                labels={"author_username": "Автор", "total_articles": "Количество статей"},
                title="Количество статей по авторам"
            )
            st.plotly_chart(fig_authors, use_container_width=True)
            
            st.subheader("Популярность авторов (общее количество статей)")
            fig_pie = px.pie(
                df_authors, 
                values="total_articles", 
                names="author_username",
                title="Распределение статей между авторами"
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        # Report
        st.divider()
        st.subheader("Отчет по активности авторов")
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Начало периода", value=datetime(2024, 1, 1))
        with col2:
            end_date = st.date_input("Конец периода", value=datetime.now())
            
        if st.button("Получить отчет"):
            report_resp = st.session_state.api_client.get_article_report(
                start_date.isoformat(), 
                end_date.isoformat()
            )
            report = report_resp.get("report", [])
            if report:
                df_report = pd.DataFrame(report)
                st.dataframe(df_report, use_container_width=True)
                
                # Visualizing report data
                if "articles_count" in df_report.columns:
                    fig_report = px.bar(
                        df_report, 
                        x="author_username", 
                        y="articles_count",
                        title="Количество статей за период",
                        color="avg_article_length",
                        labels={"author_username": "Автор", "articles_count": "Статей", "avg_article_length": "Ср. длина"}
                    )
                    st.plotly_chart(fig_report, use_container_width=True)
            else:
                st.info("За указанный период данных не найдено.")
                
    except Exception as e:
        st.error(f"Ошибка при загрузке статистики: {str(e)}")

# Main app logic
sidebar()

if st.session_state.page == "home":
    show_home()
elif st.session_state.page == "auth":
    show_auth()
elif st.session_state.page == "articles":
    show_articles()
elif st.session_state.page == "article_view":
    show_article_view()
elif st.session_state.page == "create_article":
    show_create_article()
elif st.session_state.page == "stats":
    show_stats()

