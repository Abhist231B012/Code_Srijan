# ─────────────────────────────────────────────────────────────
# CELL 1: Alternative Scoring Engine
# Weighted scorecard — mimics how Fintechs score new users
# ─────────────────────────────────────────────────────────────
# Score weights — total possible = 600 points on top of base 300
SCORE_WEIGHTS = {
    "upi_behavior"      : 150,   # Digital payment activity
    "utility_payments"  : 100,   # Bill payment discipline
    "mobile_vintage"    : 80,    # Mobile number stability
    "income_stability"  : 100,   # Income level + type
    "kyc_completeness"  : 50,    # KYC docs submitted
    "rent_regularity"   : 60,    # Rent paid on time
    "demographic_risk"  : 60,    # Age, dependents, city tier
}
print("\n📊 Score Weight Distribution:")
for category, weight in SCORE_WEIGHTS.items():
    bar = "█" * (weight // 5)
    print(f"   {category:20s} : {bar} {weight} pts")
print(f"   {'TOTAL':20s} : {'█'*12} {sum(SCORE_WEIGHTS.values())} pts")
print(f"   Base score: 300 | Max possible: 900")


class AltScoringEngine:

    def score_upi_behavior(self, upi_transactions_per_month, avg_upi_amount_rs=0):
        """
        Score based on UPI/digital payment activity
        More transactions = more financially active = less risky
        Max: 150 points
        """
        score = 0
        # Transaction frequency
        if upi_transactions_per_month >= 60:
            score += 100
        elif upi_transactions_per_month >= 40:
            score += 80
        elif upi_transactions_per_month >= 20:
            score += 55
        elif upi_transactions_per_month >= 10:
            score += 35
        elif upi_transactions_per_month >= 5:
            score += 20
        else:
            score += 5    # Very low activity
        # Average transaction amount (financial capacity)
        if avg_upi_amount_rs >= 5000:
            score += 50
        elif avg_upi_amount_rs >= 2000:
            score += 35
        elif avg_upi_amount_rs >= 500:
            score += 20
        elif avg_upi_amount_rs > 0:
            score += 10
        return min(score, SCORE_WEIGHTS["upi_behavior"])

    def score_utility_payments(self, bills_paid_on_time, total_bills=12,
                                types_of_bills=1):
        """
        Score based on utility bill payment discipline
        Electric, water, gas, DTH, broadband etc.
        Max: 100 points
        """
        score = 0
        if total_bills == 0:
            return 30    # No record — neutral
        payment_rate = bills_paid_on_time / total_bills
        # Payment consistency
        if payment_rate >= 0.95:
            score += 70
        elif payment_rate >= 0.85:
            score += 55
        elif payment_rate >= 0.70:
            score += 40
        elif payment_rate >= 0.50:
            score += 25
        else:
            score += 5
        # Variety of bills paid (shows more financial responsibility)
        score += min(types_of_bills * 10, 30)
        return min(score, SCORE_WEIGHTS["utility_payments"])

    def score_mobile_vintage(self, mobile_years_active, same_number=1,
                              prepaid_or_postpaid="postpaid"):
        """
        Score based on mobile number stability
        Long-term same number = stable identity = lower risk
        Max: 80 points
        """
        score = 0
        # Vintage (years with same operator/number)
        if mobile_years_active >= 5:
            score += 50
        elif mobile_years_active >= 3:
            score += 40
        elif mobile_years_active >= 2:
            score += 30
        elif mobile_years_active >= 1:
            score += 20
        else:
            score += 5
        # Same number continuity
        score += same_number * 15
        # Postpaid = more committed = lower risk
        if prepaid_or_postpaid == "postpaid":
            score += 15
        else:
            score += 5
        return min(score, SCORE_WEIGHTS["mobile_vintage"])

    def score_income_stability(self, monthly_income_rs, employment_type,
                                employment_years, income_regularity="regular"):
        """
        Score based on income level and stability
        Max: 100 points
        """
        score = 0
        # Income level scoring (₹ per month)
        if monthly_income_rs >= 100000:
            score += 50
        elif monthly_income_rs >= 50000:
            score += 42
        elif monthly_income_rs >= 30000:
            score += 35
        elif monthly_income_rs >= 20000:
            score += 27
        elif monthly_income_rs >= 12000:
            score += 18
        elif monthly_income_rs >= 8000:
            score += 10
        else:
            score += 3
        # Employment type stability
        emp_score_map = {
            "Government_Employee"    : 30,
            "Private_Salaried"       : 25,
            "Corporate_Salaried"     : 25,
            "Self_Employed_Business" : 18,
            "Retired_Pensioner"      : 22,
            "Daily_Wage"             : 8,
            "Farmer"                 : 12,
            "Unemployed"             : 0,
            "Student"                : 5,
        }
        score += emp_score_map.get(employment_type, 10)
        # Employment tenure
        if employment_years >= 5:
            score += 20
        elif employment_years >= 3:
            score += 15
        elif employment_years >= 1:
            score += 8
        else:
            score += 2
        return min(score, SCORE_WEIGHTS["income_stability"])

    def score_kyc_completeness(self, has_aadhaar=0, has_pan=0,
                                has_bank_statement=0, has_income_proof=0,
                                has_property_doc=0):
        """
        Score based on KYC document availability
        More verified identity = less fraud risk
        Max: 50 points
        """
        score = 0
        score += has_aadhaar        * 15   # Most important — biometric verified
        score += has_pan            * 12   # Tax identity
        score += has_bank_statement * 10   # Financial proof
        score += has_income_proof   * 8    # Income proof
        score += has_property_doc   * 5    # Asset proof
        return min(score, SCORE_WEIGHTS["kyc_completeness"])

    def score_rent_regularity(self, rent_paid_on_time_months, total_months_rented=12,
                               owns_house=0):
        """
        Score based on rent payment discipline
        Regular rent payer → disciplined with financial obligations
        Max: 60 points
        """
        if owns_house == 1:
            return 50    # Owns house = better than renting
        if total_months_rented == 0:
            return 25    # No data — neutral
        rent_rate = rent_paid_on_time_months / total_months_rented
        if rent_rate >= 0.95:
            return 60
        elif rent_rate >= 0.85:
            return 48
        elif rent_rate >= 0.70:
            return 35
        elif rent_rate >= 0.50:
            return 20
        else:
            return 5

    def score_demographic(self, age_years, number_of_dependents=0,
                           city_tier=2, education_level="Higher_Secondary_12th"):
        """
        Score based on demographic risk factors
        Max: 60 points
        """
        score = 0
        # Age risk curve (too young or too old = higher risk)
        if 30 <= age_years <= 50:
            score += 25
        elif 25 <= age_years < 30 or 50 < age_years <= 58:
            score += 20
        elif 22 <= age_years < 25 or 58 < age_years <= 65:
            score += 12
        elif age_years < 22:
            score += 5
        else:
            score += 8
        # Dependents (more dependents = more financial pressure)
        if number_of_dependents == 0:
            score += 15
        elif number_of_dependents <= 2:
            score += 10
        elif number_of_dependents <= 4:
            score += 5
        else:
            score += 0
        # City tier (metro = more formal economy access)
        city_score = {1: 12, 2: 8, 3: 4}
        score += city_score.get(city_tier, 6)
        # Education
        edu_score = {
            "PhD_Professional_Degree"    : 8,
            "Graduate_Postgraduate"      : 7,
            "Higher_Secondary_12th"      : 5,
            "Dropout_College"            : 3,
            "Up_to_10th_Standard"        : 2,
        }
        score += edu_score.get(education_level, 4)
        return min(score, SCORE_WEIGHTS["demographic_risk"])