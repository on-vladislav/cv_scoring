import streamlit as st
from openai import OpenAI
from parse_hh import get_html, extract_vacancy_data, extract_resume_data
import os

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])


SYSTEM_PROMPT = """
Проскорь кандидата, насколько он подходит для данной вакансии.
Сначала напиши короткий анализ, который будет пояснять оценку.
Отдельно оцени качество заполнения резюме (понятно ли, с какими задачами сталкивался кандидат и каким образом их решал?).
Эта оценка должна учитываться при выставлении финальной оценки.
Потом представь результат в виде оценки от 1 до 10.
""".strip()


def request_gpt(system_prompt, user_prompt):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=1000,
        temperature=0,
    )
    return response.choices[0].message.content


st.title("CV Scoring App")

job_url = st.text_input("Ссылка на вакансию hh.ru")
resume_url = st.text_input("Ссылка на резюме hh.ru")

if st.button("Проанализировать соответствие"):
    with st.spinner("Анализируем данные ..."):
        try:
            if not job_url or not resume_url:
                st.error("Вставь обе ссылки: и на вакансию, и на резюме.")
                st.stop()

            job_html = get_html(job_url)
            resume_html = get_html(resume_url)

            job_text = extract_vacancy_data(job_html)
            resume_text = extract_resume_data(resume_html)

            prompt = f"# ВАКАНСИЯ\n{job_text}\n\n# РЕЗЮМЕ\n{resume_text}"
            response = request_gpt(SYSTEM_PROMPT, prompt)

            st.subheader("📊 Результат анализа:")
            st.markdown(response)

        except Exception as e:
            st.error(f"Произошла ошибка: {e}")
