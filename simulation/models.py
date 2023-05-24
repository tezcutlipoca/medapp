from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from datetime import timedelta, date
import random

from simulation.data import fake_medication_names, first_names, last_names
from simulation.settings import Settings


@dataclass
class Treatment:
    medication_name: str = field(default_factory=lambda: random.choice(fake_medication_names))
    duration: timedelta = field(
        default_factory=lambda: timedelta(days=random.randint(*Settings.treatment_duration_bounds))
    )
    start_date: date = field(default_factory=lambda: date.today())
    reminder_interval_days: int = field(default_factory=lambda: random.randint(*Settings.reminder_interval_days_bounds))
    reminder_times_a_day: int = field(default_factory=lambda: random.randint(*Settings.reminder_times_a_day_bound))
    well_being_impact_range: tuple = field(
        default_factory=lambda: random.choice(tuple(Settings.well_being_impact_ranges.values()))
    )

    def __post_init__(self):
        self.reminder_dates = tuple(
            [
                self.start_date + timedelta(days=d)
                for d in range(self.duration.days)
                if not d % self.reminder_interval_days
            ]
        )

    def impact_well_being(self, user: User):
        new_well_being = user.well_being + random.choice(self.well_being_impact_range)
        user.well_being = max(1, min(new_well_being, 5))  # 1..5
        return user

    def repr(self):
        attrs = asdict(self)
        attrs.update(
            {
                'duration_days': attrs.pop('duration').days,
                'start_date': self.start_date.strftime('%Y-%m-%d'),
            }
        )

        return attrs


@dataclass
class User:
    first_name: str = field(default_factory=lambda: random.choice(first_names))
    last_name: str = field(default_factory=lambda: random.choice(last_names))
    age: int = field(default_factory=lambda: random.randint(*Settings.age_bounds))
    treatments: list[Treatment] = field(default_factory=list)
    well_being: int = field(default_factory=lambda: random.randint(2, 4))
    miss_medication_likelihood: float = field(
        default_factory=lambda: random.uniform(*Settings.miss_medication_likelihood_bounds)
    )

    def get_active_treatments_for_date(self, day: date):
        return [treatment for treatment in self.treatments if day in treatment.reminder_dates]

    def repr(self):
        attrs = asdict(self)
        attrs.update({'treatments': [t.repr() for t in self.treatments]})
        return attrs


@dataclass
class DailyTreatmentLog:
    medication_name: str
    due_intakes: int
    marked_intakes: int

    @classmethod
    def from_user_and_treatment(cls, user: User, treatment: Treatment):
        due_intakes = treatment.reminder_times_a_day
        marked_intakes = due_intakes - sum(
            [int(user.miss_medication_likelihood > random.random()) for _ in range(due_intakes)]
        )

        return cls(
            medication_name=treatment.medication_name,
            due_intakes=due_intakes,
            marked_intakes=marked_intakes,
        )

    def repr(self):
        return asdict(self)


@dataclass
class SimulationDayLog:
    well_being: int
    date: date
    daily_treatment_info: list[DailyTreatmentLog]

    def repr(self):
        attrs = asdict(self)
        attrs.update(
            {
                'date': self.date.strftime('%Y-%m-%d'),
                'daily_treatment_info': [dti.repr() for dti in self.daily_treatment_info],
            }
        )
        return attrs


@dataclass
class SimulationLog:
    user: User
    days: list[SimulationDayLog] = field(default_factory=list)

    def repr(self):
        return {'user': self.user.repr(), 'days': [day.repr() for day in self.days]}

    def save_results(self):
        with open(Settings.results_path, 'w') as _out:
            json.dump(self.repr(), _out, indent=2)
