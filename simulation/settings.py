from datetime import timedelta, date
from pathlib import Path


class Settings:
    # general
    random_seed = 100  # change to get different results, set to None to get random results
    start_date = date.today() - timedelta(days=30)
    duration = timedelta(30)
    results_path = Path('./simulation_result.json')

    # treatment
    treatment_duration_bounds = (7, 10)
    reminder_interval_days_bounds = (1, 3)  # every how many days
    reminder_times_a_day_bound = (1, 3)  # how many times a day
    well_being_impact_ranges = {
        'positive': tuple(range(0, 3)),
        'normal': tuple(range(-1, 2)),
        # 'negative': tuple(range(-2, 1)),
        # 'high_jitter': tuple(range(-3, 4)),
    }

    # user
    n_treatments = 3
    miss_medication_likelihood_bounds = (0.1, 0.5)
    age_bounds = (45, 90)
