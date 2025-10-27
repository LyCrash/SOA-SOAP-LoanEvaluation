import sys, logging, json, random
from spyne import Application, rpc, ServiceBase, Unicode
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from spyne.util.wsgi_wrapper import run_twisted

logging.basicConfig(level=logging.INFO)


# ---------------------------------------------------------------------
# Institutional Policy Parameters
# ---------------------------------------------------------------------

POLICY = {
    "min_credit_score": 55,           # Minimum acceptable score
    "max_loan_to_value": 0.85,        # Max ratio (loan/property value)
    "max_debt_to_income": 0.4,        # Max ratio (debt/income)
    "base_interest_rate": 3.0,        # %
}


# ---------------------------------------------------------------------
# Decision Logic
# ---------------------------------------------------------------------

def analyze_risk(data):
    """Perform a basic financial and risk analysis."""
    credit_score = float(data.get("credit_score", 0))
    property_value = float(data.get("property_value", 0))
    loan_amount = float(data.get("loan_amount", 0))
    income = float(data.get("revenu_mensuel", 0))
    expenses = float(data.get("depenses_mensuelles", 0))
    employment_stable = data.get("emploi_stable", True)

    # Derived metrics
    monthly_savings = max(0, income - expenses)
    debt_to_income = loan_amount / (income * 12) if income > 0 else 1
    loan_to_value = loan_amount / property_value if property_value > 0 else 1

    # Risk score (simple heuristic)
    risk_score = (
        (credit_score / 100) * 0.5
        + (1 - loan_to_value) * 0.3
        + (1 - debt_to_income) * 0.15
        + (0.05 if employment_stable else 0)
    )
    risk_score = min(max(risk_score, 0), 1)

    default_prob = round((1 - risk_score) * 100, 2)

    return {
        "credit_score": credit_score,
        "loan_amount": loan_amount,
        "property_value": property_value,
        "loan_to_value": round(loan_to_value, 2),
        "debt_to_income": round(debt_to_income, 2),
        "monthly_savings": round(monthly_savings, 2),
        "employment_stable": employment_stable,
        "risk_score": round(risk_score * 100, 2),
        "default_probability": default_prob
    }


def apply_policies(risk_data):
    """Apply institutional rules and return detailed reasoning."""
    approved = True
    reasons = []
    recommendations = []

    # --- Credit score policy ---
    if risk_data["credit_score"] < POLICY["min_credit_score"]:
        approved = False
        reasons.append(
            f"Credit score ({risk_data['credit_score']}) is below the minimum threshold ({POLICY['min_credit_score']})."
        )
        recommendations.append(
            "Improve your credit score by paying bills on time, reducing outstanding debts, and avoiding new credit requests."
        )

    # --- Loan-to-value policy ---
    if risk_data["loan_to_value"] > POLICY["max_loan_to_value"]:
        approved = False
        reasons.append(
            f"Loan-to-Value ratio ({risk_data['loan_to_value']:.2f}) exceeds the acceptable limit ({POLICY['max_loan_to_value']})."
        )
        recommendations.append(
            "Increase your down payment or consider a lower loan amount to improve your loan-to-value ratio."
        )

    # --- Debt-to-income policy ---
    if risk_data["debt_to_income"] > POLICY["max_debt_to_income"]:
        approved = False
        reasons.append(
            f"Debt-to-Income ratio ({risk_data['debt_to_income']:.2f}) is higher than the recommended maximum ({POLICY['max_debt_to_income']})."
        )
        recommendations.append(
            "Try to increase your income or reduce your monthly expenses to improve your debt ratio."
        )

    # --- Global risk score ---
    if risk_data["risk_score"] < 40:
        approved = False
        reasons.append(
            f"Global risk score ({risk_data['risk_score']}) is too low, indicating a high probability of default."
        )
        recommendations.append(
            "Work on improving your financial stability and credit behavior before reapplying."
        )

    # --- Employment stability ---
    if not risk_data["employment_stable"]:
        approved = False
        reasons.append("Employment instability detected.")
        recommendations.append(
            "Consider applying once your employment situation has stabilized or provide additional financial guarantees."
        )

    # Interest rate calculation (depends on risk)
    base_rate = POLICY["base_interest_rate"]
    risk_adjustment = (100 - risk_data["risk_score"]) / 20  # higher risk → higher rate
    interest_rate = round(base_rate + risk_adjustment, 2)

    # If approved, give positive feedback
    if approved:
        reasons.append("Applicant meets all institutional requirements.")
        recommendations.append("Maintain your good financial habits to preserve your creditworthiness.")

    return approved, reasons, recommendations, interest_rate


# ---------------------------------------------------------------------
# Spyne SOAP Service
# ---------------------------------------------------------------------

class DecisionService(ServiceBase):
    @rpc(Unicode, _returns=Unicode)
    def make_decision(ctx, data):
        """Receives JSON data and returns loan approval decision."""
        try:
            parsed = json.loads(data)
        except Exception as e:
            logging.error(f"[Decision] Invalid JSON: {e}")
            return json.dumps({"status": "error", "message": str(e)})

        try:
            risk_data = analyze_risk(parsed)
            approved, reasons, recommendations, rate = apply_policies(risk_data)

            decision = {
                "approved": approved,
                "interest_rate": rate,
                "loan_amount": risk_data["loan_amount"],
                "risk_details": risk_data,
                "reasons": reasons,
                "recommendations": recommendations,
                "message": "✅ Approved" if approved else "❌ Rejected"
            }

            logging.info(f"[Decision] {decision['message']} | Rate: {rate}%")
            return json.dumps(decision, indent=2, ensure_ascii=False)

        except Exception as e:
            logging.error(f"[Decision] Error during processing: {e}")
            return json.dumps({"status": "error", "message": str(e)})


# ---------------------------------------------------------------------
# SOAP Application Setup
# ---------------------------------------------------------------------

app = Application(
    [DecisionService],
    tns='loan.services.decision',
    in_protocol=Soap11(validator='lxml'),
    out_protocol=Soap11()
)

if __name__ == '__main__':
    sys.exit(run_twisted([(WsgiApplication(app), b'DecisionService')], 8004))
