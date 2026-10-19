# Metric Plan

**Time window:** 2023-10-01 to 2025-09-30. Customers whose first valid order is dated 2023-10-01 to 2025-09-30 (24 monthly groups). Each first order is found over all history, not just this window. Second orders are looked for up to 12 months later, so up to 2026-09-30, the last day of data. Every group has a full 12 months of follow-up.

**Rules applied to every metric:**

- Order date = orders.created_at as a UTC calendar date. No other date column is used. Do not use users.created_at, delivered_at or shipped_at.
- Remove orders dated after 2026-09-30 (five orders dated 2027-2028). They are never a first or second order. Report how many were removed.
- One row per order_id. If an order_id appears more than once and the copies are identical, keep one. If they conflict, keep the earliest created_at row. If it can't be resolved, drop that order_id. Count distinct order_id only.
- Remove orders with no user_id. They can't be tied to a customer or channel. Report how many were removed.
- Remove orders with num_of_item > 40. They look like entry errors. Cross-check against the row count in order_items and report how many were removed.
- Valid order = after the steps above, orders.status is not Cancelled and not Returned (so Complete, Shipped and Processing count). Only the order-level status is used. Partly returned orders (an order with some returned items but not marked Returned as a whole) are valid and count as a first or repeat order. Item-level status in order_items is not used to exclude orders. Status is the current status, not the status on the order date.
- First valid order = the earliest valid order per customer over ALL history. Do this before applying the 2023-10-01 to 2025-09-30 window. If a customer's earliest order is not valid, their first valid order is the next valid one.
- Customer's channel = users.traffic_source, joined with orders.user_id = users.id. Label it 'sign-up channel'. One channel per customer. Orders whose user has no matching users row, or a blank channel, go in a separate 'Unknown channel' group. Show it apart from the named channels.
- Second order (repeat) = a different valid order_id, dated on a later calendar date than the first valid order date and no later than the first valid order date + 12 calendar months. Same-day orders do not count as repeats. If the first order is on 29 Feb, the 12-month end date is 28 Feb the next year.
- Never show first_name, last_name or email. Do not use orders.gender, users.gender or product fields.

## 1. New customers (first-time buyers)

*How many customers did each channel bring whose first valid order fell in each month? This is the base for the repeat rate.*

- **Formula:** Count of distinct customers (orders.user_id) whose first valid order date falls in the month, grouped by sign-up channel. Customers with no valid order are not counted.
- **Grain:** One row per sign-up channel per first-order month (at most 5 named channels + Unknown x 24 months). Plus one pooled row per channel for all 24 months.
- **Breakdowns:** Sign-up channel (users.traffic_source), Month of first valid order
- **Filters:** Channel; First-order month
- **Time logic:** A customer is placed in the month of their first valid order date (orders.created_at, UTC), found over all history. Keep first valid order dates from 2023-10-01 to 2025-09-30. The pooled row sums the 24 months.
- **Cleaning:** Apply all shared rules.; Customers are counted once, in one month only.
- **Excluded example:** A customer whose first order was cancelled in Nov 2023 and whose next valid order was in Feb 2024 is counted in Feb 2024, not Nov 2023. A customer whose only order was marked Returned is not counted at all. A customer whose first order was only partly returned (order not marked Returned) is counted from that order.

## 2. Repeat customers

*How many of those new customers placed a second valid order within 12 months of their first?*

- **Formula:** Count of distinct customers from the New customers group who have at least one other valid order, on a later calendar date than their first valid order date and no later than first valid order date + 12 calendar months. Each customer counts once.
- **Grain:** One row per sign-up channel per first-order month. Plus one pooled row per channel for all 24 months.
- **Breakdowns:** Sign-up channel (users.traffic_source), Month of first valid order
- **Filters:** Channel; First-order month
- **Time logic:** The customer is placed by the month of the first valid order, not the month of the second order. The second order date (orders.created_at, UTC) must be after the first order date and no later than the first order date + 12 months. This can reach 2026-09-30.
- **Cleaning:** Apply all shared rules.; The second order must have a different order_id from the first. Duplicate rows of one order never make a repeat.
- **Excluded example:** A customer whose first valid order was 2024-03-10 and whose second valid order was 2025-04-02 is not a repeat. It is more than 12 months later. A second order placed on the same day as the first is also not a repeat.

## 3. 12-month repeat purchase rate

*Which channels bring customers who buy a second time within 12 months of their first order?*

- **Formula:** Repeat customers divided by New customers, as a percentage. For the 24-month total per channel, add up repeat customers and new customers across all months first, then divide. Do not average the monthly rates.
- **Grain:** One row per sign-up channel per first-order month (with New customers and Repeat customers shown beside the rate). Plus one pooled 24-month row per channel.
- **Breakdowns:** Sign-up channel (users.traffic_source), Month of first valid order
- **Filters:** Channel; First-order month
- **Time logic:** Same as the two metrics above. Customers are placed by first valid order date (2023-10-01 to 2025-09-30). Repeat orders are counted up to first order date + 12 months.
- **Cleaning:** Apply all shared rules.; If a channel and month has no new customers, show the rate as blank ('no new customers'), not 0%.; Show the New customers count beside every rate. Mark rates based on fewer than 30 new customers as 'small base'. Use the pooled 24-month rate as the main comparison.
- **Excluded example:** A customer who first bought in Oct 2025 is left out. They have less than 12 months of follow-up if you count to the data end, and the brief limits the window to Sep 2025. A customer with a first order in Jan 2024 and a second order that is now marked Returned is counted as not repeat. A second order that was only partly returned counts as a repeat.

## Confirmed with the stakeholder

- If only part of an order was returned, should the whole order be left out? Left out means it can't count as a first order or a second order. Answer: No, only leave out orders that were fully returned or cancelled. If someone kept part of an order, they still made a real purchase, so it should count as a first or repeat order.
- If a customer places two separate orders on the same day, should the second one count as a repeat purchase? Answer: No, a repeat should be on a later day. Two orders on the same day are really one shopping trip, not a customer coming back.

## Decisions assumed (please confirm)

- Shipped and Processing orders count as valid, as the brief says. Some could later be cancelled or returned.
- Orders with more than 40 items are treated as errors and excluded. Only five orders are affected.
- Status is the current status. An order that was fine at the time but is Returned now is excluded. This can slightly lower recent repeat rates.
- The channel is the sign-up channel in users.traffic_source. It is the acquiring channel, but it does not track later marketing touches.
- Orders whose customer has no users row, or no channel, are grouped as 'Unknown channel'. They are shown separately and left out of the channel comparison.
- The 24-month channel rate is pooled (sum of repeats divided by sum of new customers). It is not an average of monthly rates.
- Months or channels with no new customers show a blank rate, not 0%. Rates on fewer than 30 new customers are marked 'small base'.
- Duplicate order rows are collapsed to one row per order_id. Conflicting copies keep the earliest. Unresolvable ones are dropped.
- Orders with a missing customer or a date after 2026-09-30 are excluded and their counts are reported.
- '12 months' is 12 calendar months on UTC dates, counted from the first valid order date.
- Orders with delivery or shipping dates out of sequence are not excluded. Those dates are not used.
