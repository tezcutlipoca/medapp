import json
from datetime import timedelta
import random
from pprint import pprint

from simulation.models import User, Treatment, SimulationLog, SimulationDayLog, DailyTreatmentLog
from simulation.settings import Settings


class Simulation:
    def __init__(self):
        random.seed(Settings.random_seed)

        treatments = []
        for _ in range(Settings.n_treatments):
            if not treatments:
                treatments.append(Treatment(start_date=Settings.start_date))
            else:
                prev_treatment = treatments[-1]
                treatments.append(Treatment(start_date=prev_treatment.start_date + prev_treatment.duration))

        self.user = User(treatments=treatments)
        self.log = SimulationLog(self.user)

    def run(self):
        simulation_days = (Settings.start_date + timedelta(days=d) for d in range(Settings.duration.days))
        for simulation_day in simulation_days:
            daily_treatment_info = []

            for treatment in self.user.get_active_treatments_for_date(simulation_day):
                treatment_info = DailyTreatmentLog.from_user_and_treatment(self.user, treatment)
                if treatment_info.marked_intakes > 0:
                    treatment.impact_well_being(self.user)
                daily_treatment_info.append(treatment_info)

            self.log.days.append(
                SimulationDayLog(
                    well_being=self.user.well_being,
                    date=simulation_day,
                    daily_treatment_info=daily_treatment_info,
                )
            )


if __name__ == '__main__':
    simulation = Simulation()
    simulation.run()
    simulation.log.save_results()
