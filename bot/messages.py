CALLBACK_CLOSE = "close"
CALLBACK_BACK = "back"

START_TEXT = "Welcome. Use /search to search jobs."
SEARCH_PROMPT_TEXT = "Type a job title or keyword."
HELP_TEXT = (
    "Use /search, then type something like:\n"
    "Software Engineer\n"
    "Python Developer\n"
    "مدیر محصول"
)
EMPTY_QUERY_TEXT = "Please send a job title or keyword."
NO_RESULTS_TEXT = "No jobs found for this search."
JOB_NOT_FOUND_TEXT = "This job is no longer available."


def remove_keyboard() -> dict:
    return {"remove_keyboard": True}


def search_prompt() -> tuple[str, dict]:
    return SEARCH_PROMPT_TEXT, inline_keyboard([[button("Close", CALLBACK_CLOSE)]])


def format_results(query: str, jobs: list[dict]) -> tuple[str, dict]:
    if not jobs:
        return (
            f'{NO_RESULTS_TEXT}\n\nSearch: "{query}"',
            inline_keyboard([[button("Close", CALLBACK_CLOSE)]]),
        )

    lines = [f'Results for "{query}":', "Choose a job:"]
    keyboard = []

    for index, job in enumerate(jobs, start=1):
        lines.append(format_job_line(index, job))
        keyboard.append(
            [
                button(
                    truncate(f"{index}. {job['button_text']}", 64),
                    job_callback(job),
                )
            ]
        )

    keyboard.append([button("Close", CALLBACK_CLOSE)])
    return "\n".join(lines), inline_keyboard(keyboard)


def format_job_detail(job: dict) -> tuple[str, dict]:
    lines = [
        job["title"],
        "",
        *format_detail_lines(job),
    ]
    keyboard = [
        [{"text": "Open job", "url": job["url"]}],
        [button("Back", CALLBACK_BACK), button("Close", CALLBACK_CLOSE)],
    ]
    return "\n".join(line for line in lines if line is not None), inline_keyboard(keyboard)


def format_detail_lines(job: dict) -> list[str]:
    lines = []
    for label, key in (
        ("Company", "company"),
        ("Location", "location"),
        ("Published", "published"),
        ("Salary", "salary"),
        ("Experience", "experience"),
        ("Contract", "contract"),
        ("Work type", "work_type"),
        ("Industry", "industry"),
        ("Source", "source_label"),
    ):
        value = job.get(key)
        if value:
            lines.append(f"{label}: {value}")

    description = first_paragraph(job.get("job_description", ""))
    if description:
        lines.extend(["", description])

    return lines


def first_paragraph(value: str, max_length: int = 700) -> str:
    value = "\n".join(line.strip() for line in (value or "").splitlines() if line.strip())
    return truncate(value, max_length) if value else ""


def format_job_line(index: int, job: dict) -> str:
    subtitle = f" ({job['subtitle']})" if job.get("subtitle") else ""
    return f"{index}. {job['title']}{subtitle}"


def job_callback(job: dict) -> str:
    return f"job:{job['source']}:{job['id']}"


def parse_job_callback(data: str) -> tuple[str, str] | None:
    parts = data.split(":", 2)
    if len(parts) != 3 or parts[0] != "job":
        return None
    return parts[1], parts[2]


def inline_keyboard(rows: list[list[dict]]) -> dict:
    return {"inline_keyboard": rows}


def button(text: str, callback_data: str) -> dict:
    return {"text": text, "callback_data": callback_data}


def truncate(value: str, max_length: int) -> str:
    if len(value) <= max_length:
        return value
    if max_length <= 3:
        return value[:max_length]
    return value[: max_length - 3].rstrip() + "..."
