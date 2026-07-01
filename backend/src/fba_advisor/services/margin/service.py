"""Margin business service with deterministic, testable calculations."""

from fba_advisor.domain.models import MarginEstimate, MarginInput


class MarginService:
    """Calculate FBA-style margin estimates from explicit inputs."""

    def estimate(self, inputs: MarginInput) -> MarginEstimate:
        """Calculate revenue, costs, profit, and margin rate."""
        if inputs.selling_price <= 0:
            msg = "selling_price must be greater than zero."
            raise ValueError(msg)
        if inputs.product_cost < 0 or inputs.fulfillment_fee < 0 or inputs.shipping_cost < 0:
            msg = "cost values must be zero or greater."
            raise ValueError(msg)
        if not 0 <= inputs.referral_fee_rate <= 1:
            msg = "referral_fee_rate must be between 0 and 1."
            raise ValueError(msg)
        referral_fee = inputs.selling_price * inputs.referral_fee_rate
        total_cost = (
            inputs.product_cost
            + inputs.fulfillment_fee
            + referral_fee
            + inputs.shipping_cost
            + inputs.fixed_costs
        )
        profit = inputs.selling_price - total_cost
        return MarginEstimate(
            revenue=inputs.selling_price,
            total_cost=total_cost,
            profit=profit,
            margin_rate=profit / inputs.selling_price,
            referral_fee=referral_fee,
        )
