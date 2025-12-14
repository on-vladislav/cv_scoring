import requests
from bs4 import BeautifulSoup


def get_html(url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    }
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.text


def extract_vacancy_data(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    def q(css: str, default="Не найдено") -> str:
        el = soup.select_one(css)
        return el.get_text(" ", strip=True) if el else default

    title = q("h1")
    salary = q('[data-qa="vacancy-salary"]')
    company = q('[data-qa="vacancy-company-name"]')

    desc_el = soup.select_one('[data-qa="vacancy-description"]')
    description_text = desc_el.get_text("\n", strip=True) if desc_el else "Описание не найдено"

    md = []
    md.append(f"# {title}")
    md.append(f"**Компания:** {company}")
    md.append(f"**Зарплата:** {salary}")
    md.append("## Описание")
    md.append(description_text)
    return "\n\n".join(md).strip()


def extract_resume_data(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    def q(css: str, default="Не найдено") -> str:
        el = soup.select_one(css)
        return el.get_text(" ", strip=True) if el else default

    # В резюме hh структура плавает, но data-qa обычно стабильнее
    name = q('[data-qa="resume-personal-name"], h2[data-qa="bloko-header-1"], h2')
    location = q('[data-qa="resume-personal-address"]')
    job_title = q('[data-qa="resume-block-title-position"]')
    job_status = q('[data-qa="job-search-status"]')

    # Пол/возраст лучше не брать первым <p>, он часто не тот.
    gender_age = q('[data-qa="resume-personal-gender"], [data-qa="resume-personal-age"]', default="")

    experiences = []
    exp_section = soup.select_one('[data-qa="resume-block-experience"]')
    if exp_section:
        items = exp_section.select(".resume-block-item-gap")
        for item in items:
            period = (item.select_one(".bloko-column_s-2") or item.select_one(".bloko-column_s-3"))
            period_text = period.get_text(" ", strip=True) if period else ""

            company_el = item.select_one(".bloko-text_strong")
            company = company_el.get_text(" ", strip=True) if company_el else ""

            position_el = item.select_one('[data-qa="resume-block-experience-position"]')
            position = position_el.get_text(" ", strip=True) if position_el else ""

            desc_el = item.select_one('[data-qa="resume-block-experience-description"]')
            desc = desc_el.get_text("\n", strip=True) if desc_el else ""

            block = []
            if period_text:
                block.append(f"**{period_text}**")
            if company:
                block.append(f"*{company}*")
            if position:
                block.append(f"**{position}**")
            if desc:
                block.append(desc)

            if block:
                experiences.append("\n\n".join(block))

    skills = []
    skills_section = soup.select_one('[data-qa="skills-table"]')
    if skills_section:
        skills = [t.get_text(" ", strip=True) for t in skills_section.select('[data-qa="bloko-tag__text"]')]

    md = []
    md.append(f"# {name}")
    if gender_age:
        md.append(f"**{gender_age}**")
    md.append(f"**Местоположение:** {location}")
    md.append(f"**Должность:** {job_title}")
    md.append(f"**Статус:** {job_status}")

    md.append("## Опыт работы")
    md.append("\n\n---\n\n".join(experiences) if experiences else "Опыт работы не найден.")

    md.append("## Ключевые навыки")
    md.append(", ".join(skills) if skills else "Навыки не указаны.")

    return "\n\n".join(md).strip()
