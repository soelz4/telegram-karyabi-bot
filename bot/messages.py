START_TEXT = (
    "Send a job title or keyword and I will search Jobinja, Quera, Karboom, "
    "and Jobvision."
)
HELP_TEXT = (
    "Examples:\n"
    "Software Engineer\n"
    "Python Developer\n"
    "مدیر محصول\n\n"
    "Each result has a button that opens the original job page."
)
EMPTY_QUERY_TEXT = "Please send a job title or keyword."
NO_RESULTS_TEXT = "No jobs found for this search."


def format_results(query: str, jobs: list[dict]) -> tuple[str, dict | None]:
    if not jobs:
        return f'{NO_RESULTS_TEXT}\n\nSearch: "{query}"', None

    lines = [f'Results for "{query}":']
    keyboard = []

    for index, job in enumerate(jobs, start=1):
        lines.append(format_job_line(index, job))
        keyboard.append(
            [
                {
                    "text": truncate(job["button_text"], 64),
                    "url": job["url"],
                }
            ]
        )

    return "\n".join(lines), {"inline_keyboard": keyboard}


def format_job_line(index: int, job: dict) -> str:
    subtitle = f" ({job['subtitle']})" if job.get("subtitle") else ""
    return f"{index}. {job['title']}{subtitle}"


def truncate(value: str, max_length: int) -> str:
    if len(value) <= max_length:
        return value
    if max_length <= 3:
        return value[:max_length]
    return value[: max_length - 3].rstrip() + "..."
